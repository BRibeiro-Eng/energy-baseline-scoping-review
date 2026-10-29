#!/usr/bin/env python3
"""Validate detector-(c) responses, verify their quotes, emit recall_flags.json.

A response FIRES the detector if either signal list is non-empty -- never on
`conservative_classification` (C-2.3 §3-Step-4: "Detector (c) fires on any listed
continuous-process signal (the recall direction), not on the model's final
classification"). A model that lists a refinery signal and still says "not Corpus
B" has fired the detector; that is the whole point of counter-anchoring.

Every quote is checked against the paper's own Stage-0 text under the §6.3
normalisation. An unverifiable quote invalidates that signal, not the response:
the signal is dropped and logged, because a fabricated quote must not put a paper
into the census work-list on false pretences -- nor silently keep it out.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―]", "-", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def validate(rec, schema_keys):
    errs = []
    missing = schema_keys - set(rec)
    if missing:
        errs.append(f"missing fields: {sorted(missing)}")
    if not re.fullmatch(r"rayyan-\d+", str(rec.get("key", ""))):
        errs.append(f"bad key: {rec.get('key')!r}")
    if rec.get("application_strength") not in (
            "applied", "validated", "demonstrated", "mentioned_only", "none"):
        errs.append(f"bad application_strength: {rec.get('application_strength')!r}")
    if not isinstance(rec.get("conservative_classification"), bool):
        errs.append("conservative_classification must be boolean")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", type=Path, default=HERE / "responses")
    ap.add_argument("--out", type=Path, default=HERE.parent / "recall_flags.json")
    args = ap.parse_args()

    schema = json.loads((HERE / "response.schema.json").read_text())
    required = set(schema["required"])
    queue = set(json.loads((HERE / "QUEUE.json").read_text()))

    fired, clean, invalid, dropped = [], 0, [], []
    strength = Counter()
    seen = set()
    for path in sorted(args.responses.glob("rayyan-*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        key = rec.get("key") or path.stem
        seen.add(key)
        errs = validate(rec, required)
        if key not in queue:
            errs.append("key outside the concordant-excluded frame")
        if errs:
            invalid.append({"key": key, "errors": errs})
            continue
        bundle = json.loads((ROOT / "output" / "stage0" / f"{key}.json").read_text())
        text = norm(" ".join((p.get("text") or "")
                             for p in (bundle.get("pdf") or {}).get("pages") or []))
        kept = 0
        for field in ("listed_sector_signals", "other_continuous_flow_signals"):
            for sig in rec.get(field) or []:
                if norm(sig.get("quote", "")) in text:
                    kept += 1
                else:
                    dropped.append({"key": key, "field": field,
                                    "quote": str(sig.get("quote"))[:90]})
        strength[rec.get("application_strength")] += 1
        if kept:
            fired.append(key)
        else:
            clean += 1

    args.out.write_text(json.dumps(sorted(set(fired)), indent=1) + "\n", encoding="utf-8")
    report = {
        "queue": len(queue),
        "responses_present": len(seen),
        "responses_missing": len(queue - seen),
        "invalid": invalid,
        "fired_after_quote_verification": len(set(fired)),
        "no_signal": clean,
        "signals_dropped_unverifiable_quote": dropped,
        "application_strength": dict(strength),
        "complete": len(queue - seen) == 0 and not invalid,
    }
    (HERE / "collect_report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("invalid", "signals_dropped_unverifiable_quote")}, indent=1))
    print(f"invalid: {len(invalid)}  dropped signals: {len(dropped)}")
    if not report["complete"]:
        print("\nINCOMPLETE — the union cannot close until every queued paper has a valid response.")
    return report


if __name__ == "__main__":
    main()
