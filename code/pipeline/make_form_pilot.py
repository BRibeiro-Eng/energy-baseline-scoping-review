#!/usr/bin/env python3
"""
§13.1 Form pilot setup. Draws 5 papers (seed 42, stratified 3 Included + 2 Maybe)
from the Stage-0-ELIGIBLE pool (proceeds_to_stage1 == true, per §18.7) and writes:

  output/pilot_form/SELECTED_KEYS.json   provenance of the draw
  output/pilot_form/{key}.json           empty value-only template per paper

The reviewer (B. Ribeiro) extracts these 5 manually using the schema (§6.1/§6.2)
to verify form consistency/completeness, then declares the schema frozen (§18.8).
The AI does NOT extract these papers.

Run AFTER stage0_prepare.py. Reproducible: same eligible pool + seed -> same 5.
"""
import glob
import json
import os

import stage0_prepare as s0   # reuse the tested select_form_pilot

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE0_DIR = os.path.join(HERE, "stage0")
PILOT_DIR = os.path.join(HERE, "pilot_form")

# Level A / B field names (PROTOCOL.md §6)
LEVEL_A_JUDGMENT = ["country_region", "sector_of_activity", "type_of_organisation",
                    "normative_context", "enpi_enb_model_types"]
LEVEL_B = ["normalisation_variables", "baseline_construction_method", "validation_types",
           "scale_of_application", "identifies_limitations", "specific_limitations",
           "proposes_treatment_mechanism", "proposes_adaptations", "adaptation_types",
           "normative_framing_of_adaptations", "empirical_refinery_application",
           "data_type", "performance_metrics_reported", "implementation_barriers"]


def template_for(bundle):
    md = bundle["metadata"]
    return {
        "key": bundle["key"],
        "_pilot": "FORM PILOT (§13.1). Chart manually using the schema (§6.1/§6.2). "
                  "Record any form consistency/completeness problems in 'form_issues'. "
                  "value-only — evidence/confidence not needed for the form pilot. "
                  "Fill level_b ONLY if you classify the paper as Level 3B.",
        "metadata": {  # A1-A6, A12 — deterministic, prefilled from Stage 0 for your review
            "paper_id": md["paper_id"], "authors": md["authors"], "year": md["year"],
            "title": md["title"], "source": md["source"],
            "document_type": md["document_type"],
            "source_string": md["source_string"],   # null: see SELECTED_KEYS.json note
            "rayyan_decision": md["rayyan_decision"],
        },
        "eligibility": {"methodological_eligibility": None,
                        "ineligibility_reason": None, "level_3b": None},
        "level_a": {f: ([] if f == "enpi_enb_model_types" else None) for f in LEVEL_A_JUDGMENT},
        "level_b": {f: None for f in LEVEL_B},
        "form_issues": "",
    }


def main():
    bundles = [json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(STAGE0_DIR, "*.json"))]
    eligible = [b for b in bundles if b.get("proceeds_to_stage1")]
    inc = [b["key"] for b in eligible if b["metadata"]["rayyan_decision"] == "Included"]
    may = [b["key"] for b in eligible if b["metadata"]["rayyan_decision"] == "Maybe"]

    picks = s0.select_form_pilot(inc, may, seed=42, n_inc=3, n_maybe=2)
    by = {b["key"]: b for b in bundles}

    os.makedirs(PILOT_DIR, exist_ok=True)
    selected = []
    for k in picks:
        md = by[k]["metadata"]
        selected.append({"key": k, "rayyan_decision": md["rayyan_decision"],
                         "year": md["year"], "title": md["title"]})
        with open(os.path.join(PILOT_DIR, f"{k}.json"), "w", encoding="utf-8") as f:
            json.dump(template_for(by[k]), f, indent=2, ensure_ascii=False)

    prov = {
        "purpose": "§13.1 form pilot — verify charting form consistency/completeness",
        "pool": "Stage-0-eligible (proceeds_to_stage1 == true), per §18.7",
        "pool_size": len(eligible),
        "strata": {"Included_eligible": len(inc), "Maybe_eligible": len(may)},
        "seed": 42, "stratification": "3 Included + 2 Maybe",
        "selected_keys": picks,
        "selected": selected,
        "ai_extracts_these": False,
        "next": "Reviewer charts these 5 manually -> declares schema frozen (§18.8). "
                "AI pipeline does NOT run on them.",
        "note_source_string": "A12 source_string is null for all papers (the Rayyan export "
                              "carries no STRING-A/STRING-B provenance). Documented limitation.",
    }
    with open(os.path.join(PILOT_DIR, "SELECTED_KEYS.json"), "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2, ensure_ascii=False)
    print(json.dumps(prov, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
