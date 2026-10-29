import copy

from output_validator import (
    STAGE2_FIELDS,
    STAGE3_FIELDS,
    validate_initial_output,
    validate_stage3_supplement,
)


STAGE2_VALUES = {
    "multi_site": True,
    "country_region": "Italy",
    "sector_of_activity": "industrial gases",
    "type_of_organisation": "continuous process",
    "ems_standard": ["ISO 50001"],
    "mv_protocol": ["none"],
    "regulatory_driver": ["EU EED"],
    "enpi_enb_model_types": ["linear regression"],
    "complementary_methodologies": ["none"],
}

STAGE3_VALUES = {
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
            "evidence_quote": "R2 was 0.736",
            "page": 2,
        }
    ],
    "implementation_barriers": [],
}


def _env(value=None, quote="not found in source", page=None, non_contiguous=False, confidence=None):
    return {
        "value": value,
        "evidence_quote": quote,
        "page": page,
        "non_contiguous_evidence": non_contiguous,
        "confidence": confidence,
    }


def _bundle():
    return {
        "key": "rayyan-1",
        "pdf": {
            "pages": [
                {"page": 1, "text": "This eligible study applies a baseline model in a petroleum refinery."},
                {"page": 2, "text": "The model uses production and temperature. R2 was 0.736."},
            ]
        },
    }


def _record(*, eligible=True, level_3b=True):
    stage1 = {
        "methodological_eligibility": _env(
            eligible, "eligible study applies a baseline model", 1, confidence=0.9
        ),
        "ineligibility_reason": None,
        "borderline_review_synthesis_eligibility": False,
        "paper_type": _env(
            "single applied case",
            "eligible study applies a baseline model" if eligible else "not applicable",
            1 if eligible else None,
            confidence=0.9 if eligible else None,
        ),
        "level_3b": _env(
            level_3b if eligible else False,
            "petroleum refinery" if eligible else "not applicable",
            1 if eligible else None,
            confidence=0.9 if eligible else None,
        ),
        "notes": None,
    }
    return {
        "record_type": "initial_extraction",
        "paper_key": "rayyan-1",
        "schema_version": "2.2.1",
        "validation_protocol": "C-2.3",
        "prompt_tag": "v2.3.1-operational",
        "attempt": 1,
        "completed_at": "2026-07-14T12:00:00+01:00",
        "stage1": stage1,
        "stage2": {name: _env(copy.deepcopy(STAGE2_VALUES[name])) for name in STAGE2_FIELDS}
        if eligible else None,
        "stage3": {name: _env(copy.deepcopy(STAGE3_VALUES[name])) for name in STAGE3_FIELDS}
        if eligible and level_3b else None,
    }


