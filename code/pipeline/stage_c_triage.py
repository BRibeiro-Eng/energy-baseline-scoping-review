#!/usr/bin/env python3
"""Stage C triage — what the reviewer reads, and why, from ONE extraction surface.

  /usr/local/bin/python3 output/stage_c_triage.py --surface pilot_claude [--csv]

WHY THIS EXISTS. The registered design (Protocol C-2.3 §3-Step-1/Step-2) extracts with two
model families and partitions every (paper, field) cell into concordant or divergent. The
divergence set is what routed the reviewer's attention. Reviewer decision 2026-09-12: the second
surface is no longer an extractor, so that router is gone for Tier 2 (Tiers 1 and 3 already ran
dual and are untouched).

Nothing is lost from the CLAIMS -- the verification matrix never treated model agreement as
verification, only as provisional. What is lost is the TRIAGE. This replaces it with a signal
that is arguably better suited to the job and costs no second pass: the record's own
declarations about where it is weak.

  * `support_class: requires inference` -- the extractor says it combined the quote with
    reasoning. The matrix already bars these from every headline figure.
  * a routing class -- interleaved, line-number ambiguity, locator corrected: the grounding
    check itself is asking for a human.
  * `claim_status: general` -- a textbook statement, which must not be counted as a finding.
    This is the defect that motivated the whole re-extraction.
  * an `other` enum with a verbatim -- the closed list did not hold the answer.
  * an absence with a basis and no quote -- an absence can only be confirmed by reading, never
    by checking what was found.

The honest comparison with divergence routing: inter-model divergence flags FEWER cells (two
models agree far more often than one model hedges), but on a criterion that shares model biases
-- two surfaces reading a sentence the same wrong way is invisible to it. These signals flag
more cells, on a criterion about this extraction's own weakness, and every one of them is
declared in the record rather than inferred.

PRIORITIES
  P0  the instrument asked for a human: a routing class. Not optional.
  P1  a result depends on this cell AND the cell is self-declared weak.
  P2  a result depends on this cell AND it is an absence -- reading is the only way.
  P3  a result depends on this cell and it is a direct statement with an exact quote: sample.
  P4  no registered result depends on this cell. No human time is budgeted for it.

The field -> result map below is the operationalisation of
RESULT_FIELD_VERIFICATION_MATRIX_2026-09-12.md §3. Editing one without the other is a defect.
"""
import argparse, collections, csv, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT); sys.path.insert(0, HERE)
from stage_c_grounding import check_record, walk_values            # noqa: E402

# result -> the path fragments whose cells feed it (matrix §3)
RESULTS = {
    "R1 mechanisms reported, and their shape": ["mechanisms["],
    "R2 n of 42 report class X (denominator)": ["mechanisms["],
    "R3 fouling/catalyst absent (denominator)": ["mechanisms["],
    "R4 which effects dominate": ["mechanisms["],
    "R5 general is not a finding": ["mechanisms["],
    "R6 adaptations recur, unanchored": ["adaptations["],
    "R7 two thirds propose nothing (denominator)": ["adaptations["],
    "R8 adaptation-to-mechanism link": ["adaptations["],
    "R9 barriers stable across sectors": ["implementation_barriers[", "sector_registered"],
    "R10 energy not metered at the boundary": ["C5_measurement["],
    "R11 baselines seldom rebuilt": ["C6_re_estimation"],
    "R12 validity envelopes rarely stated": ["C7_validity_envelope"],
    "R13 out-of-sample validation is rare": ["C8_metrics"],
    "R14 reproducibility elements": ["C13_reproducibility"],
    "R15 transferability to a refinery (SQ4)": ["refinery_or_petrochemical_case",
                                               "C12_data_requirements", "C5_measurement[",
                                               "implementation_barriers["],
}


def results_for(path):
    return [r for r, frags in RESULTS.items() if any(f in path for f in frags)]


