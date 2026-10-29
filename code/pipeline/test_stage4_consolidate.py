import json

from review_controller import import_validated_outputs, lock_corpus_b_roster, reconcile_imports
from stage4_consolidate import consolidate
from test_review_controller import _setup, _write_json


def test_stage4_uses_finalised_human_membership_and_filters_level_b(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    receipt = lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": False}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    assert receipt["keys"] == ["rayyan-1"]

    review = {
        "key": "rayyan-2",
        "_phase": "blind",
        "_review_fields": ["eligibility.level_3b"],
        "eligibility": {"level_3b": False},
        "level_a": {},
        "level_b": {},
        "reviewer_notes": "membership adjudication",
        "reviewer_evidence": {
            "eligibility.level_3b": {
                "quote": "baseline model",
                "page": 1,
                "rule": "closed-sector membership rule",
            }
        },
        "_done": True,
    }
    review_path = reviewer / "reviews" / "blind" / "rayyan-2.json"
    _write_json(review_path, review)
    _write_json(
        reviewer / "reviews" / "blind" / "rayyan-2.state.json",
        {"key": "rayyan-2", "state": "finalised", "finalised_at": "2026-07-14T12:00:00+01:00"},
    )

    result = consolidate(reviewer, canonical_root=root)
    assert result["records"] == 3
    assert result["unresolved_fields"] == 0
    merged = json.loads((reviewer / "reports" / "final" / "merged.json").read_text())
    paper2 = next(row for row in merged if row["key"] == "rayyan-2")
    assert paper2["eligibility"]["level_3b"] is False
    assert paper2["level_b"] is None
    assert paper2["provenance"]["eligibility.level_3b"]["selected_source"] == "human"
    lineage = json.loads((reviewer / "reports" / "final" / "stage4_lineage.json").read_text())
    assert lineage["roster_receipt_sha256"] == receipt["receipt_sha256"]
    assert lineage["input_sha256"]


def test_stage4_fails_closed_on_unresolved_divergence(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": False}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    try:
        consolidate(reviewer, canonical_root=root)
    except RuntimeError as exc:
        assert "unresolved" in str(exc)
    else:
        raise AssertionError("Stage 4 accepted an unresolved membership divergence")


def test_stage4_accepts_registered_human_absence_evidence(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    receipt = lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": False}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    assert receipt["keys"] == ["rayyan-1"]

    review = {
        "key": "rayyan-2",
        "_phase": "blind",
        "_review_fields": ["eligibility.level_3b"],
        "eligibility": {"level_3b": False},
        "level_a": {},
        "level_b": {},
        "reviewer_notes": "absence decision after full-text review",
        "reviewer_evidence": {
            "eligibility.level_3b": {
                "mode": "not_reported_after_full_text_review",
                "quote": None,
                "page": None,
                "rule": "No continuous-process application was found in the full text.",
            }
        },
        "_done": True,
    }
    review_path = reviewer / "reviews" / "blind" / "rayyan-2.json"
    _write_json(review_path, review)
    _write_json(
        reviewer / "reviews" / "blind" / "rayyan-2.state.json",
        {"key": "rayyan-2", "state": "finalised", "finalised_at": "2026-07-16T12:00:00+01:00"},
    )

    result = consolidate(reviewer, canonical_root=root)
    assert result["unresolved_fields"] == 0
    merged = json.loads((reviewer / "reports" / "final" / "merged.json").read_text())
    paper2 = next(row for row in merged if row["key"] == "rayyan-2")
    evidence = paper2["provenance"]["eligibility.level_3b"]["human_evidence"]
    assert evidence["mode"] == "not_reported_after_full_text_review"
    assert evidence["grounding"]["method"] == "human_full_text_absence_review"
    assert evidence["grounding"]["grounded"] is False


def _finalise_level_3b_false_review(reviewer):
    review = {
        "key": "rayyan-2",
        "_phase": "blind",
        "_review_fields": ["eligibility.level_3b"],
        "eligibility": {"level_3b": False},
        "level_a": {},
        "level_b": {},
        "reviewer_notes": "membership adjudication",
        "reviewer_evidence": {
            "eligibility.level_3b": {
                "quote": "baseline model",
                "page": 1,
                "rule": "closed-sector membership rule",
            }
        },
        "_done": True,
    }
    path = reviewer / "reviews" / "blind" / "rayyan-2.json"
    _write_json(path, review)
    _write_json(
        path.with_name("rayyan-2.state.json"),
        {"key": "rayyan-2", "state": "finalised", "finalised_at": "2026-07-20T12:00:00+01:00"},
    )


def test_stage4_applies_ineligible_structural_rules(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": False}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    _finalise_level_3b_false_review(reviewer)

    reasons = {
        "chatgpt": "No qualifying energy-performance model.",
        "claude": "No EnPI or energy-baseline model is identified or characterised.",
    }
    for family, country in (("chatgpt", "Italy"), ("claude", "United States")):
        path = reviewer / "imports" / family / "rayyan-3.json"
        record = json.loads(path.read_text())
        record["stage1"]["methodological_eligibility"]["value"] = False
        record["stage1"]["ineligibility_reason"] = reasons[family]
        record["stage2"]["country_region"]["value"] = country
        _write_json(path, record)

    result = consolidate(reviewer, canonical_root=root)
    assert result["unresolved_fields"] == 0
    merged = json.loads((reviewer / "reports" / "final" / "merged.json").read_text())
    paper = next(row for row in merged if row["key"] == "rayyan-3")
    assert all(value is None for value in paper["level_a"].values())
    assert paper["eligibility"]["ineligibility_reason"] == reasons["chatgpt"]
    assert paper["provenance"]["level_a.country_region"]["selected_source"] == (
        "structural_not_applicable"
    )
    reason_provenance = paper["provenance"]["eligibility.ineligibility_reason"]
    assert reason_provenance["selected_source"] == "model_narrative_precedence"
    assert reason_provenance["chatgpt"] == reasons["chatgpt"]
    assert reason_provenance["claude"] == reasons["claude"]


def test_stage4_keeps_eligible_level_a_divergence_unresolved(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": False}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    _finalise_level_3b_false_review(reviewer)
    claude = reviewer / "imports" / "claude" / "rayyan-1.json"
    record = json.loads(claude.read_text())
    record["stage2"]["country_region"]["value"] = "Portugal"
    _write_json(claude, record)

    try:
        consolidate(reviewer, canonical_root=root)
    except RuntimeError as exc:
        assert "1 unresolved" in str(exc)
    else:
        raise AssertionError("Stage 4 auto-resolved an eligible Level-A divergence")
    unresolved = json.loads((reviewer / "reports" / "final" / "unresolved.json").read_text())
    assert [(row["paper_key"], row["section"], row["field"]) for row in unresolved] == [
        ("rayyan-1", "level_a", "country_region")
    ]
