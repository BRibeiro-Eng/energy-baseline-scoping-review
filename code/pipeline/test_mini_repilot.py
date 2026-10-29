"""Seven-paper stored-fixture end-to-end mini-repilot (no model invocation)."""

import copy
import json

from batch_controller import (
    approve_proposal,
    finalize_active_batch,
    propose_batch,
    recover_active_batch,
)
from pack_builder import build_workspaces
from review_controller import (
    import_validated_outputs,
    lock_corpus_b_roster,
    materialize_review_assignments,
    reconcile_imports,
)
from stage4_consolidate import consolidate
from test_output_validator import _record
from test_pack_builder import REVISIONS, _fixture_root


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _keyed(record, key, *, attempt=1):
    value = copy.deepcopy(record)
    value["paper_key"] = key
    value["attempt"] = attempt
    return value


def _records(family):
    records = {
        "rayyan-1": _keyed(_record(level_3b=True), "rayyan-1"),       # Level B
        "rayyan-2": _keyed(_record(level_3b=False), "rayyan-2"),      # Level A
        "rayyan-3": _keyed(_record(eligible=False), "rayyan-3"),      # exclusion
        "rayyan-4": _keyed(_record(level_3b=False), "rayyan-4"),      # borderline
        "rayyan-5": _keyed(
            _record(level_3b=(family == "claude")), "rayyan-5"
        ),                                                               # divergence
        "rayyan-6": _keyed(_record(level_3b=False), "rayyan-6"),
        "rayyan-7": _keyed(_record(level_3b=False), "rayyan-7"),
    }
    records["rayyan-4"]["stage1"]["borderline_review_synthesis_eligibility"] = True
    return records


def _run_pack(workspace, family):
    records = _records(family)
    first = propose_batch(workspace)
    assert len(first["keys"]) == 5
    approve_proposal(workspace, first["batch_id"], authorized_by="fixture", fixture=True)
    assert recover_active_batch(workspace)["status"] == "active"  # interrupted-session path
    for key in first["keys"]:
        record = records[key]
        if family == "chatgpt" and key == "rayyan-5":
            broken = copy.deepcopy(record)
            broken["stage2"] = None
            _write_json(workspace / "outputs" / "raw" / f"{key}.attempt-01.json", broken)
        else:
            _write_json(workspace / "outputs" / "raw" / f"{key}.attempt-01.json", record)
    result = finalize_active_batch(workspace, fixture=True)
    if family == "chatgpt":
        assert result["repair_required"] == ["rayyan-5"]
        repaired = _keyed(records["rayyan-5"], "rayyan-5", attempt=2)
        _write_json(workspace / "outputs" / "raw" / "rayyan-5.attempt-02.json", repaired)
        result = finalize_active_batch(workspace, fixture=True)
    assert result["status"] == "completed"

    second = propose_batch(workspace)
    assert len(second["keys"]) == 2
    approve_proposal(workspace, second["batch_id"], authorized_by="fixture", fixture=True)
    for key in second["keys"]:
        _write_json(workspace / "outputs" / "raw" / f"{key}.attempt-01.json", records[key])
    assert finalize_active_batch(workspace, fixture=True)["status"] == "completed"


def test_seven_paper_end_to_end_fixture_mini_repilot(tmp_path):
    root = _fixture_root(tmp_path, filed=False, n_proceeding=7)
    build_workspaces(root, development=True, revisions=REVISIONS)
    production = root / "production"
    for family in ("chatgpt", "claude"):
        _run_pack(production / family, family)

    reviewer = production / "reviewer_workspace"
    assert import_validated_outputs(production) == {"chatgpt": 7, "claude": 7}
    reconciliation = reconcile_imports(reviewer)
    assert reconciliation["common_keys"] == 7
    receipt = lock_corpus_b_roster(
        reviewer,
        decisions={"rayyan-5": {"level_3b": False}},
        fn_census={"closed": True, "confirmed_corpus_b_keys": []},
        version="B-fixture-v1",
    )
    assert receipt["keys"] == ["rayyan-1"]

    materialize_review_assignments(
        reviewer,
        [{
            "paper_key": "rayyan-5",
            "phase": "blind",
            "wave": "membership",
            "review_fields": ["eligibility.level_3b"],
        }],
        canonical_root=root,
    )
    review = reviewer / "reviews" / "membership" / "blind" / "rayyan-5.json"
    data = json.loads(review.read_text())
    data["eligibility"]["level_3b"] = False
    data["reviewer_evidence"] = {
        "eligibility.level_3b": {
            "quote": "baseline model", "page": 1, "rule": "closed-sector rule"
        }
    }
    data["_done"] = True
    _write_json(review, data)
    _write_json(
        review.with_name("rayyan-5.blind.json"),
        {"key": "rayyan-5", "level_3b": False, "committed_at": "2026-07-14T12:00:00+01:00"},
    )
    _write_json(
        review.with_name("rayyan-5.state.json"),
        {"key": "rayyan-5", "state": "finalised", "finalised_at": "2026-07-14T12:01:00+01:00"},
    )
    result = consolidate(reviewer, canonical_root=root)
    assert result["records"] == 7
    assert result["unresolved_fields"] == 0
    assert (reviewer / "reports" / "final" / "merged.csv").is_file()
    assert (production / "chatgpt" / "outputs" / "raw" / "rayyan-5.attempt-01.json").is_file()
    assert (production / "chatgpt" / "outputs" / "raw" / "rayyan-5.attempt-02.json").is_file()
