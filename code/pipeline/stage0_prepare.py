#!/usr/bin/env python3
"""
Stage 0 — Deterministic preparation (PROTOCOL.md §8). Pure Python, no LLM.

Iterates the Level-3 universe (Included + Maybe) from data/articles.csv and, for
each paper, builds output/stage0/{key}.json per §8.10. Implements:

  §8.1 bibliographic fields + notes parsing (rayyan decision, source string)
  §8.2 excluded-duplicates check (fires FIRST — reviewer confirmation, 2026-06-18)
  §8.3 PDF presence
  §8.4 text-extraction fallback chain (ocr_recovered -> pymupdf -> pdfplumber
       -> tesseract -> quarantine-proposed)
  §8.5 text-quality gates
  §8.6 retraction scan
  §8.7 composite garbled detection
  §8.8 deterministic eligibility gates (doc type / year / language)
  §8.9 title/DOI vs metadata cross-check (wrong-PDF detection)
  §8.10 bundle output

Usage:
  python3 output/stage0_prepare.py --sample 3      # smoke test on 3 papers (§18.5)
  python3 output/stage0_prepare.py --keys k1,k2    # specific keys
  python3 output/stage0_prepare.py                 # full Level-3 universe

Reviewer-confirmed deviations from a literal §8 reading (2026-06-18):
  - Dedup secondaries were physically moved to pdfs_quarantine/rayyan_dedup/, so
    they also get pdf.available=false; the PRISMA "3 removed" count comes from
    excluded_as_duplicate, which §8.2 sets first (confirmation B).
  - source_string: the Rayyan export carries NO STRING-A/STRING-B markers, so it
    is null for every paper. Recorded per-paper as flags.source_string_missing
    (systemic; reported once in the summary, NOT routed to needs_review per-paper).
  - Truncated/preview (total<5000 but mean>=100) does NOT block Stage 1 (§8.5 +
    §8.10 note). Only image_only (mean<100) blocks on the text gate.
  - Quarantine (§8.4.5) is RECORDED (output/stage0_quarantine_proposed.json), not
    auto-applied: data/ is declared read-only (§0.5) and moving files is
    destructive. Does not fire in the current corpus (preflight pre-resolved it).
"""
import argparse
import csv
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

import fitz                       # pymupdf
import pdfplumber                 # noqa: F401  (used in fallback)
from rapidfuzz import fuzz

# ----------------------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)                       # level3_extraction/
DATA = os.path.join(BASE, "data")
OUT = HERE                                         # output/
PDFS = os.path.join(DATA, "pdfs")
OCR_DIR = os.path.join(DATA, "ocr_recovered")
QUAR_UNREADABLE = os.path.join(DATA, "pdfs_quarantine", "unreadable")
STAGE0_DIR = os.path.join(OUT, "stage0")

# ----------------------------------------------------------------------------- constants (§8.7, §8.6, §5.1)
COMMON_WORDS = {
    "the", "of", "and", "in", "to", "is", "for", "a", "that", "with", "on", "this",
    "by", "as", "are", "be", "an", "or", "we", "was", "were", "have", "has", "which",
    "from", "at", "it", "not", "but", "energy", "system", "process", "model", "data",
    "based", "study", "results", "analysis", "performance", "method", "industrial",
}
_COMMON_RE = re.compile(r"\b(?:%s)\b" % "|".join(sorted(map(re.escape, COMMON_WORDS))))
# 'withdrawn' removed 2026-06-18 (reviewer decision): in this corpus it matches
# "EN 16001 was withdrawn" (the standard superseded by ISO 50001), not article
# retractions. Genuine retractions carry explicit RETRACTED wording (COPE). See §8.6.
RETRACTION_MARKERS = ("retracted", "retraction notice",
                      "this article has been retracted")
ALLOWED_DOC_TYPES = {"journal article", "conference proceedings",
                     "dissertation", "grey literature"}
REFERENCE_ORG_HINTS = ("iso", "international organization for standardization",
                       "international energy agency", "iea", "doe", "department of energy",
                       "lbnl", "lawrence berkeley", "concawe", "nrcan", "natural resources canada",
                       "iogp", "ipieca", "solomon")
