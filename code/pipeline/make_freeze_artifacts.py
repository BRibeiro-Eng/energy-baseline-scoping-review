#!/usr/bin/env python3
"""make_freeze_artifacts.py — corpus-freeze closing artefacts (reviewer decision,
2026-07-10: corpus FROZEN at the current canonical store; remaining missing PDFs
are declared non-recoverable).

Produces, from data/articles.csv + data/pdfs/ + data/excluded_duplicates.json +
data/redownload_queue.json:

  data/non_retrieved_records.json — one record per deduplicated-universe key
      (Included+Maybe minus the 3 Rayyan-dedup secondaries) with NO PDF in the
      canonical store. reason = "wrong_pdf_unresolved" for keys still unresolved
      in redownload_queue.json (wrong-content PDF quarantined), else
      "not_retrieved". This is the PRISMA "reports not retrieved" registry.

  data/MISSINGNESS.md — retrieved vs non-retrieved sensitivity tables (Rayyan
      decision, DOI presence, year band, document type, sector signal) so the
      thesis can characterise missingness rather than assume it random. The
      sector-signal section lists potential Corpus-B losses explicitly
      (title hits >=1 term of fn_hunt.CONTINUOUS_PROCESS_TERMS).

Pure inspection: reads data/, writes ONLY the two artefacts above. Never touches
a PDF. Reuses stage0_prepare (universe construction, notes parsing, doc-type
inference) and fn_hunt (canonical sector lexicon) so the freeze artefacts cannot
drift from the pipeline's own definitions.

Usage:
  python3 output/make_freeze_artifacts.py
"""
import json
import os
import re
import urllib.parse
from collections import Counter
from datetime import datetime, timezone

from fn_hunt import scan_text
from stage0_prepare import (DATA, PDFS, infer_document_type, load_csv,
                            load_json, parse_notes)

FREEZE_DATE = "2026-07-10"
NON_RETRIEVED_OUT = os.path.join(DATA, "non_retrieved_records.json")
MISSINGNESS_OUT = os.path.join(DATA, "MISSINGNESS.md")

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'&<>#]+", re.I)

# Small English stopword set for the title-language heuristic. A title with
# ZERO hits and >=4 words is flagged possible-non-English (conservative:
# never blocks anything, only annotates).
TITLE_STOPWORDS = {
    "the", "of", "and", "in", "to", "for", "a", "an", "on", "with", "by",
    "from", "at", "as", "into", "through", "based", "using", "towards",
    "toward", "via", "under", "between", "its",
}


def extract_doi(row: dict) -> str:
    """DOI from the doi column, else parsed out of url/notes (Scopus URLs carry
    doi=10.xxxx%2F... URL-encoded)."""
    doi = (row.get("doi") or "").strip()
    if doi:
        return doi.split()[0].rstrip(".,;")
    for field in ("url", "notes"):
        raw = urllib.parse.unquote(row.get(field) or "")
        m = DOI_RE.search(raw)
        if m:
            return m.group(0).rstrip(".,;")
    return ""


def language_flag(row: dict) -> str:
    """Annotation only: metadata language != English, or title with zero
    English stopwords (>=4 words). Empty string = no flag."""
    lang = (row.get("language") or "").strip()
    if lang and lang.lower() != "english":
        return f"metadata_language:{lang}"
    title_words = re.findall(r"[a-zA-ZÀ-ɏ]+", (row.get("title") or "").lower())
    if len(title_words) >= 4 and not any(w in TITLE_STOPWORDS for w in title_words):
        return "title_suggests_non_english"
    return ""


def year_band(year) -> str:
    try:
        y = int(year)
    except (TypeError, ValueError):
        return "unknown"
    if y < 2020:
        return "pre-2020"
    if y <= 2023:
        return "2020-2023"
    return "2024+"


