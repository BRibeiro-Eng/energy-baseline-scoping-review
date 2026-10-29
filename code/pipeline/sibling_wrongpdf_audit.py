#!/usr/bin/env python3
"""Sibling audit for the rayyan-472535725 wrong-PDF class.

Read-only. Scans every output/stage0/*.json for the 725 failure signature:

  The PDF's OWN page-1 title line is near-identical to the Rayyan title, so the
  §8.9 gate (fuzz.partial_ratio >= 70 over the first two pages) waves it through,
  BUT a distinctive content word of the Rayyan title is missing from that title
  line -- the tell-tale of a companion paper by the same authors.
  (725: Rayyan "Applying ENERGY management ..." vs PDF "Applying WASTE Management ...")

Matching against the title LINE, not the whole page, is what makes this work:
"energy" does appear elsewhere on 725's page 1, so a whole-page test misses it.

Emits a ranked JSON + console report. Mutates nothing.
"""
import json
import os
import re
import sys
from rapidfuzz import fuzz

STAGE0 = "output/stage0"

STOP = {
    "the", "and", "for", "with", "from", "that", "this", "using", "use", "used",
    "case", "study", "studies", "into", "its", "his", "her", "their", "are", "was",
    "were", "been", "have", "has", "had", "not", "but", "all", "any", "can", "may",
    "new", "via", "per", "under", "over", "between", "among", "based", "toward",
    "towards", "paper", "article", "vol", "volume", "part",
    "open", "access", "abstract", "introduction", "keywords", "doi", "issn", "isbn",
    "http", "https", "www", "org", "com", "pdf", "page", "pages", "author", "authors",
    "one", "two", "three", "first", "second", "third", "also", "such", "some",
    "more", "most", "other", "others", "than", "then", "when", "where", "which",
    "who", "whose", "how", "why", "what", "about", "after", "before", "during",
    "each", "both", "these", "those", "there", "here", "will", "would", "could",
    "should", "must", "shall", "does", "did", "done", "make", "made", "many",
    "much", "very", "well", "good", "best",
}


def norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def present(word: str, text_norm: str, text_squash: str) -> bool:
    """Hyphenation/line-break tolerant containment ('effi- ciency' -> 'efficiency')."""
    if word in text_norm or word in text_squash:
        return True
    # derivational tolerance: efficiency/efficient share a 5-char stem
    if len(word) >= 6 and (word[:5] in text_norm or word[:5] in text_squash):
        return True
    return False


def content_words(title: str):
    return [w for w in norm(title).split() if len(w) >= 4 and w not in STOP]


def best_title_line(page1_text: str, title: str):
    """Best-matching contiguous 1-3 line window in the top of page 1.

    Maximising similarity to the Rayyan title is deliberately conservative: if a
    line containing the 'missing' word exists anywhere up top, it gets picked and
    the bundle is NOT flagged.
    """
    lines = [ln.strip() for ln in (page1_text or "").splitlines() if ln.strip()]
    lines = lines[:35]
    nt = norm(title)
    best, best_s = "", 0.0
    for i in range(len(lines)):
        for span in (1, 2, 3):
            if i + span > len(lines):
                continue
            cand = " ".join(lines[i:i + span])
            if len(norm(cand)) < 12:
                continue
            s = fuzz.ratio(nt, norm(cand))
            if s > best_s:
                best_s, best = s, cand
    return best, round(best_s, 1)


def years_in(text: str):
    return set(re.findall(r"\b(19[5-9]\d|20[0-4]\d)\b", text or ""))


