"""Tests for provenance_rotation — surface-segment rotation invariants."""
import json

import pytest

from provenance_rotation import RotationError, rotate_surface


def _pack(tmp_path, *, executor="chatgpt", surface=None, batches=None, active=None):
    ws = tmp_path / executor
    (ws / "state").mkdir(parents=True)
    (ws / "run_metadata.json").write_text(json.dumps({
        "execution_surfaces": {executor: surface if surface is not None else {
            "app_version": "26.715.72359",
            "model_label": "gpt-5.6-sol",
            "surface": "Codex/ChatGPT application (consumer subscription)",
        }},
        "run": {
            "executor": executor,
            "run_id": f"{executor}-test",
            "started_at": "2026-07-23T11:04:56+01:00",
            "batches": batches if batches is not None else [
                {"batch_id": "batch-0001", "completed_at": "2026-07-23T11:46:35+01:00"},
                {"batch_id": "batch-0052", "completed_at": "2026-08-21T10:23:33+01:00"},
            ],
        },
    }), encoding="utf-8")
    (ws / "state" / "active_batch.json").write_text(json.dumps(active), encoding="utf-8")
    (ws / "state" / "proposed_batch.json").write_text("null", encoding="utf-8")
    return ws


def _rotate(ws, **kw):
    args = {
        "executor": "chatgpt",
        "app_version": "26.818.41509",
        "model_label": "gpt-5.6-sol",
        "observed_at": "2026-08-24T12:00:00+01:00",
        "reason": "surface app update observed between run segments",
        "authorized_by": "Bernardo Ribeiro",
    }
    args.update(kw)
    return rotate_surface(ws, **args)


def test_seeds_segment_one_from_an_unsegmented_pack(tmp_path):
    ws = _pack(tmp_path)
    result = _rotate(ws)
    first, second = result["segments"]
    assert first["segment"] == 1
    assert first["app_version"] == "26.715.72359"
    assert first["opened_at"] == "2026-07-23T11:04:56+01:00"
    assert second["segment"] == 2
    assert second["app_version"] == "26.818.41509"


def test_closes_segment_one_at_the_last_finalized_batch(tmp_path):
    ws = _pack(tmp_path)
    closed = _rotate(ws)["closed"]
    assert closed["closed_at"] == "2026-08-21T10:23:33+01:00"
    assert closed["last_batch"] == "batch-0052"


def test_never_overwrites_the_recorded_version_of_a_closed_segment(tmp_path):
    ws = _pack(tmp_path)
    _rotate(ws)
    metadata = json.loads((ws / "run_metadata.json").read_text())
    segments = metadata["execution_surfaces"]["chatgpt"]["surface_segments"]
    assert segments[0]["app_version"] == "26.715.72359"
    assert metadata["execution_surfaces"]["chatgpt"]["app_version"] == "26.818.41509"


def test_scalar_tracks_the_open_segment_so_the_verifier_still_passes(tmp_path):
    ws = _pack(tmp_path)
    _rotate(ws)
    surface = json.loads((ws / "run_metadata.json").read_text())["execution_surfaces"]["chatgpt"]
    assert surface["app_version"] and surface["model_label"]
    open_segments = [s for s in surface["surface_segments"] if s["closed_at"] is None]
    assert len(open_segments) == 1
    assert (open_segments[0]["app_version"], open_segments[0]["model_label"]) == (
        surface["app_version"], surface["model_label"])


def test_unchanged_surface_is_a_no_op(tmp_path):
    ws = _pack(tmp_path)
    before = (ws / "run_metadata.json").read_text()
    result = _rotate(ws, app_version="26.715.72359")
    assert result["rotated"] is False
    assert (ws / "run_metadata.json").read_text() == before


def test_rotation_is_idempotent_across_repeated_calls(tmp_path):
    ws = _pack(tmp_path)
    _rotate(ws)
    after_first = (ws / "run_metadata.json").read_text()
    assert _rotate(ws)["rotated"] is False
    assert (ws / "run_metadata.json").read_text() == after_first


def test_reverting_to_an_earlier_surface_is_refused(tmp_path):
    ws = _pack(tmp_path)
    _rotate(ws)
    with pytest.raises(RotationError, match="already occupies segment 1"):
        _rotate(ws, app_version="26.715.72359", model_label="gpt-5.6-sol")


def test_active_batch_blocks_rotation(tmp_path):
    ws = _pack(tmp_path, active={"batch_id": "batch-0053", "keys": []})
    with pytest.raises(RotationError, match="active_batch.json is not null"):
        _rotate(ws)


