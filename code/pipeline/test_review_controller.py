import json
from pathlib import Path

import pytest

from pack_builder import build_workspaces
from review_controller import (
    ReviewError,
    corpus_b_branch,
    import_validated_outputs,
    lock_corpus_b_roster,
    reconcile_imports,
    select_level_b_assignments,
    materialize_review_assignments,
)
from supplement_controller import (
    approve_supplement_proposal,
    finalize_supplement_batch,
    plan_stage3_supplements,
    propose_supplement_batch,
)
from output_validator import STAGE3_FIELDS
from test_output_validator import STAGE3_VALUES, _env
from test_output_validator import _record
from test_pack_builder import REVISIONS, _fixture_root


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _set_key(record, key):
    record = json.loads(json.dumps(record))
    record["paper_key"] = key
    return record


def _setup(tmp_path):
    root = _fixture_root(tmp_path, filed=False, n_proceeding=3)
    build_workspaces(root, development=True, revisions=REVISIONS)
    production = root / "production"

    # key 1: both models agree true/true and both have Stage 3.
    for family in ("chatgpt", "claude"):
        _write_json(production / family / "outputs" / "validated" / "rayyan-1.json", _record())

    # key 2: ChatGPT says level_3b=false (therefore no Stage 3), Claude says true.
    chat2 = _set_key(_record(level_3b=False), "rayyan-2")
    claude2 = _set_key(_record(level_3b=True), "rayyan-2")
    _write_json(production / "chatgpt" / "outputs" / "validated" / "rayyan-2.json", chat2)
    _write_json(production / "claude" / "outputs" / "validated" / "rayyan-2.json", claude2)

    # key 3: both models agree false; it is not in Corpus B.
    for family in ("chatgpt", "claude"):
        _write_json(
            production / family / "outputs" / "validated" / "rayyan-3.json",
            _set_key(_record(level_3b=False), "rayyan-3"),
        )
    return root, production, production / "reviewer_workspace"