def test_valid_complete_level_b_output_passes():
    report = validate_initial_output(_record(), _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is True
    assert report["errors"] == []
    assert report["grounding"]["checked"] == 4


def test_eligible_record_requires_complete_stage2():
    record = _record()
    record["stage2"] = None
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert "stage2 is required when eligible" in report["errors"]


def test_level3_false_forbids_initial_stage3():
    record = _record(level_3b=False)
    record["stage3"] = {name: _env() for name in STAGE3_FIELDS}
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert "stage3 must be null when level_3b is false" in report["errors"]


def test_identity_and_attempt_are_bound_to_assignment():
    report = validate_initial_output(_record(), _bundle(), expected_key="rayyan-2", expected_attempt=2)
    assert report["valid"] is False
    assert "paper_key does not match assignment" in report["errors"]
    assert "attempt does not match assignment" in report["errors"]


def test_ungrounded_quote_invalidates_output():
    record = _record()
    record["stage1"]["level_3b"]["evidence_quote"] = "words absent from the source"
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any("stage1.level_3b: evidence is not grounded" in error for error in report["errors"])


def test_non_contiguous_quote_requires_aligned_page_list():
    record = _record()
    record["stage1"]["level_3b"].update({
        "evidence_quote": ["petroleum", "temperature"],
        "page": [1],
        "non_contiguous_evidence": True,
    })
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any("evidence_quote/page length mismatch" in error for error in report["errors"])


def test_invalid_paper_type_enum_is_rejected():
    record = copy.deepcopy(_record())
    record["stage1"]["paper_type"]["value"] = "made-up type"
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any("stage1.paper_type.value" in error for error in report["errors"])


def test_invalid_stage2_model_enum_is_rejected():
    record = copy.deepcopy(_record())
    record["stage2"]["enpi_enb_model_types"]["value"] = ["NOT-IN-CONTRACT"]
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any("stage2.enpi_enb_model_types" in error for error in report["errors"])


def test_invalid_stage3_boolean_is_rejected():
    record = copy.deepcopy(_record())
    record["stage3"]["empirical_refinery_application"]["value"] = "yes"
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any("stage3.empirical_refinery_application" in error for error in report["errors"])


def test_malformed_b13b_object_is_rejected():
    record = copy.deepcopy(_record())
    record["stage3"]["performance_metrics_reported"]["value"] = [{"nonsense": 42}]
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any("stage3.performance_metrics_reported" in error for error in report["errors"])


def test_ungrounded_nested_b13b_quote_invalidates_output():
    record = copy.deepcopy(_record())
    record["stage3"]["performance_metrics_reported"]["value"][0]["evidence_quote"] = (
        "words absent from the source"
    )
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any(
        "stage3.performance_metrics_reported.value[0]: evidence is not grounded" in error
        for error in report["errors"]
    )


def test_nested_b13b_non_contiguous_quote_requires_aligned_page_list():
    record = copy.deepcopy(_record())
    metric = record["stage3"]["performance_metrics_reported"]["value"][0]
    metric.update({
        "evidence_quote": ["R2", "0.736"],
        "page": [2],
        "non_contiguous_evidence": True,
    })
    report = validate_initial_output(record, _bundle(), expected_key="rayyan-1", expected_attempt=1)
    assert report["valid"] is False
    assert any(
        "stage3.performance_metrics_reported.value[0]: evidence_quote/page length mismatch"
        in error
        for error in report["errors"]
    )


def _supplement():
    return {
        "record_type": "stage3_supplement",
        "paper_key": "rayyan-1",
        "schema_version": "2.2.1",
        "validation_protocol": "C-2.3",
        "prompt_tag": "v2.3.1-operational",
        "roster_version": "B-v1",
        "roster_receipt_sha256": "a" * 64,
        "initial_output_sha256": "b" * 64,
        "attempt": 1,
        "completed_at": "2026-07-14T12:00:00+01:00",
        "stage3": {name: _env(copy.deepcopy(STAGE3_VALUES[name])) for name in STAGE3_FIELDS},
    }


def _supplement_plan():
    return {
        "blocked": False,
        "roster_version": "B-v1",
        "roster_receipt_sha256": "a" * 64,
        "authorized_keys": ["rayyan-1"],
        "items": [{"paper_key": "rayyan-1", "initial_output_sha256": "b" * 64}],
    }


def test_stage3_supplement_is_bound_to_roster_and_frozen_initial_output():
    report = validate_stage3_supplement(
        _supplement(), _bundle(), _supplement_plan(), expected_key="rayyan-1", expected_attempt=1
    )
    assert report["valid"] is True
    changed = _supplement()
    changed["initial_output_sha256"] = "c" * 64
    report = validate_stage3_supplement(
        changed, _bundle(), _supplement_plan(), expected_key="rayyan-1", expected_attempt=1
    )
    assert report["valid"] is False
    assert "initial output hash does not match supplement plan" in report["errors"]


def test_stage3_supplement_refuses_blocked_or_unauthorized_plan():
    plan = _supplement_plan()
    plan["blocked"] = True
    report = validate_stage3_supplement(
        _supplement(), _bundle(), plan, expected_key="rayyan-1", expected_attempt=1
    )
    assert report["valid"] is False
    assert "supplement plan is blocked" in report["errors"]


def test_stage3_supplement_checks_nested_b13b_grounding():
    record = _supplement()
    record["stage3"]["performance_metrics_reported"]["value"][0]["evidence_quote"] = "absent"
    report = validate_stage3_supplement(
        record, _bundle(), _supplement_plan(), expected_key="rayyan-1", expected_attempt=1
    )
    assert report["valid"] is False
    assert any(
        "stage3.performance_metrics_reported.value[0]: evidence is not grounded" in error
        for error in report["errors"]
    )
