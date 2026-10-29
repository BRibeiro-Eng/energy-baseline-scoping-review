import json
from pathlib import Path

import pytest

from batch_controller import (
    BatchError,
    approve_proposal,
    finalize_active_batch,
    propose_batch,
    recover_active_batch,
    workspace_status,
)
from pack_builder import build_workspaces
from test_output_validator import _record
from test_pack_builder import REVISIONS, _fixture_root
from run_initializer import initialize_run


def _workspace(tmp_path):
    root = _fixture_root(tmp_path, filed=False)
    build_workspaces(root, development=True, revisions=REVISIONS)
    return root / "production" / "chatgpt"


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_propose_defaults_to_five_or_remaining_and_does_not_activate(tmp_path):
    workspace = _workspace(tmp_path)
    proposal = propose_batch(workspace)
    assert proposal["keys"] == ["rayyan-1"]
    assert proposal["requested_size"] == 5
    status = workspace_status(workspace)
    assert status["proposed_batch"]["batch_id"] == proposal["batch_id"]
    assert status["active_batch"] is None


def test_approval_is_blocked_by_runtime_gate_unless_fixture_mode_is_explicit(tmp_path):
    workspace = _workspace(tmp_path)
    proposal = propose_batch(workspace, size=1)
    with pytest.raises(BatchError, match="production gate"):
        approve_proposal(workspace, proposal["batch_id"], authorized_by="Bernardo")
    active = approve_proposal(
        workspace, proposal["batch_id"], authorized_by="fixture", fixture=True
    )
    assert active["status"] == "active"
    with pytest.raises(BatchError, match="active batch"):
        propose_batch(workspace, size=1)


def test_valid_attempt_is_promoted_and_batch_stops_completed(tmp_path):
    workspace = _workspace(tmp_path)
    proposal = propose_batch(workspace, size=1)
    approve_proposal(workspace, proposal["batch_id"], authorized_by="fixture", fixture=True)
    raw = workspace / "outputs" / "raw" / "rayyan-1.attempt-01.json"
    _write_json(raw, _record())

    result = finalize_active_batch(workspace, fixture=True)
    assert result["status"] == "completed"
    assert result["completed"] == ["rayyan-1"]
    assert (workspace / "outputs" / "validated" / "rayyan-1.json").is_file()
    assert raw.is_file()
    status = workspace_status(workspace)
    assert status["active_batch"] is None
    assert status["completed_keys"] == ["rayyan-1"]
    assert status["proposed_batch"] is None


def test_invalid_first_attempt_requires_targeted_repair_then_accepts_attempt_two(tmp_path):
    workspace = _workspace(tmp_path)
    proposal = propose_batch(workspace, size=1)
    approve_proposal(workspace, proposal["batch_id"], authorized_by="fixture", fixture=True)
    broken = _record()
    broken["stage2"] = None
    _write_json(workspace / "outputs" / "raw" / "rayyan-1.attempt-01.json", broken)

    first = finalize_active_batch(workspace, fixture=True)
    assert first["status"] == "repair_required"
    assert first["repair_required"] == ["rayyan-1"]
    assert recover_active_batch(workspace)["status"] == "repair_required"

    repaired = _record()
    repaired["attempt"] = 2
    _write_json(workspace / "outputs" / "raw" / "rayyan-1.attempt-02.json", repaired)
    second = finalize_active_batch(workspace, fixture=True)
    assert second["status"] == "completed"
    accepted = json.loads((workspace / "outputs" / "validated" / "rayyan-1.json").read_text())
    assert accepted["attempt"] == 2


def test_invalid_second_attempt_is_quarantined_and_not_promoted(tmp_path):
    workspace = _workspace(tmp_path)
    proposal = propose_batch(workspace, size=1)
    approve_proposal(workspace, proposal["batch_id"], authorized_by="fixture", fixture=True)
    for attempt in (1, 2):
        broken = _record()
        broken["attempt"] = attempt
        broken["stage2"] = None
        _write_json(
            workspace / "outputs" / "raw" / f"rayyan-1.attempt-{attempt:02d}.json",
            broken,
        )
    result = finalize_active_batch(workspace, fixture=True)
    assert result["status"] == "completed_with_failures"
    assert result["failed"] == ["rayyan-1"]
    assert not (workspace / "outputs" / "validated" / "rayyan-1.json").exists()
    assert (workspace / "outputs" / "quarantine" / "rayyan-1.json").is_file()


def test_size_ten_requires_two_green_batches(tmp_path):
    root = _fixture_root(tmp_path, filed=False, n_proceeding=11)
    build_workspaces(root, development=True, revisions=REVISIONS)
    workspace = root / "production" / "chatgpt"
    state = workspace / "state"
    with pytest.raises(BatchError, match="two consecutive green"):
        propose_batch(workspace, size=10)
    for n in (1, 2):
        _write_json(state / "batches" / f"batch-{n:04d}.json", {"status": "completed", "green": True})
    proposal = propose_batch(workspace, size=10)
    assert len(proposal["keys"]) == 10


def test_real_repilot_bypass_is_limited_to_a_development_subset(tmp_path):
    root = _fixture_root(tmp_path, filed=False, n_proceeding=3)
    build_workspaces(
        root,
        development=True,
        revisions=REVISIONS,
        queue_keys=["rayyan-1", "rayyan-2"],
    )
    workspace = root / "production" / "chatgpt"
    initialize_run(
        workspace,
        run_id="repilot-chatgpt",
        executor="chatgpt",
        app_version="Codex test",
        model_label="GPT test",
    )
    proposal = propose_batch(workspace)
    active = approve_proposal(
        workspace,
        proposal["batch_id"],
        authorized_by="Bernardo",
        repilot=True,
    )
    assert active["repilot_mode"] is True

    full_root = _fixture_root(tmp_path / "full", filed=False, n_proceeding=2)
    build_workspaces(full_root, development=True, revisions=REVISIONS)
    full = full_root / "production" / "chatgpt"
    full_proposal = propose_batch(full)
    with pytest.raises(BatchError, match="subset"):
        approve_proposal(
            full,
            full_proposal["batch_id"],
            authorized_by="Bernardo",
            repilot=True,
        )
