"""Non-destructive strict revalidation and same-family repair preparation.

The original raw attempts and their original acceptance reports are never
modified.  This tool writes a separate reviewer-side ledger and, when asked,
one attempt-2 instruction into the failing model family's control inbox.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from field_contract import contract_sha256
from output_validator import validate_initial_output
from reconcile import reconcile_record


FAMILIES = ("chatgpt", "claude")
LEDGER_NAME = "repilot_strict_revalidation.json"
SUMMARY_NAME = "repilot_strict_revalidation.md"


class RevalidationError(RuntimeError):
    """The pilot cannot be safely audited or repaired."""


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def _atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_bytes(path, _json_bytes(value))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RevalidationError(f"invalid JSON {path}: {exc}") from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head(path: Path) -> str | None:
    process = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
    )
    return process.stdout.strip() if process.returncode == 0 else None


def _original_artifacts(production: Path, family: str, key: str) -> dict[str, Any]:
    report = (
        production / family / "outputs" / "validation_reports"
        / f"{key}.attempt-01.json"
    )
    promoted = production / family / "outputs" / "validated" / f"{key}.json"
    return {
        "validation_report_path": str(report.relative_to(production)),
        "validation_report_sha256": _sha256(report) if report.is_file() else None,
        "promoted_output_path": str(promoted.relative_to(production)),
        "promoted_output_sha256": _sha256(promoted) if promoted.is_file() else None,
    }


def _expected_keys(source_root: Path) -> list[str]:
    queue_path = source_root / "config" / "REPILOT_7_KEYS.json"
    loaded = _load_json(queue_path)
    if isinstance(loaded, dict):
        loaded = loaded.get("selected_keys_total") or loaded.get("selected_keys")
    if not isinstance(loaded, list) or not loaded or any(not isinstance(key, str) for key in loaded):
        raise RevalidationError("re-pilot queue must be a non-empty list of paper keys")
    if len(loaded) != len(set(loaded)):
        raise RevalidationError("re-pilot queue contains duplicate keys")
    return sorted(loaded)


def _attempt_result(
    production_root: Path,
    source_root: Path,
    family: str,
    key: str,
    attempt: int,
) -> dict[str, Any]:
    relative = Path(family) / "outputs" / "raw" / f"{key}.attempt-{attempt:02d}.json"
    raw = production_root / relative
    if not raw.is_file():
        return {
            "exists": False,
            "path": relative.as_posix(),
            "sha256": None,
            "valid": False,
            "errors": ["raw attempt is missing"],
            "warnings": [],
            "grounding": {"checked": 0, "results": []},
        }

    before = _sha256(raw)
    try:
        record = json.loads(raw.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = {
            "valid": False,
            "errors": [f"invalid raw JSON: {exc}"],
            "warnings": [],
            "grounding": {"checked": 0, "results": []},
        }
    else:
        bundle_path = source_root / "output" / "stage0" / f"{key}.json"
        bundle = _load_json(bundle_path)
        report = validate_initial_output(
            record,
            bundle,
            expected_key=key,
            expected_attempt=attempt,
        )
    after = _sha256(raw)
    if after != before:
        raise RevalidationError(f"raw changed during audit: {family}/{key}/attempt-{attempt}")
    return {
        "exists": True,
        "path": relative.as_posix(),
        "sha256": before,
        "valid": bool(report.get("valid")),
        "errors": list(report.get("errors") or []),
        "warnings": list(report.get("warnings") or []),
        "grounding": report.get("grounding") or {"checked": 0, "results": []},
    }


def _protect_previously_audited_raws(path: Path, records: list[dict[str, Any]]) -> None:
    if not path.is_file():
        return
    previous = _load_json(path)
    old = {
        (row.get("family"), row.get("paper_key"), attempt): details
        for row in previous.get("records") or []
        for attempt, details in (row.get("attempts") or {}).items()
        if details.get("exists")
    }
    current = {
        (row.get("family"), row.get("paper_key"), attempt): details
        for row in records
        for attempt, details in (row.get("attempts") or {}).items()
        if details.get("exists")
    }
    for identity, details in old.items():
        replacement = current.get(identity)
        if replacement is None or replacement.get("sha256") != details.get("sha256"):
            family, key, attempt = identity
            raise RevalidationError(
                f"previously audited raw changed: {family}/{key}/attempt-{attempt}"
            )


def _failure_location(error: str) -> str:
    if error.startswith("schema "):
        return error.split(":", 1)[0]
    return error.split(":", 1)[0]


def _markdown(ledger: dict[str, Any]) -> str:
    summary = ledger["summary"]
    lines = [
        "# Strict re-pilot revalidation",
        "",
        f"- Contract SHA-256: `{ledger['contract_sha256']}`",
        f"- Expected family-paper records: {summary['expected_records']}",
        f"- Strict-valid selected records: {summary['valid_selected_records']}",
        f"- Strict failures: {summary['strict_failures']}",
        f"- Missing records: {summary['missing_records']}",
        f"- Final gate: **{'GREEN' if summary['green'] else 'RED'}**",
        "",
        "This summary is value-blind: it identifies records and validation locations, not model values.",
        "",
        "## Record disposition",
        "",
    ]
    for row in ledger["records"]:
        label = f"{row['family']} / {row['paper_key']}"
        if row["selected_attempt"] is not None:
            lines.append(f"- {label}: strict-valid attempt {row['selected_attempt']}")
            continue
        chosen = row["attempts"]["2"] if row["attempts"]["2"]["exists"] else row["attempts"]["1"]
        locations = sorted({_failure_location(error) for error in chosen["errors"]})
        suffix = ", ".join(locations) if locations else "unspecified validation failure"
        lines.append(f"- {label}: strict failure at {suffix}")
    lines.append("")
    return "\n".join(lines)


def audit_repilot(production_root: str | Path, source_root: str | Path) -> dict[str, Any]:
    """Strictly validate both family outputs without touching any source raw."""
    production = Path(production_root).expanduser().resolve(strict=True)
    source = Path(source_root).expanduser().resolve(strict=True)
    keys = _expected_keys(source)
    source_revisions = {
        "documentation_commit": _git_head(source),
        "code_commit": _git_head(source / "output"),
    }
    records = []
    for family in FAMILIES:
        for key in keys:
            attempts = {
                "1": _attempt_result(production, source, family, key, 1),
                "2": _attempt_result(production, source, family, key, 2),
            }
            chosen_number = 2 if attempts["2"]["exists"] else 1
            chosen = attempts[str(chosen_number)]
            records.append(
                {
                    "family": family,
                    "paper_key": key,
                    "original_artifacts": _original_artifacts(production, family, key),
                    "attempts": attempts,
                    "evaluated_attempt": chosen_number if chosen["exists"] else None,
                    "selected_attempt": chosen_number if chosen["exists"] and chosen["valid"] else None,
                }
            )

    report_dir = production / "reviewer_workspace" / "reports"
    ledger_path = report_dir / LEDGER_NAME
    _protect_previously_audited_raws(ledger_path, records)
    for row in records:
        second = row["attempts"]["2"]
        if not second["exists"]:
            continue
        strict_report = {
            "record_type": "strict_revalidation_report",
            "family": row["family"],
            "paper_key": row["paper_key"],
            "attempt": 2,
            "raw_sha256": second["sha256"],
            "contract_sha256": contract_sha256(),
            "source_revisions": source_revisions,
            "valid": second["valid"],
            "errors": second["errors"],
            "warnings": second["warnings"],
            "grounding": second["grounding"],
        }
        target = (
            production / row["family"] / "outputs" / "validation_reports"
            / f"{row['paper_key']}.attempt-02.strict-revalidation.json"
        )
        _atomic_json(target, strict_report)
    selected = [row for row in records if row["selected_attempt"] is not None]
    missing = sum(1 for row in records if not row["attempts"]["1"]["exists"])
    grounding_checked = sum(
        row["attempts"][str(row["selected_attempt"])]["grounding"].get("checked", 0)
        for row in selected
    )
    expected = len(FAMILIES) * len(keys)
    summary = {
        "expected_records": expected,
        "valid_selected_records": len(selected),
        "strict_failures": expected - len(selected),
        "missing_records": missing,
        "repair_attempts_present": sum(1 for row in records if row["attempts"]["2"]["exists"]),
        "strict_grounding_checks": grounding_checked,
        "green": len(selected) == expected and missing == 0,
    }
    ledger = {
        "ledger_version": "1.0",
        "generated_at": _now(),
        "contract_sha256": contract_sha256(),
        "source_revisions": source_revisions,
        "source_root": str(source),
        "production_root": str(production),
        "expected_families": list(FAMILIES),
        "expected_keys": keys,
        "records": records,
        "summary": summary,
    }
    _atomic_json(ledger_path, ledger)
    _atomic_bytes(report_dir / SUMMARY_NAME, _markdown(ledger).encode("utf-8"))
    return ledger


def prepare_repairs(
    production_root: str | Path,
    ledger: dict[str, Any] | str | Path,
) -> dict[str, Any]:
    """Prepare at most one repair instruction for each strict-invalid raw."""
    production = Path(production_root).expanduser().resolve(strict=True)
    if not isinstance(ledger, dict):
        ledger = _load_json(Path(ledger).expanduser().resolve(strict=True))
    if ledger.get("contract_sha256") != contract_sha256():
        raise RevalidationError("ledger contract does not match current canonical contract")

    failing = [row for row in ledger.get("records") or [] if row.get("selected_attempt") is None]
    for row in failing:
        if (row.get("attempts") or {}).get("2", {}).get("exists"):
            raise RevalidationError(
                f"attempt 2 already exists and is not valid: {row['family']}/{row['paper_key']}"
            )

    created = reused = 0
    instructions = []
    unrepairable = []
    for row in failing:
        first = (row.get("attempts") or {}).get("1") or {}
        if not first.get("exists"):
            unrepairable.append({"family": row["family"], "paper_key": row["paper_key"], "reason": "attempt 1 missing"})
            continue
        family = row["family"]
        key = row["paper_key"]
        instruction = {
            "instruction_version": "1.0",
            "kind": "same_family_strict_repair",
            "family": family,
            "paper_key": key,
            "required_attempt": 2,
            "prior_raw_path": first["path"],
            "prior_raw_sha256": first["sha256"],
            "contract_sha256": ledger["contract_sha256"],
            "strict_errors": first.get("errors") or [],
            "permitted_output_path": f"outputs/raw/{key}.attempt-02.json",
            "permitted_validation_report_path": (
                f"outputs/validation_reports/{key}.attempt-02.strict-revalidation.json"
            ),
            "constraints": [
                "Use only the same model family named in this instruction.",
                "Re-open the assigned Stage-0 bundle and source PDF; do not copy another family's output.",
                "Do not modify attempt 1, promoted outputs, or original validation reports.",
                "No attempt 3 is permitted.",
            ],
        }
        target = production / family / "state" / "control_inbox" / f"{key}.strict-repair.json"
        data = _json_bytes(instruction)
        if target.exists():
            if target.read_bytes() != data:
                raise RevalidationError(f"existing repair instruction differs: {family}/{key}")
            reused += 1
        else:
            _atomic_bytes(target, data)
            created += 1
        instructions.append(instruction)
    return {
        "created": created,
        "reused": reused,
        "instructions": instructions,
        "unrepairable": unrepairable,
    }


def _value(envelope):
    return envelope.get("value") if isinstance(envelope, dict) else envelope


def _value_record(record: dict[str, Any]) -> dict[str, Any]:
    stage1 = record.get("stage1") or {}
    return {
        "key": record.get("paper_key"),
        "eligibility": {
            "methodological_eligibility": _value(stage1.get("methodological_eligibility")),
            "paper_type": _value(stage1.get("paper_type")),
            "borderline_review_synthesis_eligibility": stage1.get(
                "borderline_review_synthesis_eligibility"
            ),
            "level_3b": _value(stage1.get("level_3b")),
        },
        "level_a": {
            name: _value(envelope)
            for name, envelope in (record.get("stage2") or {}).items()
        },
        "level_b": {
            name: _value(envelope)
            for name, envelope in (record.get("stage3") or {}).items()
        },
    }


def _preserve_copy(source: Path, target: Path) -> None:
    data = source.read_bytes()
    if target.exists():
        if target.read_bytes() != data:
            raise RevalidationError(f"strict namespace import differs: {target}")
        return
    _atomic_bytes(target, data)


def _reconciliation_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Strict-selected re-pilot reconciliation",
        "",
        f"- Contract SHA-256: `{result['contract_sha256']}`",
        f"- Common paper pairs: {summary['common_keys']}",
        f"- Compared cells: {summary['compared']}",
        f"- Concordant routing cells: {summary['concordant']}",
        f"- Divergent routing cells: {summary['divergent']}",
        "",
        "Agreement is a routing signal only, not a reliability estimate. This report is value-blind.",
        "",
        "| Tier | Compared | Concordant | Divergent |",
        "|---|---:|---:|---:|",
    ]
    for tier in (1, 2, 3):
        row = summary[f"tier{tier}"]
        lines.append(
            f"| {tier} | {row['compared']} | {row['concordant']} | {row['divergent']} |"
        )
    lines.extend(["", "## Normalization deltas from the original pilot queue", ""])
    if result["normalization_deltas"]:
        for delta in result["normalization_deltas"]:
            lines.append(
                f"- {delta['paper_key']} — {delta['section']}.{delta['field']}: "
                f"agreement {str(delta['from_agree']).lower()} → {str(delta['to_agree']).lower()}"
            )
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def reconcile_strict_selected(
    production_root: str | Path,
    ledger: dict[str, Any] | str | Path,
) -> dict[str, Any]:
    """Reconcile strict-selected attempts in a separate immutable namespace."""
    production = Path(production_root).expanduser().resolve(strict=True)
    if not isinstance(ledger, dict):
        ledger = _load_json(Path(ledger).expanduser().resolve(strict=True))
    if not (ledger.get("summary") or {}).get("green"):
        raise RevalidationError("strict revalidation must be green before reconciliation")
    if ledger.get("contract_sha256") != contract_sha256():
        raise RevalidationError("ledger contract does not match current canonical contract")

    namespace = production / "reviewer_workspace" / "strict_revalidation"
    by_identity = {
        (row["family"], row["paper_key"]): row for row in ledger.get("records") or []
    }
    loaded: dict[tuple[str, str], dict[str, Any]] = {}
    for family in FAMILIES:
        for key in ledger.get("expected_keys") or []:
            row = by_identity.get((family, key))
            if row is None or row.get("selected_attempt") is None:
                raise RevalidationError(f"missing strict selection: {family}/{key}")
            attempt = str(row["selected_attempt"])
            details = row["attempts"][attempt]
            source = production / details["path"]
            if _sha256(source) != details["sha256"]:
                raise RevalidationError(f"selected raw hash mismatch: {family}/{key}")
            target = namespace / "imports" / family / f"{key}.json"
            _preserve_copy(source, target)
            loaded[(family, key)] = _load_json(target)

    totals = {
        tier: {"compared": 0, "concordant": 0, "divergent": 0}
        for tier in (1, 2, 3)
    }
    normalization_deltas = []
    keys = ledger.get("expected_keys") or []
    for key in keys:
        reconciliation = reconcile_record(
            _value_record(loaded[("chatgpt", key)]),
            _value_record(loaded[("claude", key)]),
        )
        _atomic_json(namespace / "reconciled" / f"{key}.json", reconciliation)
        for field in reconciliation["fields"]:
            bucket = totals[field["tier"]]
            bucket["compared"] += 1
            bucket["concordant" if field["agree"] else "divergent"] += 1

        original_path = (
            production / "reviewer_workspace" / "state" / "reconciled" / f"{key}.json"
        )
        if original_path.is_file():
            original = _load_json(original_path)
            previous = {
                (field["section"], field["field"]): field["agree"]
                for field in original.get("fields") or []
            }
            for field in reconciliation["fields"]:
                identity = (field["section"], field["field"])
                if identity in previous and previous[identity] != field["agree"]:
                    normalization_deltas.append(
                        {
                            "paper_key": key,
                            "section": field["section"],
                            "field": field["field"],
                            "from_agree": previous[identity],
                            "to_agree": field["agree"],
                        }
                    )

    summary = {
        "common_keys": len(keys),
        "compared": sum(row["compared"] for row in totals.values()),
        "concordant": sum(row["concordant"] for row in totals.values()),
        "divergent": sum(row["divergent"] for row in totals.values()),
        **{f"tier{tier}": totals[tier] for tier in (1, 2, 3)},
    }
    result = {
        "generated_at": _now(),
        "contract_sha256": ledger["contract_sha256"],
        "ledger_sha256": hashlib.sha256(_json_bytes(ledger)).hexdigest(),
        "summary": summary,
        "normalization_deltas": normalization_deltas,
    }
    reports = production / "reviewer_workspace" / "reports"
    _atomic_json(reports / "repilot_strict_reconciliation.json", result)
    _atomic_bytes(
        reports / "repilot_strict_reconciliation.md",
        _reconciliation_markdown(result).encode("utf-8"),
    )
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit")
    audit.add_argument("--production-root", type=Path, required=True)
    audit.add_argument("--source-root", type=Path, required=True)
    repairs = subparsers.add_parser("prepare-repairs")
    repairs.add_argument("--production-root", type=Path, required=True)
    repairs.add_argument("--ledger", type=Path, required=True)
    reconcile = subparsers.add_parser("reconcile")
    reconcile.add_argument("--production-root", type=Path, required=True)
    reconcile.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "audit":
        result = audit_repilot(args.production_root, args.source_root)
    elif args.command == "prepare-repairs":
        result = prepare_repairs(args.production_root, args.ledger)
    else:
        result = reconcile_strict_selected(args.production_root, args.ledger)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