def test_proposed_batch_blocks_rotation(tmp_path):
    ws = _pack(tmp_path)
    (ws / "state" / "proposed_batch.json").write_text('{"batch_id": "batch-0053"}', encoding="utf-8")
    with pytest.raises(RotationError, match="proposed_batch.json is not null"):
        _rotate(ws)


def test_executor_must_match_the_workspace_directory(tmp_path):
    ws = _pack(tmp_path, executor="chatgpt")
    with pytest.raises(RotationError, match="does not match workspace"):
        _rotate(ws, executor="claude")


def test_uninitialized_surface_is_refused(tmp_path):
    ws = _pack(tmp_path, surface={"app_version": None, "model_label": None})
    with pytest.raises(RotationError, match="not initialized"):
        _rotate(ws)


def test_reason_and_authorization_are_required(tmp_path):
    ws = _pack(tmp_path)
    with pytest.raises(RotationError, match="required"):
        _rotate(ws, reason="  ")
    with pytest.raises(RotationError, match="required"):
        _rotate(ws, authorized_by="")


def test_pack_with_no_batch_history_closes_at_run_start(tmp_path):
    ws = _pack(tmp_path, batches=[])
    closed = _rotate(ws)["closed"]
    assert closed["closed_at"] == "2026-07-23T11:04:56+01:00"
    assert closed["last_batch"] is None


# --- sync_open_segment ---------------------------------------------------

from provenance_rotation import sync_open_segment  # noqa: E402


def _rotated_pack(tmp_path, extra_batches=()):
    ws = _pack(tmp_path)
    _rotate(ws)
    metadata = json.loads((ws / "run_metadata.json").read_text())
    metadata["run"]["batches"].extend(extra_batches)
    (ws / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return ws


def test_sync_stamps_the_batches_finalized_after_the_segment_opened(tmp_path):
    ws = _rotated_pack(tmp_path, [
        {"batch_id": "batch-0053", "completed_at": "2026-08-24T13:49:55+01:00"},
        {"batch_id": "batch-0054", "completed_at": "2026-08-24T14:57:08+01:00"},
    ])
    segment = sync_open_segment(ws, executor="chatgpt")["segment"]
    assert (segment["first_batch"], segment["last_batch"]) == ("batch-0053", "batch-0054")
    assert segment["batches_in_segment"] == 2


def test_sync_never_claims_a_batch_from_the_closed_segment(tmp_path):
    ws = _rotated_pack(tmp_path, [
        {"batch_id": "batch-0053", "completed_at": "2026-08-24T13:49:55+01:00"},
    ])
    sync_open_segment(ws, executor="chatgpt")
    segments = json.loads((ws / "run_metadata.json").read_text(
        ))["execution_surfaces"]["chatgpt"]["surface_segments"]
    assert segments[0]["last_batch"] == "batch-0052"      # closed segment untouched
    assert segments[1]["first_batch"] == "batch-0053"


def test_sync_is_idempotent(tmp_path):
    ws = _rotated_pack(tmp_path, [
        {"batch_id": "batch-0053", "completed_at": "2026-08-24T13:49:55+01:00"},
    ])
    sync_open_segment(ws, executor="chatgpt")
    after = (ws / "run_metadata.json").read_text()
    assert sync_open_segment(ws, executor="chatgpt")["synced"] is False
    assert (ws / "run_metadata.json").read_text() == after


def test_sync_advances_last_batch_as_batches_accumulate(tmp_path):
    ws = _rotated_pack(tmp_path, [
        {"batch_id": "batch-0053", "completed_at": "2026-08-24T13:49:55+01:00"},
    ])
    sync_open_segment(ws, executor="chatgpt")
    metadata = json.loads((ws / "run_metadata.json").read_text())
    metadata["run"]["batches"].append(
        {"batch_id": "batch-0055", "completed_at": "2026-08-25T09:00:00+01:00"})
    (ws / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    segment = sync_open_segment(ws, executor="chatgpt")["segment"]
    assert (segment["first_batch"], segment["last_batch"]) == ("batch-0053", "batch-0055")


def test_sync_is_a_no_op_before_the_first_batch_of_the_segment(tmp_path):
    ws = _rotated_pack(tmp_path)
    result = sync_open_segment(ws, executor="chatgpt")
    assert result["synced"] is False
    assert "no batch finalized" in result["reason"]


def test_sync_on_an_unsegmented_pack_is_a_no_op(tmp_path):
    ws = _pack(tmp_path)
    assert sync_open_segment(ws, executor="chatgpt")["synced"] is False
