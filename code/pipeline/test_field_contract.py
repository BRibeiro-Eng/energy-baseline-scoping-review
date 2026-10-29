import json
from pathlib import Path

from jsonschema import Draft202012Validator

from field_contract import (
    STAGE1_FIELDS,
    STAGE2_FIELDS,
    STAGE3_FIELDS,
    build_article_output_schema,
    build_stage3_supplement_schema,
    contract_sha256,
    reviewer_field_contract,
)


VALID_VALUES = {
    "stage1": {
        "methodological_eligibility": True,
        "ineligibility_reason": None,
        "borderline_review_synthesis_eligibility": False,
        "paper_type": "single applied case",
        "level_3b": True,
        "notes": None,
    },
    "stage2": {
        "multi_site": True,
        "country_region": "Italy",
        "sector_of_activity": "industrial gases",
        "type_of_organisation": "continuous process",
        "ems_standard": ["ISO 50001"],
        "mv_protocol": ["none"],
        "regulatory_driver": ["EU EED"],
        "enpi_enb_model_types": ["linear regression"],
        "complementary_methodologies": ["none"],
    },
    "stage3": {
        "normalisation_variables": ["production"],
        "baseline_period_start": "2022",
        "baseline_period_end": "2022",
        "baseline_construction_method": "linear regression",
        "validation_types": ["statistical"],
        "scale_of_application": "facility",
        "scope_description": "site-level model",
        "identifies_model_limitations": True,
        "specific_limitations": ["other"],
        "proposes_treatment_mechanism": True,
        "proposes_adaptations": True,
        "adaptation_types": ["segmented baseline"],
        "normative_framing_of_adaptations": "absent",
        "empirical_refinery_application": False,
        "data_type": "audit data",
        "model_parameters_reported": ["slope=1"],
        "performance_metrics_reported": [
            {
                "metric": "R²",
                "value": "0.736",
                "unit": None,
                "period_or_context": "2022",
                "evidence_quote": "R2 0.736",
                "page": 1,
            }
        ],
        "implementation_barriers": [],
    },
}


ENUM_FIELDS = {
    ("stage1", "paper_type"),
    ("stage2", "type_of_organisation"),
    ("stage2", "ems_standard"),
    ("stage2", "mv_protocol"),
    ("stage2", "regulatory_driver"),
    ("stage2", "enpi_enb_model_types"),
    ("stage2", "complementary_methodologies"),
    ("stage3", "validation_types"),
    ("stage3", "scale_of_application"),
    ("stage3", "specific_limitations"),
    ("stage3", "adaptation_types"),
    ("stage3", "normative_framing_of_adaptations"),
    ("stage3", "data_type"),
}


def _envelope(value):
    return {
        "value": value,
        "evidence_quote": "not found in source",
        "page": None,
        "non_contiguous_evidence": False,
        "confidence": None,
    }


def _field_schema(schema, section, field):
    return schema["$defs"][f"{section}Object"]["properties"][field]


def test_registry_covers_every_frozen_field_in_order():
    assert tuple(STAGE1_FIELDS) == tuple(VALID_VALUES["stage1"])
    assert tuple(STAGE2_FIELDS) == tuple(VALID_VALUES["stage2"])
    assert tuple(STAGE3_FIELDS) == tuple(VALID_VALUES["stage3"])


def test_every_field_accepts_its_canonical_value_and_rejects_an_object():
    schema = build_article_output_schema()
    for section, values in VALID_VALUES.items():
        for field, value in values.items():
            field_schema = _field_schema(schema, section, field)
            candidate = value if section == "stage1" and field in {
                "ineligibility_reason", "borderline_review_synthesis_eligibility", "notes"
            } else _envelope(value)
            assert not list(Draft202012Validator(field_schema).iter_errors(candidate)), (
                section, field
            )
            assert list(Draft202012Validator(field_schema).iter_errors({"bad": True})), (
                section, field
            )


def test_every_enum_or_multienum_rejects_unknown_values():
    schema = build_article_output_schema()
    for section, field in sorted(ENUM_FIELDS):
        field_schema = _field_schema(schema, section, field)
        canonical = VALID_VALUES[section][field]
        bad_value = ["NOT-IN-CONTRACT"] if isinstance(canonical, list) else "NOT-IN-CONTRACT"
        assert list(Draft202012Validator(field_schema).iter_errors(_envelope(bad_value))), (
            section, field
        )


def test_b13b_requires_nested_evidence_and_rejects_unknown_properties():
    schema = build_article_output_schema()
    field_schema = _field_schema(schema, "stage3", "performance_metrics_reported")
    valid = _envelope(VALID_VALUES["stage3"]["performance_metrics_reported"])
    assert not list(Draft202012Validator(field_schema).iter_errors(valid))

    missing_page = json.loads(json.dumps(valid))
    missing_page["value"][0].pop("page")
    assert list(Draft202012Validator(field_schema).iter_errors(missing_page))

    unknown = json.loads(json.dumps(valid))
    unknown["value"][0]["nonsense"] = 42
    assert list(Draft202012Validator(field_schema).iter_errors(unknown))


def test_stage3_supplement_uses_the_identical_stage3_contract():
    article = build_article_output_schema()
    supplement = build_stage3_supplement_schema()
    assert supplement["properties"]["stage3"] == article["properties"]["stage3"]


def test_reviewer_projection_uses_prompt_vocabulary_and_value_only_b13b():
    assert reviewer_field_contract("level_a", "enpi_enb_model_types")["options"][:2] == [
        "linear regression", "multiple regression"
    ]
    assert "other-named" in reviewer_field_contract("level_a", "ems_standard")["options"]
    assert reviewer_field_contract("level_b", "specific_limitations")["options"][-1] == "other"
    metric = reviewer_field_contract("level_b", "performance_metrics_reported")
    assert [item["name"] for item in metric["item_fields"]] == [
        "metric", "value", "unit", "period_or_context"
    ]


def test_contract_hash_is_stable_sha256_over_canonical_schema():
    first = contract_sha256()
    second = contract_sha256()
    assert first == second
    assert len(first) == 64
    int(first, 16)


def test_frozen_prompts_contain_every_registered_controlled_string():
    root = Path(__file__).resolve().parent.parent
    prompt_by_stage = {
        "stage1": (root / "prompts" / "stage1_system.md").read_text(encoding="utf-8"),
        "stage2": (root / "prompts" / "stage2_system.md").read_text(encoding="utf-8"),
        "stage3": (root / "prompts" / "stage3_system.md").read_text(encoding="utf-8"),
    }
    for stage, fields in (
        ("stage1", STAGE1_FIELDS),
        ("stage2", STAGE2_FIELDS),
        ("stage3", STAGE3_FIELDS),
    ):
        for field, definition in fields.items():
            value_schema = definition.get("value_schema") or {}
            options = value_schema.get("enum")
            if options is None and value_schema.get("type") == "array":
                options = (value_schema.get("items") or {}).get("enum")
            for option in options or []:
                if isinstance(option, str):
                    assert option in prompt_by_stage[stage], (stage, field, option)
    assert "each object has its own evidence_quote" in prompt_by_stage["stage3"]


def test_protocol_documents_model_and_human_b13b_representations():
    protocol = (Path(__file__).resolve().parent.parent / "PROTOCOL.md").read_text(
        encoding="utf-8"
    )
    assert "v2.2.1 enforcement erratum (2026-07-14" in protocol
    assert "metric`, `value`, `unit`, `period_or_context`,\n`evidence_quote`, and `page`" in protocol
    assert "stored\nseparately in `reviewer_evidence`" in protocol
