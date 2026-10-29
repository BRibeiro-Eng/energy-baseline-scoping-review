#!/usr/bin/env python3
"""§13.2 AI validation pilot setup — n=30 papers.

Draws 30 papers (seed 43, stratified 15 Included + 15 Maybe) from the
Stage-0-ELIGIBLE pool (proceeds_to_stage1 == true), EXCLUDING the 7 papers
already used in prior pilots:

  Form pilot §13.1 / v2.0 (5):
    rayyan-472535376, rayyan-472535533, rayyan-472536358,
    rayyan-472535592, rayyan-472535623
  v2.1 / v2.2 re-pilot fresh additions (2):
    rayyan-472536623, rayyan-472535494

Writes:
  output/pilot_30/SELECTED_KEYS.json         provenance of the draw
  output/pilot_30/manual/{key}.json          empty value-only blind template per paper
  output/pilot_30/INSTRUCTIONS_REVIEWER.md   how to fill the templates

Reviewer (B. Ribeiro) extracts these 30 manually FIRST (blind). THEN the
AI pipeline runs on the same 30. THEN per-variable Cohen's kappa / PABAK
is computed against the reviewer's extractions.

Schema: v2.2.1 (frozen). Templates are value-only (no evidence envelope —
evidence/confidence are AI-only, per §17 Q5).

Reproducible: same eligible pool + same exclusion set + seed 43 -> same 30.
"""
import glob
import json
import os
import random

import stage0_prepare as s0

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE0_DIR = os.path.join(HERE, "stage0")
PILOT_DIR = os.path.join(HERE, "pilot_30")
MANUAL_DIR = os.path.join(PILOT_DIR, "manual")

# Keys already used in earlier pilots — excluded from §13.2 sample
EXCLUDED_KEYS = {
    # §13.1 form pilot (v2.0)
    "rayyan-472535376", "rayyan-472535533", "rayyan-472536358",
    "rayyan-472535592", "rayyan-472535623",
    # v2.1 / v2.2 re-pilot fresh additions
    "rayyan-472536623", "rayyan-472535494",
}

SEED = 43
N_INC = 15
N_MAYBE = 15

# ============================================================ v2.2.1 schema field lists

# Eligibility — A1b paper_type, level_3b, plus the v2.2.1 borderline flag
ELIGIBILITY_FIELDS = {
    "methodological_eligibility": None,            # bool
    "ineligibility_reason": None,                  # str | null
    "borderline_review_synthesis_eligibility": False,
    "paper_type": None,                            # enum (7 values)
    "level_3b": None,                              # bool
}

# Level A judgement fields (Stage 2). A1, A2-A6, A12 come from Stage 0 metadata.
LEVEL_A_FIELDS = {
    "multi_site": None,                # A1c — true / false / "not applicable"
    "country_region": None,            # A7
    "sector_of_activity": None,        # A8 (verbatim)
    "type_of_organisation": None,      # A9 enum
    "ems_standard": [],                # A10a multi-enum
    "mv_protocol": [],                 # A10b multi-enum
    "regulatory_driver": [],           # A10c multi-enum
    "enpi_enb_model_types": [],        # A11 multi-enum
    "complementary_methodologies": [], # A11b multi-enum
}

# Level B (Stage 3) — only fill if level_3b is true.
LEVEL_B_FIELDS = {
    "normalisation_variables": [],          # B1 list of strings
    "baseline_period_start": None,          # B2a string | null | "not reported"
    "baseline_period_end": None,            # B2b string | null | "not reported"
    "baseline_construction_method": None,   # B2c free-text 1-3 sentences
    "validation_types": [],                 # B3 multi-enum
    "scale_of_application": None,           # B4 enum
    "scope_description": None,              # B4b free-text
    "identifies_model_limitations": None,   # B5 bool
    "specific_limitations": [],             # B6 multi-enum (empty if B5=false)
    "proposes_treatment_mechanism": None,   # B7 bool
    "proposes_adaptations": None,           # B8 bool
    "adaptation_types": [],                 # B9 multi-enum (empty if B8=false)
    "normative_framing_of_adaptations": None,  # B10 enum
    "empirical_refinery_application": None, # B11 bool
    "data_type": None,                      # B12 enum strict
    "model_parameters_reported": [],        # B13a list of strings
    "performance_metrics_reported": [],     # B13b list of {metric,value,unit,period_or_context}
    "implementation_barriers": [],          # B14 list of strings
}


def select_validation_pilot(included_keys, maybe_keys, seed, n_inc, n_maybe):
    """Deterministic stratified sample. Keys are sorted within each stratum
    before sampling so the result depends only on pool membership and seed
    (reproducibility, §14)."""
    random.seed(seed)
    inc = sorted(included_keys)
    may = sorted(maybe_keys)
    picks = sorted(random.sample(inc, n_inc)) + sorted(random.sample(may, n_maybe))
    return picks


