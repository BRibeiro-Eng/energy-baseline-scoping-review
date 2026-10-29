#!/usr/bin/env python3
"""fn_census_build.py — assemble the C-2.3 §3-Step-4 FN candidate-union census.

Runs the two deterministic detectors over the concordant-excluded frame, merges
whatever detector (c) has returned, and emits the triaged work-list the reviewer
must EMPTY. All census logic lives in output/fn_hunt.py; this is the harness.

Frame: papers both models classified level_3b=false. The 23 divergent papers are
not here -- they are decided by the §3-Step-3 Tier-1 census, and §7 runs the two
in parallel precisely because the FN census inputs do not depend on them.

Triage (§3-Step-4): Tier-hit-A = a multi-word sector term, a sector metadata
match, or any model/recall-pass flag -> full read (~10-12 min). Tier-hit-B =
generic single terms only -> 2-minute skim with a one-line logged justification.
Any doubt promotes B to A. Nothing is dropped: both tiers are the census.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fn_hunt import CONTINUOUS_PROCESS_TERMS, candidate_union, hunt, scan_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "production" / "reviewer_workspace"
OUT = ROOT / "output" / "fn_census"

# §3-Step-4 names these as the generic single terms that route to the 2-min skim.
GENERIC_TERMS = {"steel", "steady-state", "steady state", "continuous process",
                 "refining", "petroleum"}

# Detector (a): "types the organisation as a continuous-process sector".
SECTOR_METADATA = re.compile(
    r"refin|petrochem|petroleum|cement|clinker|pulp|paper mill|steel|metallurg|"
    r"smelt|ammonia|ethylene|olefin|sulfur|sulphur|chlor|industrial gas|"
    r"air separation|glass|chemical|fertili[sz]er|methanol",
    re.IGNORECASE,
)


def _value(env):
    return env.get("value") if isinstance(env, dict) else env


def load_records():
    fams = ("chatgpt", "claude")
    keys = sorted(p.stem for p in (WS / "imports" / "claude").glob("rayyan-*.json"))
    recs = {}
    for k in keys:
        recs[k] = {f: json.loads((WS / "imports" / f / f"{k}.json").read_text(encoding="utf-8"))
                   for f in fams}
    return recs


def frame(recs):
    """Concordant-excluded set: both models said level_3b=false."""
    out = []
    for k, r in recs.items():
        vals = [_value((r[f].get("stage1") or {}).get("level_3b")) for f in ("chatgpt", "claude")]
        if not any(vals):
            out.append(k)
    return sorted(out)


def detector_a(recs, keys):
    """Model flags: borderline flag, or a continuous-process organisation/sector."""
    flagged, why = [], {}
    for k in keys:
        reasons = []
        for fam in ("chatgpt", "claude"):
            s1 = recs[k][fam].get("stage1") or {}
            s2 = recs[k][fam].get("stage2") or {}
            if s1.get("borderline_review_synthesis_eligibility") is True:
                reasons.append(f"{fam}:borderline_flag")
            for field in ("sector_of_activity", "type_of_organisation"):
                v = _value(s2.get(field))
                if isinstance(v, str) and SECTOR_METADATA.search(v):
                    reasons.append(f"{fam}:{field}={v[:44]}")
        if reasons:
            flagged.append(k)
            why[k] = sorted(set(reasons))
    return flagged, why


def detector_b(keys, extra_terms=()):
    items = []
    for k in keys:
        b = json.loads((ROOT / "output" / "stage0" / f"{k}.json").read_text(encoding="utf-8"))
        text = " ".join((p.get("text") or "") for p in (b.get("pdf") or {}).get("pages") or [])
        items.append({"key": k, "level_3b": False, "text": text})
    return hunt(items, extra_terms)


def tier_of(entry, why):
    """Tier-hit-A unless the ONLY evidence is generic single lexicon terms."""
    if {"model_flags", "recall_pass"} & set(entry["detectors"]):
        return "A"
    terms = set(entry.get("terms") or [])
    return "B" if terms and terms <= GENERIC_TERMS else "A"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recall-flags", type=Path,
                    help="JSON list of keys flagged by detector (c); omit before the pass runs")
    ap.add_argument("--extra-terms", type=Path,
                    help="JSON list of closure-loop lexicon expansions")
    args = ap.parse_args()

    recs = load_records()
    keys = frame(recs)
    a_keys, a_why = detector_a(recs, keys)
    extra = json.loads(args.extra_terms.read_text()) if args.extra_terms else []
    b_hits = detector_b(keys, extra)
    c_keys = json.loads(args.recall_flags.read_text()) if args.recall_flags else []
    stray = [k for k in c_keys if k not in set(keys)]
    if stray:
        raise SystemExit(f"recall flags outside the frame: {stray[:5]}")

    union = candidate_union(a_keys, b_hits, c_keys)
    for e in union:
        e["tier"] = tier_of(e, a_why)
        if e["key"] in a_why:
            e["model_flag_reasons"] = a_why[e["key"]]
        m = json.loads((ROOT / "output" / "stage0" / f"{e['key']}.json").read_text())["metadata"]
        e["title"], e["year"] = m.get("title"), m.get("year")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "candidates.json").write_text(json.dumps(union, indent=1, ensure_ascii=False) + "\n",
                                         encoding="utf-8")
    summary = {
        "frame_concordant_excluded": len(keys),
        "detector_a_model_flags": len(a_keys),
        "detector_b_lexicon": len(b_hits),
        "detector_c_recall_pass": len(c_keys),
        "detector_c_status": "RUN" if c_keys else "NOT RUN — union incomplete, census cannot close",
        "union_total": len(union),
        "tier_hit_A": sum(1 for e in union if e["tier"] == "A"),
        "tier_hit_B": sum(1 for e in union if e["tier"] == "B"),
        "lexicon_extra_terms": extra,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return union


if __name__ == "__main__":
    main()