def test_import_and_reconcile_routes_membership_divergence(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    imported = import_validated_outputs(production)
    assert imported["chatgpt"] == 3
    assert imported["claude"] == 3
    result = reconcile_imports(reviewer)
    assert result["common_keys"] == 3
    queue = json.loads((reviewer / "queues" / "tier1_membership.json").read_text())
    assert {item["paper_key"] for item in queue} == {"rayyan-2"}
    assert {item["field"] for item in queue} == {"level_3b"}


def test_roster_lock_requires_membership_decision_and_closed_fn_census(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    with pytest.raises(ReviewError, match="missing human decision"):
        lock_corpus_b_roster(reviewer, decisions={}, fn_census={"closed": True}, version="B-v1")
    with pytest.raises(ReviewError, match="FN census is not closed"):
        lock_corpus_b_roster(
            reviewer,
            decisions={"rayyan-2": {"level_3b": True}},
            fn_census={"closed": False},
            version="B-v1",
        )


def test_locked_roster_drives_model_specific_supplements_without_rewriting_initial(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    receipt = lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": True}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    assert receipt["keys"] == ["rayyan-1", "rayyan-2"]
    assert "decisions" not in receipt
    assert "model" not in json.dumps(receipt).lower()

    chat_plan = plan_stage3_supplements(production / "chatgpt", receipt)
    claude_plan = plan_stage3_supplements(production / "claude", receipt)
    assert chat_plan["keys"] == ["rayyan-2"]
    assert claude_plan["keys"] == []
    original = json.loads(
        (production / "chatgpt" / "outputs" / "validated" / "rayyan-2.json").read_text()
    )
    assert original["stage1"]["level_3b"]["value"] is False
    assert original["stage3"] is None


def test_stage3_supplement_runs_as_separate_approved_batch(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    receipt = lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-2": {"level_3b": True}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-v1",
    )
    workspace = production / "chatgpt"
    plan = plan_stage3_supplements(workspace, receipt)
    proposal = propose_supplement_batch(workspace)
    assert proposal["keys"] == ["rayyan-2"]
    approve_supplement_proposal(
        workspace, proposal["batch_id"], authorized_by="fixture", fixture=True
    )
    item = plan["items"][0]
    raw = {
        "record_type": "stage3_supplement",
        "paper_key": "rayyan-2",
        "schema_version": "2.2.1",
        "validation_protocol": "C-2.3",
        "prompt_tag": "v2.3.1-operational",
        "roster_version": plan["roster_version"],
        "roster_receipt_sha256": plan["roster_receipt_sha256"],
        "initial_output_sha256": item["initial_output_sha256"],
        "attempt": 1,
        "completed_at": "2026-07-14T12:00:00+01:00",
        "stage3": {
            name: _env([] if name == "performance_metrics_reported" else STAGE3_VALUES[name])
            for name in STAGE3_FIELDS
        },
    }
    _write_json(
        workspace / "outputs" / "raw" / "rayyan-2.stage3-supplement.attempt-01.json",
        raw,
    )
    result = finalize_supplement_batch(workspace, fixture=True)
    assert result["status"] == "completed"
    assert (
        workspace / "outputs" / "validated" / "rayyan-2.stage3-supplement.json"
    ).is_file()
    initial = json.loads((workspace / "outputs" / "validated" / "rayyan-2.json").read_text())
    assert initial["stage1"]["level_3b"]["value"] is False
    assert initial["stage3"] is None


def test_import_is_immutable(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    source = production / "chatgpt" / "outputs" / "validated" / "rayyan-1.json"
    data = json.loads(source.read_text())
    data["completed_at"] = "changed"
    _write_json(source, data)
    with pytest.raises(ReviewError, match="immutable import differs"):
        import_validated_outputs(production)


def test_supplements_import_separately_and_never_enter_initial_reconciliation(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    supplement = {"record_type": "stage3_supplement", "paper_key": "rayyan-2"}
    _write_json(
        production / "chatgpt" / "outputs" / "validated"
        / "rayyan-2.stage3-supplement.json",
        supplement,
    )
    imported = import_validated_outputs(production)
    assert imported["chatgpt"] == 3
    assert (
        reviewer / "imports" / "chatgpt" / "supplements"
        / "rayyan-2.stage3-supplement.json"
    ).is_file()
    result = reconcile_imports(reviewer)
    assert result["common_keys"] == 3


@pytest.mark.parametrize(
    ("size", "name", "blind", "remainder", "paused"),
    [
        (0, "integral_blind_first", 0, 0, False),
        (25, "integral_blind_first", 25, 0, False),
        (26, "integral_blind_first", 26, 0, False),
        (40, "integral_blind_first", 40, 0, False),
        (41, "hybrid", 40, 1, False),
        (60, "hybrid", 40, 20, False),
        (61, "paused_over_60", 0, 61, True),
    ],
)
def test_corpus_b_branch_boundaries(size, name, blind, remainder, paused):
    branch = corpus_b_branch(size)
    assert branch["name"] == name
    assert branch["blind_first_n"] == blind
    assert branch["prefill_verification_n"] == remainder
    assert branch["paused"] is paused


def test_level_b_assignment_uses_priority_head_seeded_subsample_and_fallback():
    records = [
        {
            "key": f"rayyan-{number}",
            "sector_of_activity": (
                "petroleum refinery" if number == 1 else
                "petrochemical" if number == 2 else "cement"
            ),
            "year": 1990 + number,
        }
        for number in range(1, 42)
    ]
    plan = select_level_b_assignments(records)
    assert len(plan["blind_first_keys"]) == 40
    assert len(plan["verification_keys"]) == 1
    assert {"rayyan-1", "rayyan-2"} <= set(plan["priority_head_keys"])
    remaining = plan["verification_keys"][0]
    fallback = select_level_b_assignments(records, missing_comparison_keys=[remaining])
    assert remaining in fallback["blind_first_keys"]
    assert remaining in fallback["fallback_blind_keys"]
    assert fallback["verification_keys"] == []


def test_level_b_assignment_refuses_over_60_before_work():
    records = [{"key": f"rayyan-{number}", "sector_of_activity": "cement", "year": 2020}
               for number in range(1, 62)]
    with pytest.raises(ReviewError, match="paused"):
        select_level_b_assignments(records)


def test_materialized_review_templates_withhold_only_blind_targets(tmp_path):
    root, production, reviewer = _setup(tmp_path)
    import_validated_outputs(production)
    reconcile_imports(reviewer)
    result = materialize_review_assignments(
        reviewer,
        [
            {
                "paper_key": "rayyan-2",
                "phase": "blind",
                "review_fields": ["eligibility.level_3b"],
            },
            {
                "paper_key": "rayyan-1",
                "phase": "verification",
                "review_fields": ["level_a.country_region"],
            },
        ],
        canonical_root=root,
    )
    assert result["created"] == 2
    blind = json.loads((reviewer / "reviews" / "blind" / "rayyan-2.json").read_text())
    assert blind["eligibility"]["level_3b"] is None
    assert blind["eligibility"]["methodological_eligibility"] is True
    assert blind["_blind_required"] is True
    ai = json.loads((reviewer / "reviews" / "blind" / "rayyan-2.ai.json").read_text())
    assert set(ai["models"]) == {"chatgpt", "claude"}
    verification = json.loads(
        (reviewer / "reviews" / "verification" / "rayyan-1.json").read_text()
    )
    assert verification["_blind_required"] is False
    assert verification["level_a"]["country_region"] == "Italy"