GARBLE_SAMPLE_LEN = 5000
# §8.7b: per-page control-char fraction. A broken embedded-font ToUnicode CMap
# remaps glyphs into C0/C1 control codepoints; the composite detect_garbled
# heuristic misses it whenever a clean cover page or interleaved clean runs keep
# common_word_matches >= 8 (which vetoes both garbled_bytes and garbled_glyphs).
# HARD => treat as garbled and advance the §8.4 fallback chain (OCR recovery).
# SOFT => localized damage (a single garbled table/equation) — recorded for
# reviewer inspection, does NOT block Stage 1.
PAGE_CONTROL_HARD = 0.15
PAGE_CONTROL_SOFT = 0.05


# ============================================================ PURE DECISION FUNCTIONS
def normalise_text(s: str) -> str:
    """§12.2: dehyphenate end-of-line breaks, collapse whitespace, lowercase."""
    if not s:
        return ""
    s = re.sub(r"-\s*\n\s*", "", s)          # reconnect end-of-line hyphenated words
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def parse_notes(notes: str) -> dict:
    """§8.1: extract Rayyan decision, source string (STRING-A/B), snowball flag."""
    notes = notes or ""
    m = re.search(r'RAYYAN-INCLUSION:\s*\{[^}]*"Bernardo"\s*=>\s*"(\w+)"', notes)
    decision = m.group(1) if m else None
    has_a = bool(re.search(r"STRING[-_ ]?A", notes, re.I))
    has_b = bool(re.search(r"STRING[-_ ]?B", notes, re.I))
    if has_a and has_b:
        source_string = "both"
    elif has_a:
        source_string = "A"
    elif has_b:
        source_string = "B"
    else:
        source_string = None
    via_snowballing = bool(re.search(r"snowball", notes, re.I))
    return {"rayyan_decision": decision, "source_string": source_string,
            "via_snowballing": via_snowballing}


def compute_text_quality(pages: list) -> dict:
    """§8.5: total chars, mean chars/page, strict has_extractable_text."""
    n = len(pages)
    total = sum(len(p.get("text", "")) for p in pages)
    mean = (total / n) if n else 0
    return {"total_chars": total,
            "mean_chars_per_page": round(mean, 1) if mean % 1 else int(mean),
            "has_extractable_text": (mean >= 100 and total >= 5000)}


def detect_garbled(text: str) -> dict:
    """§8.7: composite garbled heuristic over the first 5000 chars."""
    sample = (text or "")[:GARBLE_SAMPLE_LEN]
    n = len(sample)
    ascii_letters = sum(1 for c in sample if ("a" <= c <= "z") or ("A" <= c <= "Z"))
    ascii_letter_fraction = (ascii_letters / n) if n else 0.0
    common_word_matches = len(_COMMON_RE.findall(sample.lower()))
    garbled_bytes = (ascii_letter_fraction < 0.45 and common_word_matches < 8)
    garbled_glyphs = (ascii_letter_fraction >= 0.45 and common_word_matches < 8)
    return {"ascii_letter_fraction": round(ascii_letter_fraction, 4),
            "common_word_matches": common_word_matches,
            "garbled_bytes": garbled_bytes,
            "garbled_glyphs": garbled_glyphs}


def control_char_fraction(text: str) -> float:
    """§8.7b: fraction of C0 (excluding tab/LF/CR/FF/VT) + DEL + C1 control
    characters. A broken embedded-font ToUnicode CMap remaps glyphs into these
    ranges; legitimate text — including non-Latin scripts (CJK), mathematics,
    and typographic ligatures/quotes — carries effectively none."""
    if not text:
        return 0.0
    ctrl = 0
    for ch in text:
        o = ord(ch)
        if o in (0x09, 0x0A, 0x0D, 0x0C, 0x0B):   # tab, LF, CR, FF, VT — legitimate
            continue
        if o < 0x20 or o == 0x7F or 0x80 <= o <= 0x9F:
            ctrl += 1
    return ctrl / len(text)


_CID_RE = re.compile(r"\(cid:\d+\)")


