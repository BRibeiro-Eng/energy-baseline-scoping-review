"""v2.2.1 (FROZEN) presentation metadata for the extraction form.

Labels and help text stay local. Field types and controlled vocabularies are
projected from ``field_contract.py``, the machine-readable source of truth.

Field types:
  bool        tri-state: null (unanswered) / true / false
  enum        single choice from `options`
  multienum   any subset of the literal registered `options` (checkbox group)
  text        one-line free string
  textarea    multi-line free string
  list_str    add/remove free strings
  list_obj    add/remove objects with `item_fields`
"""

try:
    from field_contract import reviewer_field_contract
except ModuleNotFoundError:  # standalone reviewer workspace execution
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from field_contract import reviewer_field_contract

PAPER_TYPE = [
    "single applied case", "multi-case study", "review/synthesis",
    "maturity model or framework", "methodological/theoretical",
    "tool/software design", "other",
]

SCHEMA = {
    "eligibility": {
        "title": "Eligibility (§5.2) — fill for every paper",
        "fields": [
            {"name": "methodological_eligibility", "type": "bool",
             "label": "Methodological eligibility",
             "help": "Eligible iff the paper presents, proposes, evaluates, or critiques "
                     "an EnPI/EnB model with enough detail to identify what is measured "
                     "and at least one of its variables, functional form, or construction. "
                     "A fitted instance and reported validation are not eligibility gates."},
            {"name": "ineligibility_reason", "type": "text",
             "label": "Ineligibility reason",
             "help": "Short reason if ineligible; leave blank if eligible."},
            {"name": "borderline_review_synthesis_eligibility", "type": "bool",
             "label": "Borderline review/synthesis (→ mandatory human review)",
             "help": "TRUE only when a review/synthesis remains genuinely borderline after "
                     "checking whether it characterises the central models. Own fitted models "
                     "or ≥3 applications are descriptive signals, not eligibility gates."},
            {"name": "paper_type", "type": "enum", "options": PAPER_TYPE,
             "label": "Paper type (A1b)"},
            {"name": "level_3b", "type": "bool",
             "label": "Level 3B (continuous-process application)",
             "help": "TRUE iff the model is applied/validated EXPLICITLY in a continuous "
                     "process industry (refining, petrochem, cement, pulp&paper, steel, "
                     "continuous chemicals, industrial gases, other 24/7 continuous-flow). "
                     "‘could be applied to’ is NOT enough. Must be false if ineligible."},
        ],
    },
    "level_a": {
        "title": "Level A (§6.1) — fill only if eligible (else leave all null/empty)",
        "fields": [
            {"name": "multi_site", "type": "enum",
             "options": [True, False, "not applicable"],
             "label": "Multi-site (A1c)",
             "help": "‘not applicable’ only for review/synthesis aggregating across "
                     "independent orgs."},
            {"name": "country_region", "type": "text", "label": "Country/region (A7)",
             "help": "Case-study SITE geography ONLY. NOT author affiliation, NOT corporate HQ."},
            {"name": "sector_of_activity", "type": "text", "label": "Sector of activity (A8)",
             "help": "Verbatim from paper (or minimal normalisation). The verifier checks this."},
            {"name": "type_of_organisation", "type": "enum",
             "options": ["continuous process", "discrete manufacturing", "services",
                         "buildings", "mixed", "not specified"],
             "label": "Type of organisation (A9)",
             "help": "‘mixed’ = ≥2 distinct industrial sectors. NOT for multi-site single-org "
                     "(use multi_site), NOT for multi-process within one facility (use B4)."},
            {"name": "ems_standard", "type": "multienum", "other": True,
             "options": ["ISO 50001", "ISO 50002", "ISO 50006", "none"],
             "label": "EMS standard (A10a)"},
            {"name": "mv_protocol", "type": "multienum", "other": True,
             "options": ["IPMVP", "ASHRAE 14", "SEP M&V", "BPA MT&R", "ISO 17743", "none"],
             "label": "M&V protocol (A10b)"},
            {"name": "regulatory_driver", "type": "multienum", "other": True,
             "options": ["EU EED", "national audit decree", "EU-ETS",
                         "regional regulation", "none"],
             "label": "Regulatory driver (A10c)",
             "help": "EXCLUDES voluntary certs (SEP, ENERGY STAR). Driver must causally "
                     "apply to the studied dataset, not just be cited as legal context."},
            {"name": "enpi_enb_model_types", "type": "multienum", "other": True,
             "options": ["linear regression (1 IV)", "multiple regression (≥2 IVs)",
                         "physical model", "ML", "simple intensity ratio (unfitted)",
                         "SEC mean", "composite index (weighted, predicts/normalises energy)",
                         "change-point or SPC", "process integration", "not applicable"],
             "label": "EnPI/EnB model types (A11)",
             "help": "linear=exactly 1 IV; multiple=≥2 IVs (default if unspecified). "
                     "composite index = weighted ≥2 sub-metrics predicting/normalising energy — "
                     "NOT MCDM/AHP/TOPSIS (those → A11b). ‘not applicable’ mutually exclusive."},
            {"name": "complementary_methodologies", "type": "multienum",
             "options": ["pinch analysis", "exergy analysis", "thermodynamic modelling",
                         "process flowsheet simulation", "ML ensemble",
                         "multi-criteria decision-making (MCDM/AHP/TOPSIS/Fuzzy)", "none"],
             "label": "Complementary methodologies (A11b)"},
        ],
    },
    "level_b": {
        "title": "Level B (§6.2) — fill ONLY if Level 3B = true",
        "fields": [
            {"name": "normalisation_variables", "type": "list_str",
             "label": "Normalisation variables (B1)",
             "help": "Independent variables only. EXCLUDE the dependent variable (energy use)."},
            {"name": "baseline_period_start", "type": "text", "label": "Baseline start (B2a)",
             "help": "e.g. 2018-01; ‘not reported’ if absent."},
            {"name": "baseline_period_end", "type": "text", "label": "Baseline end (B2b)",
             "help": "e.g. 2019-12; ‘not reported’ if absent."},
            {"name": "baseline_construction_method", "type": "textarea",
             "label": "Baseline construction method (B2c)", "help": "1–3 sentences."},
            {"name": "validation_types", "type": "multienum",
             "options": ["empirical", "simulation", "theoretical", "statistical",
                         "none reported"],
             "label": "Validation types (B3)",
             "help": "statistical = any inferential test of fit/significance "
                     "(R², p, F, t, χ², AIC/BIC, cross-val, residual analysis)."},
            {"name": "scale_of_application", "type": "enum",
             "options": ["equipment", "sub-system / utility system", "unit",
                         "facility", "organisation"],
             "label": "Scale of application (B4)"},
            {"name": "scope_description", "type": "textarea",
             "label": "Scope description (B4b)",
             "help": "e.g. ‘water-steam circuit of the SAP plant’. Driver/audit annotations "
                     "go HERE, not in data_type."},
            {"name": "identifies_model_limitations", "type": "bool",
             "label": "Identifies MODEL limitations (B5)",
             "help": "Limitations of the EnPI/EnB MODEL ITSELF (applicability bounds, residual "
                     "issues, validation gaps). NOT operational barriers (→ B14)."},
            {"name": "specific_limitations", "type": "multienum", "other": True,
             "options": ["non-stationarity", "fouling", "catalyst deactivation",
                         "feedstock variability"],
             "label": "Specific limitations (B6)", "help": "Empty if B5 = false."},
            {"name": "proposes_treatment_mechanism", "type": "bool",
             "label": "Proposes treatment mechanism (B7)"},
            {"name": "proposes_adaptations", "type": "bool",
             "label": "Proposes adaptations (B8)",
             "help": "CONCRETE methodological adaptations for continuous-process application."},
            {"name": "adaptation_types", "type": "multienum", "other": True,
             "options": ["dynamic time window", "segmented baseline", "hybrid physical model"],
             "label": "Adaptation types (B9)", "help": "Empty if B8 = false."},
            {"name": "normative_framing_of_adaptations", "type": "enum",
             "options": ["ISO 50001/50006 explicit", "implicit", "absent"],
             "label": "Normative framing of adaptations (B10)"},
            {"name": "empirical_refinery_application", "type": "bool",
             "label": "Empirical refinery/petrochem application (B11)",
             "help": "Empirically applied to a real refinery/petrochem plant (not future case)."},
            {"name": "data_type", "type": "enum",
             "options": ["continuous time series", "audit data", "simulation",
                         "unspecified or not stated"],
             "label": "Data type (B12)", "help": "STRICT enum — no free-form suffixes."},
            {"name": "model_parameters_reported", "type": "list_str",
             "label": "Model parameters reported (B13a)",
             "help": "Fitted coefficients, intercepts, dummy coefficients. NOT goodness-of-fit."},
            {"name": "performance_metrics_reported", "type": "list_obj",
             "label": "Performance metrics reported (B13b)",
             "item_fields": [
                 {"name": "metric", "type": "enum",
                  "options": ["R²", "adjusted R²", "RMSE", "MAE", "MAPE", "CV-RMSE",
                              "% energy savings", "F-statistic", "p-value", "other-named"]},
                 {"name": "value", "type": "text"},
                 {"name": "unit", "type": "text"},
                 {"name": "period_or_context", "type": "text"},
             ],
             "help": "Goodness-of-fit metrics, NOT model parameters. Empty if none."},
            {"name": "implementation_barriers", "type": "list_str",
             "label": "Implementation barriers (B14)",
             "help": "Practical/operational obstacles. NOT model limitations (→ B5). "
                     "Ambiguous → default here (broader category)."},
        ],
    },
}


# Merge canonical mechanics onto presentation-only rows. This deliberately
# removes the legacy free-text ``other`` switch: ``other`` and ``other-named``
# are literal registered values, exactly as emitted by the model prompts.
for _section, _section_spec in SCHEMA.items():
    for _field in _section_spec["fields"]:
        _projection = reviewer_field_contract(_section, _field["name"])
        for _mechanical_key in ("type", "options", "item_fields", "other"):
            _field.pop(_mechanical_key, None)
        _field.update(_projection)