def weak(env):
    """Reasons this cell is self-declared weak. Empty means it declares itself strong."""
    why = []
    if env.get("support_class") == "requires inference":
        why.append("requires inference")
    if env.get("claim_status") == "general":
        why.append("claim_status general")
    for k, v in env.items():
        if k.endswith("other_verbatim") and v:
            why.append(f"{k} set")
    if env.get("locator_corrected"):
        why.append("locator corrected")
    return why


def triage_record(rec, pages):
    g = check_record(rec, pages)
    routed = {c["path"] for c in g["review_candidates"]}
    rows = []
    for path, env in walk_values(rec):
        rs = results_for(path)
        w = weak(env)
        absent = bool(env.get("absence_basis")) and not env.get("evidence_quote")
        if path in routed:
            p, why = "P0", "the grounding check routed this cell for human reading"
        elif rs and w:
            p, why = "P1", "; ".join(w)
        elif rs and absent:
            p, why = "P2", f"absence ({env.get('absence_basis')}) — only reading confirms it"
        elif rs:
            p, why = "P3", "direct statement with an exact quote — sample only"
        else:
            p, why = "P4", "no registered result depends on this cell"
        rows.append({"paper": rec["paper_key"], "priority": p, "path": path, "why": why,
                     "results": "; ".join(r.split()[0] for r in rs),
                     "page": env.get("page"),
                     "value": str(env.get("value"))[:70],
                     "quote": (env.get("evidence_quote") or "")[:90]})
    return rows, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", required=True)
    ap.add_argument("--csv", action="store_true", help="write the worklist to production/")
    a = ap.parse_args()
    d = f"production/stage_c/{a.surface}/outputs"
    keys = sorted(os.path.basename(p)[:-5] for p in glob.glob(d + "/rayyan-*.json"))
    if not keys:
        sys.exit(f"no records in {d}")
    allrows, per = [], {}
    for k in keys:
        rec = json.load(open(f"{d}/{k}.json", encoding="utf-8"))
        pages = json.load(open(f"output/stage0/{k}.json", encoding="utf-8"))["pdf"]["pages"]
        rows, _ = triage_record(rec, pages)
        allrows += rows
        per[k] = collections.Counter(r["priority"] for r in rows)
    print(f"{'paper':18s} {'P0':>4s} {'P1':>4s} {'P2':>4s} {'P3':>4s} {'P4':>5s} "
          f"{'to read':>8s} {'cells':>6s}")
    tot = collections.Counter()
    for k in keys:
        c = per[k]
        read = c["P0"] + c["P1"] + c["P2"]
        print(f"{k:18s} {c['P0']:4d} {c['P1']:4d} {c['P2']:4d} {c['P3']:4d} {c['P4']:5d} "
              f"{read:8d} {sum(c.values()):6d}")
        tot.update(c)
    read = tot["P0"] + tot["P1"] + tot["P2"]
    n = sum(tot.values())
    print(f"{'TOTAL':18s} {tot['P0']:4d} {tot['P1']:4d} {tot['P2']:4d} {tot['P3']:4d} "
          f"{tot['P4']:5d} {read:8d} {n:6d}")
    print(f"\nmust read: {read}/{n} cells ({read/n:.0%}) · sample: {tot['P3']} · "
          f"not result-bearing: {tot['P4']} ({tot['P4']/n:.0%})")
    print(f"per paper, mean: {read/len(keys):.0f} cells to read, {tot['P3']/len(keys):.0f} to sample")
    print("\nP1 reasons:")
    for why, c in collections.Counter(
            w for r in allrows if r["priority"] == "P1"
            for w in r["why"].split("; ")).most_common():
        print(f"  {c:4d}  {why}")
    if a.csv:
        out = f"production/stage_c/{a.surface}/triage_worklist.csv"
        order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
        allrows.sort(key=lambda r: (order[r["priority"]], r["paper"], r["path"]))
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(allrows[0].keys()))
            w.writeheader(); w.writerows(allrows)
        print(f"\nworklist: {out}")


if __name__ == "__main__":
    main()