def cid_token_fraction(text: str) -> float:
    """§8.7b: fraction of characters consumed by pdfminer/pdfplumber '(cid:N)'
    placeholder tokens. Emitted for the SAME broken-font failure (no usable
    ToUnicode CMap) that PyMuPDF renders as control codes — but as literal ASCII,
    so control_char_fraction would score it clean. pdfplumber precedes tesseract
    in the §8.4 chain, so this must be caught or the (cid:N) garbage is accepted
    and OCR never runs."""
    if not text:
        return 0.0
    return sum(len(m.group()) for m in _CID_RE.finditer(text)) / len(text)


def glyph_noise_fraction(text: str) -> float:
    """Unresolved-glyph fraction: max of the two broken-font representations
    (C0/C1 control codes and (cid:N) tokens)."""
    return max(control_char_fraction(text), cid_token_fraction(text))


def assess_glyph_corruption(pages: list) -> dict:
    """§8.7b: broken-font glyph corruption measured over the MAX single page.

    Whole-document sampling (detect_garbled's first 5000 chars) misses localized
    corruption — a single garbled table/equation page in an otherwise clean
    document, or a clean cover page masking a garbled body. The per-page maximum
    catches both. HARD (>= PAGE_CONTROL_HARD) marks broken-font corruption that
    must be re-extracted; SOFT ([PAGE_CONTROL_SOFT, PAGE_CONTROL_HARD)) records
    localized damage for reviewer inspection without blocking Stage 1."""
    mx = max((glyph_noise_fraction(p.get("text", "")) for p in pages), default=0.0)
    return {"max_page_control_fraction": round(mx, 4),
            "garbled_control_glyphs": mx >= PAGE_CONTROL_HARD,
            "partial_glyph_corruption": PAGE_CONTROL_SOFT <= mx < PAGE_CONTROL_HARD}


def is_garbled(g: dict) -> bool:
    return bool(g["garbled_bytes"] or g["garbled_glyphs"]
                or g.get("garbled_control_glyphs", False))


def scan_retraction(pages: list) -> bool:
    """§8.6: scan first 2 + last 2 pages for retraction markers (case-insensitive)."""
    if not pages:
        return False
    idxs = sorted(set([0, 1, len(pages) - 2, len(pages) - 1]) & set(range(len(pages))))
    blob = " ".join(pages[i].get("text", "") for i in idxs).lower()
    return any(m in blob for m in RETRACTION_MARKERS)


def title_doi_match(expected_title: str, expected_doi: str,
                    first_two_pages_text: str, full_text: str, image_only: bool) -> dict:
    """§8.9: fuzzy title match + DOI grep -> wrong_pdf_likely decision."""
    score = fuzz.partial_ratio(normalise_text(expected_title),
                               normalise_text(first_two_pages_text))
    score = round(score, 1)
    doi_found = bool(expected_doi) and (normalise_text(expected_doi) in normalise_text(full_text))
    wrong_pdf_likely = (score < 70) and (not doi_found) and (not image_only)
    return {"title_match_score": score, "doi_found_in_text": doi_found,
            "wrong_pdf_likely": wrong_pdf_likely}


def infer_document_type(row: dict) -> str:
    """§5.1/§8.1: infer document type (no document_type column in the CSV)."""
    notes = (row.get("notes") or "").lower()
    journal = (row.get("journal") or "").strip()
    publisher = (row.get("publisher") or "").lower()
    title = (row.get("title") or "").lower()
    if "conference name:" in notes or "conference date:" in notes:
        return "conference proceedings"
    if re.search(r"\b(dissertation|doctoral thesis|phd thesis|ph\.d\. thesis)\b", title):
        return "dissertation"
    if not journal and any(h in publisher for h in REFERENCE_ORG_HINTS):
        return "grey literature"
    if journal:
        return "journal article"
    return "other"


def doc_type_eligible(doc_type: str) -> bool:
    return doc_type in ALLOWED_DOC_TYPES


def year_eligible(year, via_snowballing: bool) -> bool:
    if via_snowballing:
        return True
    try:
        return int(year) >= 1996
    except (TypeError, ValueError):
        return False


def language_eligible(language: str, override: bool) -> bool:
    if override:
        return True
    return (language or "").strip().lower() == "english"


