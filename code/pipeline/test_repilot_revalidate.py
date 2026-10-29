import copy
import hashlib
import json

import pytest

from repilot_revalidate import (
    RevalidationError,
    audit_repilot,
    prepare_repairs,
    reconcile_strict_selected,
)
from test_output_validator import _bundle, _record


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_record(*, attempt=1):
    record = copy.deepcopy(_record())
    record["attempt"] = attempt
    record["stage3"]["performance_metrics_reported"]["value"] = []
    return record


def _pilot(tmp_path, *, invalid_attempt2=False):
    root = tmp_path / "level3_extraction"
    production = root / "production"
    _write_json(root / "config" / "REPILOT_7_KEYS.json", ["rayyan-1"])
    _write_json(root / "output" / "stage0" / "rayyan-1.json", _bundle())
    chat = production / "chatgpt" / "outputs" / "raw" / "rayyan-1.attempt-01.json"
    claude = production / "claude" / "outputs" / "raw" / "rayyan-1.attempt-01.json"
    _write_json(chat, _strict_record())
    malformed = _strict_record()
    malformed["stage3"]["performance_metrics_reported"]["value"] = [{"nonsense": 42}]
    _write_json(claude, malformed)
    for family in ("chatgpt", "claude"):
        _write_json(
            production / family / "outputs" / "validation_reports"
            / "rayyan-1.attempt-01.json",
            {"valid": True, "legacy": True},
        )
    if invalid_attempt2:
        second = copy.deepcopy(malformed)
        second["attempt"] = 2
        _write_json(
            production / "claude" / "outputs" / "raw" / "rayyan-1.attempt-02.json",
            second,
        )
    return root, production, chat, claude


def test_audit_is_immutable_and_repairs_only_the_failing_family(tmp_path):
    root, production, chat, claude = _pilot(tmp_path)
    before = {chat: _sha(chat), claude: _sha(claude)}

    ledger = audit_repilot(production, root)

    assert ledger["summary"]["green"] is False
    assert ledger["summary"]["expected_records"] == 2
    records = {(row["family"], row["paper_key"]): row for row in ledger["records"]}
    assert records[("chatgpt", "rayyan-1")]["selected_attempt"] == 1
    assert records[("claude", "rayyan-1")]["selected_attempt"] is None
    assert len(records[("chatgpt", "rayyan-1")]["original_artifacts"]["validation_report_sha256"]) == 64
    assert set(ledger["source_revisions"]) == {"documentation_commit", "code_commit"}
    assert {_sha(path) for path in before} == set(before.values())

    prepared = prepare_repairs(production, ledger)
    assert prepared["created"] == 1
    assert prepared["instructions"][0]["family"] == "claude"
    assert not (production / "chatgpt" / "state" / "control_inbox" / "rayyan-1.strict-repair.json").exists()
    instruction = production / "claude" / "state" / "control_inbox" / "rayyan-1.strict-repair.json"
    assert instruction.is_file()
    assert json.loads(instruction.read_text())["prior_raw_sha256"] == before[claude]

    _write_json(
        production / "claude" / "outputs" / "raw" / "rayyan-1.attempt-02.json",
        _strict_record(attempt=2),
    )
    repaired = audit_repilot(production, root)
    repaired_records = {
        (row["family"], row["paper_key"]): row for row in repaired["records"]
    }
    assert repaired["summary"]["green"] is True
    assert repaired_records[("claude", "rayyan-1")]["selected_attempt"] == 2
    strict_report = (
        production / "claude" / "outputs" / "validation_reports"
        / "rayyan-1.attempt-02.strict-revalidation.json"
    )
    assert json.loads(strict_report.read_text())["valid"] is True
    assert all(_sha(path) == digest for path, digest in before.items())

    reconciliation = reconcile_strict_selected(production, repaired)
    assert reconciliation["summary"] == {
        "common_keys": 1,
        "compared": 31,
        "concordant": 31,
        "divergent": 0,
        "tier1": {"compared": 4, "concordant": 4, "divergent": 0},
        "tier2": {"compared": 18, "concordant": 18, "divergent": 0},
        "tier3": {"compared": 9, "concordant": 9, "divergent": 0},
    }
    namespace = production / "reviewer_workspace" / "strict_revalidation"
    assert (namespace / "imports" / "claude" / "rayyan-1.json").is_file()


def test_invalid_attempt2_is_terminal_and_cannot_receive_a_third_attempt(tmp_path):
    root, production, _, _ = _pilot(tmp_path, invalid_attempt2=True)
    ledger = audit_repilot(production, root)
    assert ledger["summary"]["green"] is False
    with pytest.raises(RevalidationError, match="attempt 2 already exists"):
        prepare_repairs(production, ledger)


def test_audit_emits_value_blind_markdown_and_machine_ledger(tmp_path):
    root, production, _, _ = _pilot(tmp_path)
    ledger = audit_repilot(production, root)
    reports = production / "reviewer_workspace" / "reports"
    assert (reports / "repilot_strict_revalidation.json").is_file()
    summary = (reports / "repilot_strict_revalidation.md").read_text()
    assert "claude / rayyan-1" in summary
    assert "nonsense" not in summary
    assert ledger["contract_sha256"] in summary