def build_universe():
    """Deduplicated Level-3 universe: Included+Maybe minus dedup secondaries.
    Returns (records, excluded_keys) — records: {key: row+derived}."""
    rows = load_csv()
    excluded_keys = {e["excluded"] for e in load_json("excluded_duplicates.json")["entries"]}
    rq = load_json("redownload_queue.json")
    unresolved_wrong = {e["key"] for e in rq["entries"] if not e.get("resolved")}

    universe = {}
    for key, row in rows.items():
        decision = parse_notes(row.get("notes", ""))["rayyan_decision"]
        if decision not in ("Included", "Maybe") or key in excluded_keys:
            continue
        universe[key] = {
            "row": row,
            "decision": decision,
            "doi": extract_doi(row),
            "doc_type": infer_document_type(row),
            "band": year_band(row.get("year")),
            "sector_terms": scan_text(row.get("title") or ""),
            "retrieved": os.path.exists(os.path.join(PDFS, f"{key}.pdf")),
            "wrong_pdf_unresolved": key in unresolved_wrong,
        }
    return universe


def write_non_retrieved(universe):
    records = []
    for key in sorted(universe):
        u = universe[key]
        if u["retrieved"]:
            continue
        row = u["row"]
        rec = {
            "key": key,
            "title": row.get("title") or "",
            "year": row.get("year") or "",
            "journal": row.get("journal") or "",
            "doi": u["doi"],
            "rayyan_decision": u["decision"],
            "document_type": u["doc_type"],
            "reason": "wrong_pdf_unresolved" if u["wrong_pdf_unresolved"] else "not_retrieved",
        }
        lf = language_flag(row)
        if lf:
            rec["language_flag"] = lf
        records.append(rec)

    summary = {
        "total_non_retrieved": len(records),
        "by_rayyan_decision": dict(Counter(r["rayyan_decision"] for r in records)),
        "by_doi_presence": {
            "with_doi": sum(1 for r in records if r["doi"]),
            "without_doi": sum(1 for r in records if not r["doi"]),
        },
        "by_reason": dict(Counter(r["reason"] for r in records)),
    }
    payload = {
        "_comment": "PRISMA 'reports not retrieved' registry. Corpus FROZEN "
                    f"{FREEZE_DATE} (reviewer decision): these keys have no PDF in the "
                    "canonical store level3_extraction/data/pdfs/ and are declared "
                    "non-recoverable. reason=wrong_pdf_unresolved means the only PDF "
                    "ever obtained was wrong-content (quarantined in "
                    "pdfs_quarantine/wrong_pdf/). See data/MISSINGNESS.md for the "
                    "retrieved-vs-non-retrieved sensitivity analysis.",
        "version": "1.0",
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "corpus_frozen": FREEZE_DATE,
        "_summary": summary,
        "records": records,
    }
    with open(NON_RETRIEVED_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return records, summary


def _table(universe, label, keyfn, order=None):
    """Markdown table: retrieved / non-retrieved / retrieval-rate per stratum."""
    strata = {}
    for u in universe.values():
        strata.setdefault(keyfn(u), [0, 0])[0 if u["retrieved"] else 1] += 1
    keys = order or sorted(strata, key=lambda k: -sum(strata[k]))
    lines = [f"| {label} | Retrieved | Non-retrieved | Total | Retrieval rate |",
             "|---|---:|---:|---:|---:|"]
    for k in keys:
        if k not in strata:
            continue
        ret, non = strata[k]
        tot = ret + non
        lines.append(f"| {k} | {ret} | {non} | {tot} | {100 * ret / tot:.1f}% |")
    ret_all = sum(v[0] for v in strata.values())
    non_all = sum(v[1] for v in strata.values())
    tot_all = ret_all + non_all
    lines.append(f"| **All** | **{ret_all}** | **{non_all}** | **{tot_all}** | "
                 f"**{100 * ret_all / tot_all:.1f}%** |")
    return "\n".join(lines)


def write_missingness(universe):
    non_sector = [(k, u) for k, u in sorted(universe.items())
                  if not u["retrieved"] and u["sector_terms"]]

    md = []
    md.append("# MISSINGNESS — retrieved vs non-retrieved sensitivity analysis")
    md.append("")
    md.append(f"Corpus frozen **{FREEZE_DATE}** (reviewer decision). Deduplicated "
              f"Level-3 universe: **{len(universe)}** records "
              f"(Included+Maybe minus 3 Rayyan-dedup secondaries); "
              f"**{sum(u['retrieved'] for u in universe.values())}** retrieved, "
              f"**{sum(not u['retrieved'] for u in universe.values())}** non-retrieved "
              "(registry: `non_retrieved_records.json`). Generated by "
              "`output/make_freeze_artifacts.py`.")
    md.append("")
    md.append("## By Rayyan decision")
    md.append("")
    md.append(_table(universe, "Decision", lambda u: u["decision"],
                     order=["Included", "Maybe"]))
    md.append("")
    md.append("## By DOI presence")
    md.append("")
    md.append(_table(universe, "DOI", lambda u: "with DOI" if u["doi"] else "no DOI",
                     order=["with DOI", "no DOI"]))
    md.append("")
    md.append("## By year band")
    md.append("")
    md.append(_table(universe, "Year band", lambda u: u["band"],
                     order=["pre-2020", "2020-2023", "2024+", "unknown"]))
    md.append("")
    md.append("## By document type (inferred, stage0 rule)")
    md.append("")
    md.append(_table(universe, "Document type", lambda u: u["doc_type"]))
    md.append("")
    md.append("## By sector signal (title hits fn_hunt lexicon)")
    md.append("")
    md.append(_table(universe, "Sector signal",
                     lambda u: "sector signal" if u["sector_terms"] else "no signal",
                     order=["sector signal", "no signal"]))
    md.append("")
    md.append(f"### Potential Corpus-B losses ({len(non_sector)} non-retrieved "
              "records with sector signals)")
    md.append("")
    if non_sector:
        md.append("| Key | Year | Terms hit | Title |")
        md.append("|---|---|---|---|")
        for k, u in non_sector:
            title = (u["row"].get("title") or "").replace("|", "\\|")
            md.append(f"| {k} | {u['row'].get('year') or '?'} | "
                      f"{', '.join(u['sector_terms'])} | {title} |")
    else:
        md.append("(none)")
    md.append("")
    md.append("## Interpretation")
    md.append("")

    def rate(pred):
        sel = [u for u in universe.values() if pred(u)]
        return 100 * sum(u["retrieved"] for u in sel) / len(sel) if sel else float("nan")

    md.append(
        "Missingness is **not random**: retrieval succeeded far more often for "
        f"records with a DOI ({rate(lambda u: u['doi']):.1f}%) than without "
        f"({rate(lambda u: not u['doi']):.1f}%), and more often for Included "
        f"({rate(lambda u: u['decision'] == 'Included'):.1f}%) than Maybe "
        f"({rate(lambda u: u['decision'] == 'Maybe'):.1f}%) records — the missing set "
        "is dominated by DOI-less records and conference proceedings, i.e. records "
        "that were both harder to retrieve and, on average, less likely to survive "
        "full-text eligibility. The practical consequence for the review is "
        "bounded by the sector-signal census above: the titles listed there are the "
        "non-retrieved records that could plausibly have contributed to Corpus B "
        "(continuous-process sectors), and they must be acknowledged as a limitation "
        "in the PRISMA flow ('reports not retrieved') rather than silently dropped. "
        "All counts are reproducible from `articles.csv` + the frozen PDF store via "
        "this script.")
    md.append("")

    with open(MISSINGNESS_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    universe = build_universe()
    records, summary = write_non_retrieved(universe)
    write_missingness(universe)
    print(f"universe={len(universe)} retrieved={sum(u['retrieved'] for u in universe.values())} "
          f"non_retrieved={len(records)}")
    print(json.dumps(summary, indent=2))
    print(f"wrote {NON_RETRIEVED_OUT}")
    print(f"wrote {MISSINGNESS_OUT}")


if __name__ == "__main__":
    main()