def select_form_pilot(included_keys, maybe_keys, seed=42, n_inc=3, n_maybe=2):
    """§13.1: deterministic stratified sample (n_inc Included + n_maybe Maybe).

    Keys are sorted within each stratum before sampling so the result depends only
    on the pool membership and the seed, not on iteration order (reproducibility, §14).
    """
    random.seed(seed)
    inc = sorted(included_keys)
    may = sorted(maybe_keys)
    picks = sorted(random.sample(inc, n_inc)) + sorted(random.sample(may, n_maybe))
    return picks


# ============================================================ I/O & ORCHESTRATION
def load_csv():
    csv.field_size_limit(10_000_000)
    with open(os.path.join(DATA, "articles.csv"), newline="", encoding="utf-8",
              errors="replace") as f:
        return {r["key"]: r for r in csv.DictReader(f)}


def load_json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pymupdf_pages(path):
    doc = fitz.open(path)
    try:
        return [{"page": i + 1, "text": p.get_text()} for i, p in enumerate(doc)]
    finally:
        doc.close()


def _pdfplumber_pages(path):
    with pdfplumber.open(path) as pdf:
        return [{"page": i + 1, "text": p.extract_text() or ""} for i, p in enumerate(pdf.pages)]


def _tesseract_pages(path):
    """§8.4.4: render each page at 250 dpi to PNG in a working-dir tmp, OCR with -l eng."""
    out = []
    doc = fitz.open(path)
    try:
        with tempfile.TemporaryDirectory(dir=OUT, prefix=".tmp_ocr_") as tmp:
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=250)
                png = os.path.join(tmp, f"p{i + 1}.png")
                pix.save(png)
                txt = subprocess.run(["tesseract", png, "-", "-l", "eng"],
                                     capture_output=True, text=True).stdout
                out.append({"page": i + 1, "text": txt})
    finally:
        doc.close()
    return out


def extract_text(key, pdf_path):
    """§8.4 fallback chain. Returns (pages, backend, garble_trace, quarantined)."""
    trace = []
    # 1. OCR-recovered preflight shortcut (no page boundaries -> single page 1)
    ocr_path = os.path.join(OCR_DIR, f"{key}.txt")
    if os.path.exists(ocr_path):
        with open(ocr_path, encoding="utf-8", errors="replace") as f:
            return ([{"page": 1, "text": f.read()}], "ocr_recovered_preflight", trace, False)
    # 2-4. pymupdf -> pdfplumber -> tesseract, advancing on garbled (§8.7)
    pages = []  # stays [] if every backend RAISES (vs. merely garbles) — the
    #             quarantine-proposed return below must not UnboundLocalError
    for backend, fn in (("pymupdf", _pymupdf_pages),
                        ("pdfplumber", _pdfplumber_pages),
                        ("tesseract_ocr", _tesseract_pages)):
        try:
            pages = fn(pdf_path)
        except Exception as e:                       # backend failed -> next backend
            trace.append({"backend": backend, "error": f"{type(e).__name__}: {e}"})
            continue
        sample = "".join(p["text"] for p in pages)[:GARBLE_SAMPLE_LEN]
        g = detect_garbled(sample)
        gc = assess_glyph_corruption(pages)          # §8.7b per-page control-char scan
        g["max_page_control_fraction"] = gc["max_page_control_fraction"]
        g["garbled_control_glyphs"] = gc["garbled_control_glyphs"]  # HARD only advances
        trace.append({"backend": backend, **g})
        if not is_garbled(g):
            return (pages, backend, trace, False)
    # 5. all backends exhausted -> quarantine PROPOSED (not auto-applied);
    #    pages holds the last garbled extraction, or [] if all backends raised
    return (pages, None, trace, True)