def main():
    rows = []
    files = sorted(f for f in os.listdir(STAGE0) if f.endswith(".json"))
    assessed = 0
    for fn in files:
        try:
            d = json.load(open(os.path.join(STAGE0, fn)))
        except Exception as e:
            print(f"!! unreadable {fn}: {e}", file=sys.stderr)
            continue

        pdf = d.get("pdf") or {}
        flags = d.get("flags") or {}
        if not pdf.get("available") or flags.get("image_only_pdf"):
            continue
        md = d.get("metadata") or {}
        title = md.get("title") or ""
        pages = pdf.get("pages") or []
        p1 = (pages[0].get("text") if pages else "") or ""
        p1 = p1[:2500]
        if not p1.strip() or not title.strip():
            continue
        assessed += 1

        mm = pdf.get("metadata_match") or {}
        partial = mm.get("title_match_score")
        line, line_score = best_title_line(p1, title)

        nl, sl = norm(line), norm(line).replace(" ", "")
        missing = [w for w in content_words(title) if not present(w, nl, sl)]

        np1, sp1 = norm(p1), norm(p1).replace(" ", "")
        missing_page = [w for w in missing if not present(w, np1, sp1)]

        md_year = md.get("year")
        p1_years = years_in(p1)
        year_off = bool(md_year and p1_years and str(md_year) not in p1_years)

        src = md.get("source") or ""
        src_toks = [w for w in norm(src).split() if len(w) >= 4 and w not in STOP]
        src_hit = (not src_toks) or any(present(t, np1, sp1) for t in src_toks)

        # --- the 725 signature ---
        if not missing or line_score >= 96:
            continue

        risk = 4 * len(missing) + 2 * len(missing_page)
        why = [f"title word(s) absent from the PDF's own title line: {missing}"]
        if missing_page:
            why.append(f"...and absent from all of page 1: {missing_page}")
        if line_score < 90:
            risk += 2
            why.append(f"page-1 title line only {line_score}% == Rayyan title")
        if partial is not None and partial >= 70:
            why.append(f"yet the §8.9 gate scored {partial} (>=70) -> wrong_pdf_likely=false")
        if year_off:
            risk += 2
            why.append(f"Rayyan year {md_year} absent from page 1 (found: {sorted(p1_years)[:6]})")
        if not src_hit:
            risk += 1
            why.append(f"journal '{src}' not found on page 1")

        rows.append({
            "key": d.get("key"),
            "risk": risk,
            "rayyan_title": title,
            "pdf_page1_title_line": line,
            "page1_title_ratio": line_score,
            "gate_title_match_score": partial,
            "gate_wrong_pdf_likely": mm.get("wrong_pdf_likely"),
            "proceeds_to_stage1": d.get("proceeds_to_stage1"),
            "missing_from_title_line": missing,
            "missing_from_whole_page1": missing_page,
            "rayyan_year": md_year,
            "page1_years": sorted(p1_years)[:8],
            "rayyan_source": src,
            "authors": md.get("authors"),
            "doi": md.get("doi"),
            "pdf_md5": pdf.get("md5"),
            "reasons": why,
        })

    rows.sort(key=lambda r: (-r["risk"], r["key"]))
    out = "output/sibling_wrongpdf_audit_20260811.json"
    json.dump({
        "generated": "2026-08-11",
        "scanned_bundles": len(files),
        "assessed": assessed,
        "flagged": len(rows),
        "calibration": "rayyan-472535725 (the known wrong PDF) must appear in candidates",
        "method": ("flags bundles where a distinctive content word of the Rayyan title is "
                   "absent from the PDF's own page-1 title line while the §8.9 "
                   "partial_ratio gate still passed the PDF"),
        "candidates": rows,
    }, open(out, "w"), indent=2)

    print(f"scanned {len(files)} bundles, assessed {assessed} -> {len(rows)} flagged  ({out})\n")
    hit = next((r for r in rows if r["key"] == "rayyan-472535725"), None)
    print(f"CALIBRATION 725: {'FLAGGED risk=' + str(hit['risk']) if hit else '*** NOT FLAGGED ***'}\n")
    print(f"{'KEY':<22}{'RISK':>5} {'GATE':>6} {'P1FIT':>6}  MISSING FROM TITLE LINE")
    print("-" * 96)
    for r in rows:
        print(f"{r['key']:<22}{r['risk']:>5} {str(r['gate_title_match_score']):>6} "
              f"{str(r['page1_title_ratio']):>6}  {','.join(r['missing_from_title_line'])[:48]}")
    return rows


if __name__ == "__main__":
    main()
