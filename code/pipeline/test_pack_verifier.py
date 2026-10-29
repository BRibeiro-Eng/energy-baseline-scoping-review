import json

import pytest

from pack_builder import build_workspaces
from pack_verifier import VerificationError, verify_twin_packs, verify_workspace
from test_pack_builder import REVISIONS, _fixture_root


def _built(tmp_path, *, filed=False):
    root = _fixture_root(tmp_path, filed=filed)
    build_workspaces(root, development=not filed, revisions=REVISIONS)
    return root


def test_verifier_accepts_untampered_development_pack_and_reports_gate(tmp_path):
    root = _built(tmp_path, filed=False)
    report = verify_workspace(root / "production" / "chatgpt")
    assert report["ok"] is True
    assert report["production_ready"] is False
    assert "reviewer_gate.c23_signoff_date" in report["runtime_blockers"]


def test_verifier_rejects_immutable_file_drift(tmp_path):
    root = _built(tmp_path)
    protocol = root / "production" / "chatgpt" / "PROTOCOL.md"
    protocol.write_text("tampered\n")
    with pytest.raises(VerificationError, match="hash mismatch"):
        verify_workspace(root / "production" / "chatgpt")


def test_verifier_rejects_unmanifested_immutable_file(tmp_path):
    root = _built(tmp_path)
    rogue = root / "production" / "chatgpt" / "prompts" / "unregistered.md"
    rogue.write_text("not in immutable manifest\n")
    with pytest.raises(VerificationError, match="unmanifested immutable"):
        verify_workspace(root / "production" / "chatgpt")


def test_verifier_ignores_python_runtime_cache_files(tmp_path):
    root = _built(tmp_path)
    cache = root / "production" / "chatgpt" / "scripts" / "__pycache__" / "module.pyc"
    cache.parent.mkdir()
    cache.write_bytes(b"runtime cache")
    assert verify_workspace(root / "production" / "chatgpt")["ok"] is True


def test_verifier_rejects_canonical_link_drift(tmp_path):
    root = _built(tmp_path)
    link = root / "production" / "chatgpt" / "inputs" / "pdfs"
    link.unlink()
    link.symlink_to(root / "prompts", target_is_directory=True)
    with pytest.raises(VerificationError, match="input link mismatch"):
        verify_workspace(root / "production" / "chatgpt")


def test_twin_verifier_requires_equal_immutable_manifests(tmp_path):
    root = _built(tmp_path)
    report = verify_twin_packs(root / "production")
    assert report["equal_manifests"] is True
    lock = root / "production" / "claude" / "PACK_LOCK.json"
    data = json.loads(lock.read_text())
    data["immutable_manifest_sha256"] = "0" * 64
    lock.write_text(json.dumps(data))
    with pytest.raises(VerificationError, match="manifest"):
        verify_twin_packs(root / "production")


def test_require_production_rejects_fail_closed_runtime(tmp_path):
    root = _built(tmp_path, filed=False)
    with pytest.raises(VerificationError, match="production gate"):
        verify_workspace(root / "production" / "chatgpt", require_production=True)