def build_bundle(key, row, excluded_map, redownload_keys):
    notes = parse_notes(row.get("notes", ""))
    doc_type = infer_document_type(row)
    year_raw = (row.get("year") or "").strip()
    try:
        year_val = int(year_raw)
    except ValueError:
        year_val = None
    override = str(row.get("language_override", "")).strip().lower() in ("1", "true", "yes")

    bundle = {
        "key": key,
        "stage0_schema": "PROTOCOL.md §8.10",
        "metadata": {
            "paper_id": key,
            "authors": row.get("authors", ""),
            "year": year_val,
            "title": row.get("title", ""),
            "source": row.get("journal", ""),
            "document_type": doc_type,
            "source_string": notes["source_string"],   # null: no STRING-A/B markers exist
            "doi": row.get("doi", ""),
            "language": row.get("language", ""),
            "rayyan_decision": notes["rayyan_decision"],
        },
        "pdf": {"available": False, "path": None, "extraction_backend": None},
        "deterministic_gates": {},
        "flags": {
            "image_only_pdf": False, "retracted": False,
            "via_snowballing": notes["via_snowballing"],
            "excluded_as_duplicate": False,
            "garbled_bytes": False, "garbled_glyphs": False,
            "garbled_control_glyphs": False, "partial_glyph_corruption": False,
            "wrong_pdf_likely": False, "truncated_or_preview": False,
            "source_string_missing": (notes["source_string"] is None
                                      and not notes["via_snowballing"]),
            "quarantine_proposed": False,
        },
    }

    # §8.2 excluded-duplicates check — FIRST (reviewer confirmation B)
    if key in excluded_map:
        bundle["flags"]["excluded_as_duplicate"] = True
        bundle["excluded_as_duplicate"] = True
        bundle["primary_key"] = excluded_map[key]
        bundle["pdf"]["unavailable_reason"] = "rayyan_dedup_secondary_moved_to_quarantine"
        bundle["deterministic_gates"] = {"passes_all_deterministic_gates": False,
                                         "skipped_reason": "excluded_as_duplicate"}
        bundle["proceeds_to_stage1"] = False
        return bundle

    # §8.3 PDF presence
    pdf_path = os.path.join(PDFS, f"{key}.pdf")
    if not os.path.exists(pdf_path):
        bundle["pdf"]["available"] = False
        bundle["pdf"]["unavailable_reason"] = (
            "wrong_content_quarantined_redownload_queued" if key in redownload_keys
            else "not_yet_downloaded")
        bundle["deterministic_gates"] = {"passes_all_deterministic_gates": False,
                                         "skipped_reason": "pdf_not_available"}
        bundle["proceeds_to_stage1"] = False
        return bundle

    # §8.4 text extraction
    pages, backend, trace, quarantined = extract_text(key, pdf_path)
    bundle["pdf"].update({"available": True,
                          "path": os.path.relpath(pdf_path, BASE),
                          "extraction_backend": backend,
                          "n_pages": len(pages),
                          "extraction_trace": trace,
                          "md5": md5_of(pdf_path),
                          "pages": pages})  # §8.10: required for Stage 1/2/3 evidence
                                            # grounding — v2.2 fix (was missing in v2.1)
    if backend == "ocr_recovered_preflight":
        bundle["pdf"]["locator_limitation"] = "no_page_boundaries_treat_as_page_1"

    # §8.5 text quality
    q = compute_text_quality(pages)
    bundle["pdf"]["text_quality"] = q
    image_only = q["mean_chars_per_page"] < 100
    truncated = q["total_chars"] < 5000
    bundle["flags"]["image_only_pdf"] = image_only
    bundle["flags"]["truncated_or_preview"] = truncated

    # §8.7 garbled (final accepted text) + §8.7b per-page glyph corruption
    final_g = detect_garbled("".join(p["text"] for p in pages))
    glyph = assess_glyph_corruption(pages)
    bundle["flags"]["garbled_bytes"] = final_g["garbled_bytes"]
    bundle["flags"]["garbled_glyphs"] = final_g["garbled_glyphs"]
    bundle["flags"]["garbled_control_glyphs"] = glyph["garbled_control_glyphs"]
    bundle["flags"]["partial_glyph_corruption"] = glyph["partial_glyph_corruption"]
    bundle["pdf"]["text_quality"].update(
        {"ascii_letter_fraction": final_g["ascii_letter_fraction"],
         "common_word_matches": final_g["common_word_matches"],
         "max_page_control_fraction": glyph["max_page_control_fraction"]})
    if quarantined:
        bundle["flags"]["quarantine_proposed"] = True

    # §8.6 retraction
    retracted = scan_retraction(pages)
    bundle["flags"]["retracted"] = retracted

    # §8.9 title/DOI cross-check
    first_two = " ".join(p["text"] for p in pages[:2])
    full = "\n".join(p["text"] for p in pages)
    mm = title_doi_match(bundle["metadata"]["title"], bundle["metadata"]["doi"],
                         first_two, full, image_only)
    bundle["pdf"]["metadata_match"] = mm
    bundle["flags"]["wrong_pdf_likely"] = mm["wrong_pdf_likely"]

    # §8.8 deterministic eligibility gates
    g_doc = doc_type_eligible(doc_type)
    g_year = year_eligible(year_val, notes["via_snowballing"])
    g_lang = language_eligible(row.get("language", ""), override)
    g_text = not image_only            # truncated (mean ok) does NOT block (§8.5 / §8.10 note)
    g_retr = not retracted
    passes = all([g_doc, g_year, g_lang, g_text, g_retr]) and not quarantined
    bundle["deterministic_gates"] = {
        "doc_type_eligible": g_doc, "year_eligible": g_year,
        "language_eligible": g_lang, "not_retracted": g_retr,
        "extractable_text": g_text, "passes_all_deterministic_gates": passes,
    }
    # proceed to Stage 1 unless blocked / wrong-pdf / quarantined (§8.10)
    bundle["proceeds_to_stage1"] = bool(passes and not mm["wrong_pdf_likely"])
    return bundle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None, help="process first N Level-3 keys")
    ap.add_argument("--keys", type=str, default=None, help="comma-separated keys")
    ap.add_argument("--no-write", action="store_true", help="do not write bundle files")
    args = ap.parse_args()

    rows = load_csv()
    excluded_map = {e["excluded"]: e["primary"] for e in load_json("excluded_duplicates.json")["entries"]}
    redownload_keys = {e["key"] for e in load_json("redownload_queue.json")["entries"]}

    level3 = [k for k, r in rows.items()
              if parse_notes(r.get("notes", ""))["rayyan_decision"] in ("Included", "Maybe")]
    level3.sort()
    if args.keys:
        keys = [k.strip() for k in args.keys.split(",")]
    elif args.sample:
        keys = level3[:args.sample]
    else:
        keys = level3

    if not args.no_write:
        os.makedirs(STAGE0_DIR, exist_ok=True)

    from collections import Counter
    backend_ct, flag_ct = Counter(), Counter()
    proceed = avail = 0
    quarantine_proposed = []
    for key in keys:
        b = build_bundle(key, rows[key], excluded_map, redownload_keys)
        if not args.no_write:
            with open(os.path.join(STAGE0_DIR, f"{key}.json"), "w", encoding="utf-8") as f:
                json.dump(b, f, indent=2, ensure_ascii=False)
        backend_ct[b["pdf"]["extraction_backend"]] += 1
        for fl, v in b["flags"].items():
            if v:
                flag_ct[fl] += 1
        proceed += int(b.get("proceeds_to_stage1", False))
        avail += int(b["pdf"]["available"])
        if b["flags"].get("quarantine_proposed"):
            quarantine_proposed.append(key)

    ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    summary = {
        "timestamp": ts, "keys_processed": len(keys),
        "level3_universe": len(level3),
        "pdf_available": avail, "proceeds_to_stage1": proceed,
        "extraction_backends": dict(backend_ct),
        "flag_counts": dict(flag_ct),
        "quarantine_proposed_keys": quarantine_proposed,
    }
    partial_run = len(keys) < len(level3)
    if not args.no_write:
        # A partial run (--keys/--sample) must never clobber the global
        # summary — that is how stage0_summary.json ended up describing a
        # single-key smoke run. Partial summaries go to a timestamped file.
        if partial_run:
            summary["_partial_run"] = True
            fname = f"stage0_summary_partial_{ts.replace(':', '').replace('+', 'p')}.json"
        else:
            fname = "stage0_summary.json"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        if quarantine_proposed:
            with open(os.path.join(OUT, "stage0_quarantine_proposed.json"), "w", encoding="utf-8") as f:
                json.dump({"_note": "All §8.4 backends produced garbled text. NOT auto-moved "
                                    "(data/ is read-only). Reviewer to inspect and re-download.",
                           "keys": quarantine_proposed}, f, indent=2)
        with open(os.path.join(OUT, "progress.log"), "a", encoding="utf-8") as f:
            f.write(f"{ts}  STAGE0  keys={len(keys)} avail={avail} proceed={proceed} "
                    f"backends={dict(backend_ct)} flags={dict(flag_ct)}\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