def template_for(bundle):
    md = bundle["metadata"]
    return {
        "key": bundle["key"],
        "_pilot": (
            "§13.2 AI VALIDATION PILOT (n=30). BLIND manual extraction by reviewer "
            "FIRST, then AI pipeline runs over the same 30, then per-variable "
            "Cohen's kappa / PABAK against this manual reference. "
            "value-only schema (no evidence envelope — evidence/confidence are AI-only, "
            "per §17 Q5). Fill level_b ONLY if you classify the paper as Level 3B. "
            "Schema v2.2.1 (FROZEN)."
        ),
        # A1, A2-A6, A12 are Stage-0 deterministic; prefilled for context
        "metadata": {
            "paper_id": md["paper_id"],
            "authors": md["authors"],
            "year": md["year"],
            "title": md["title"],
            "source": md["source"],
            "document_type": md["document_type"],
            "source_string": md["source_string"],  # null universally — Rayyan export
            "rayyan_decision": md["rayyan_decision"],
        },
        "eligibility": dict(ELIGIBILITY_FIELDS),
        # Level A: leave fields null; v2.1 C2 scoping rule applies — if you
        # set methodological_eligibility=false, leave everything in level_a null.
        "level_a": dict(LEVEL_A_FIELDS),
        # Level B: leave fields null; fill ONLY if level_3b=true.
        "level_b": dict(LEVEL_B_FIELDS),
        "reviewer_notes": "",
    }


def main():
    bundles = [json.load(open(f, encoding="utf-8"))
               for f in glob.glob(os.path.join(STAGE0_DIR, "*.json"))]
    eligible = [b for b in bundles if b.get("proceeds_to_stage1")]

    # Apply exclusion — drop the 7 already-used keys before stratifying
    eligible_avail = [b for b in eligible if b["key"] not in EXCLUDED_KEYS]

    inc = [b["key"] for b in eligible_avail
           if b["metadata"]["rayyan_decision"] == "Included"]
    may = [b["key"] for b in eligible_avail
           if b["metadata"]["rayyan_decision"] == "Maybe"]

    assert len(inc) >= N_INC, f"only {len(inc)} Included eligible (need {N_INC})"
    assert len(may) >= N_MAYBE, f"only {len(may)} Maybe eligible (need {N_MAYBE})"

    picks = select_validation_pilot(inc, may, seed=SEED,
                                    n_inc=N_INC, n_maybe=N_MAYBE)
    by = {b["key"]: b for b in bundles}

    os.makedirs(MANUAL_DIR, exist_ok=True)

    selected = []
    for k in picks:
        md = by[k]["metadata"]
        selected.append({
            "key": k,
            "rayyan_decision": md["rayyan_decision"],
            "year": md["year"],
            "title": md["title"],
        })
        with open(os.path.join(MANUAL_DIR, f"{k}.json"), "w", encoding="utf-8") as f:
            json.dump(template_for(by[k]), f, indent=2, ensure_ascii=False)

    prov = {
        "purpose": "§13.2 AI validation pilot — n=30, kappa/PABAK against blind reviewer extraction",
        "schema_version": "v2.2.1 (FROZEN)",
        "pool": "Stage-0-eligible (proceeds_to_stage1 == true), EXCLUDING the 7 papers used in prior pilots",
        "pool_size_total_eligible": len(eligible),
        "pool_size_after_exclusion": len(eligible_avail),
        "excluded_keys": sorted(EXCLUDED_KEYS),
        "excluded_reason": "Already extracted by reviewer (form pilot §13.1) "
                           "and/or by AI in v2.1/v2.2 re-pilots — would contaminate kappa.",
        "strata_after_exclusion": {
            "Included_eligible": len(inc),
            "Maybe_eligible": len(may),
        },
        "seed": SEED,
        "stratification": f"{N_INC} Included + {N_MAYBE} Maybe",
        "selected_keys": picks,
        "selected": selected,
        "ai_extracts_these": True,
        "workflow_order": [
            "1. Reviewer fills output/pilot_30/manual/{key}.json BLIND (no AI assistance).",
            "2. AI pipeline runs Stage 1 -> Stage 2 -> Stage 3 over the same 30 PDFs.",
            "3. Per-variable Cohen's kappa / PABAK computed between reviewer JSONs and AI JSONs.",
            "4. Disagreements adjudicated; protocol amendments documented if structural issues surface.",
        ],
        "hard_gate": "PROTOCOL.md §18.10 — AI pipeline MUST NOT run before reviewer completes all 30 manual extractions.",
        "note_source_string": "A12 source_string is null for all papers (Rayyan export limitation).",
    }
    with open(os.path.join(PILOT_DIR, "SELECTED_KEYS.json"), "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2, ensure_ascii=False)
    print(json.dumps(prov, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
