#!/usr/bin/env python3
"""§13.2 HYBRID design — split the n=30 sample into:

  - 10 BLIND   (5 Included + 5 Maybe) — reviewer extracts FIRST, no AI visible.
                Yields the clean Cohen's kappa / PABAK (AI vs blind human).
  - 20 VERIFICATION (10 Included + 10 Maybe) — reviewer reviews/corrects AI output.
                Yields a correction rate; the gap vs the blind kappa estimates
                the anchoring bias.

Statistical rationale:
  Both subsets are drawn from the same seed-43 stratified sample, so they are
  exchangeable in expectation. anchoring_bias ≈ agreement_20 − kappa_10.

Operations order (HARD GATE, PROTOCOL.md §18.10):
  1. Reviewer fills manual/blind/{key}.json   (no AI).
  2. AI pipeline runs on all 30.
  3. kappa/PABAK computed on the 10 blind.
  4. Reviewer reviews manual/verification/{key}.json (AI-prefilled).
  5. anchoring bias estimated; consolidated report.

Reorganises the flat manual/{key}.json templates into manual/blind/ and
manual/verification/. Idempotent: re-running restores the same split.

Reproducible: same 30 + seed -> same 10/20 partition.
"""
import json
import os
import random
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT_DIR = os.path.join(HERE, "pilot_30")
MANUAL_DIR = os.path.join(PILOT_DIR, "manual")
BLIND_DIR = os.path.join(MANUAL_DIR, "blind")
VERIF_DIR = os.path.join(MANUAL_DIR, "verification")

SEED = 43          # same family as the n=30 draw; second independent shuffle
N_BLIND_INC = 5
N_BLIND_MAYBE = 5


def stratified_blind_pick(inc_keys, maybe_keys, seed, n_inc, n_maybe):
    """Deterministic: sort each stratum, sample n from each for the blind set."""
    random.seed(seed)
    inc = sorted(inc_keys)
    may = sorted(maybe_keys)
    blind = set(sorted(random.sample(inc, n_inc)) + sorted(random.sample(may, n_maybe)))
    return blind


def main():
    prov = json.load(open(os.path.join(PILOT_DIR, "SELECTED_KEYS.json"), encoding="utf-8"))
    selected = prov["selected"]          # 30 dicts: key, rayyan_decision, year, title

    inc = [s["key"] for s in selected if s["rayyan_decision"] == "Included"]
    may = [s["key"] for s in selected if s["rayyan_decision"] == "Maybe"]
    assert len(inc) == 15 and len(may) == 15, f"expected 15+15, got {len(inc)}+{len(may)}"

    blind = stratified_blind_pick(inc, may, SEED, N_BLIND_INC, N_BLIND_MAYBE)
    by_key = {s["key"]: s for s in selected}

    os.makedirs(BLIND_DIR, exist_ok=True)
    os.makedirs(VERIF_DIR, exist_ok=True)

    blind_keys, verif_keys = [], []
    for s in selected:
        k = s["key"]
        src = os.path.join(MANUAL_DIR, f"{k}.json")
        if k in blind:
            dst = os.path.join(BLIND_DIR, f"{k}.json")
            blind_keys.append(k)
        else:
            dst = os.path.join(VERIF_DIR, f"{k}.json")
            verif_keys.append(k)
        # move flat template into its phase folder (idempotent)
        if os.path.exists(src):
            shutil.move(src, dst)
        elif not os.path.exists(dst):
            raise FileNotFoundError(f"template missing for {k}: neither {src} nor {dst}")
        # tag the template with its phase + reset _pilot note accordingly
        tpl = json.load(open(dst, encoding="utf-8"))
        tpl["_phase"] = "blind" if k in blind else "verification"
        if k in blind:
            tpl["_pilot"] = (
                "§13.2 BLIND extraction (10 of 30). Extract FIRST, with NO AI output "
                "visible. This yields the clean AI-vs-human Cohen's kappa / PABAK. "
                "value-only schema (no evidence envelope). Fill level_b ONLY if Level 3B. "
                "Schema v2.2.1 (FROZEN)."
            )
        else:
            tpl["_pilot"] = (
                "§13.2 VERIFICATION extraction (20 of 30). This template will be "
                "AI-PREFILLED after the blind phase closes; you then review/correct it. "
                "Do NOT fill before the AI pass. Schema v2.2.1 (FROZEN)."
            )
        json.dump(tpl, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    split = {
        "purpose": "§13.2 HYBRID validation split — 10 blind (clean kappa) + 20 verification (correction rate + anchoring-bias estimate)",
        "schema_version": "v2.2.1 (FROZEN)",
        "parent_sample": "pilot_30/SELECTED_KEYS.json (n=30, seed 43)",
        "split_seed": SEED,
        "split_rule": f"second independent seed-{SEED} stratified shuffle; "
                      f"{N_BLIND_INC} Included + {N_BLIND_MAYBE} Maybe to blind, remainder to verification",
        "blind": {
            "n": len(blind_keys),
            "n_included": sum(1 for k in blind_keys if by_key[k]["rayyan_decision"] == "Included"),
            "n_maybe": sum(1 for k in blind_keys if by_key[k]["rayyan_decision"] == "Maybe"),
            "keys": sorted(blind_keys),
            "dir": "manual/blind/",
            "reviewer_action": "Extract FIRST, no AI visible (hard gate §18.10).",
        },
        "verification": {
            "n": len(verif_keys),
            "n_included": sum(1 for k in verif_keys if by_key[k]["rayyan_decision"] == "Included"),
            "n_maybe": sum(1 for k in verif_keys if by_key[k]["rayyan_decision"] == "Maybe"),
            "keys": sorted(verif_keys),
            "dir": "manual/verification/",
            "reviewer_action": "Review/correct AI-prefilled output AFTER the AI pass.",
        },
        "statistics": {
            "clean_reliability": "Cohen's kappa + PABAK on the 10 blind (AI vs blind human).",
            "verification_metric": "Field-level correction rate on the 20.",
            "anchoring_bias_estimate": "agreement_20 − kappa_10 (both subsets exchangeable, same stratified parent).",
            "power_caveat": "n=10 blind => wide kappa CI; PABAK reported alongside; conclusion rests on the combination (10 blind + 20 verification + programmatic grounding check), not any single metric.",
        },
        "operations_order": [
            "1. Reviewer fills manual/blind/{key}.json (10) BLIND.",
            "2. AI pipeline runs Stage 1->2->3 on all 30.",
            "3. kappa/PABAK on the 10 blind.",
            "4. AI output prefilled into manual/verification/{key}.json (20); reviewer reviews/corrects.",
            "5. correction rate + anchoring-bias estimate; consolidated report.",
        ],
        "hard_gate": "AI pipeline MUST NOT run before the 10 blind are complete.",
    }
    with open(os.path.join(PILOT_DIR, "VALIDATION_SPLIT.json"), "w", encoding="utf-8") as f:
        json.dump(split, f, indent=2, ensure_ascii=False)
    print(json.dumps(split, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
