import json

import pytest

from pack_builder import build_workspaces
from run_initializer import InitializationError, initialize_run
from test_pack_builder import REVISIONS, _fixture_root


def test_run_initializer_records_surface_provenance_atomically_and_is_idempotent(tmp_path):
    root = _fixture_root(tmp_path, filed=False, n_proceeding=2)
    build_workspaces(
        root,
        development=True,
        revisions=REVISIONS,
        queue_keys=["rayyan-1", "rayyan-2"],
    )
    workspace = root / "production" / "chatgpt"
    result = initialize_run(
        workspace,
        run_id="repilot-chatgpt-001",
        executor="chatgpt",
        app_version="Codex 1.2.3",
        model_label="GPT-5",
        started_at="2026-07-14T12:00:00+01:00",
    )
    assert result["initialized"] is True
    metadata = json.loads((workspace / "run_metadata.json").read_text())
    assert metadata["run"]["executor"] == "chatgpt"
    assert metadata["execution_surfaces"]["chatgpt"]["model_label"] == "GPT-5"
    assert initialize_run(
        workspace,
        run_id="repilot-chatgpt-001",
        executor="chatgpt",
        app_version="Codex 1.2.3",
        model_label="GPT-5",
        started_at="2026-07-14T12:00:00+01:00",
    )["initialized"] is False
    with pytest.raises(InitializationError, match="already initialized"):
        initialize_run(
            workspace,
            run_id="different",
            executor="chatgpt",
            app_version="Codex 1.2.3",
            model_label="GPT-5",
        )


def test_run_initializer_rejects_executor_workspace_mismatch(tmp_path):
    root = _fixture_root(tmp_path, filed=False)
    build_workspaces(root, development=True, revisions=REVISIONS)
    with pytest.raises(InitializationError, match="does not match"):
        initialize_run(
            root / "production" / "chatgpt",
            run_id="bad",
            executor="claude",
            app_version="Claude 1",
            model_label="Claude",
        )
