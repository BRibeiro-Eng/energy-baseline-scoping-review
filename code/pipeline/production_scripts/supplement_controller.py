"""Model-local Stage-3 supplement planning from a blind-safe roster receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import contextlib
import datetime as dt
import fcntl
from pathlib import Path

from pack_verifier import VerificationError, verify_workspace
from output_validator import validate_stage3_supplement


class SupplementError(RuntimeError):
    pass


def _canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def _hash_value(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as stream:
        stream.write(_canonical(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SupplementError(f"invalid supplement state {path}: {exc}") from exc


def _now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


@contextlib.contextmanager
def _locked(workspace):
    path = Path(workspace) / "state" / ".supplement.lock"
    with path.open("a+") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _verify(workspace, require_production=False):
    try:
        return verify_workspace(workspace, require_production=require_production)
    except VerificationError as exc:
        raise SupplementError(str(exc)) from exc


def _branch(size):
    if size <= 40:
        return "integral_blind_first", False
    if size <= 60:
        return "hybrid", False
    return "paused_over_60", True


def plan_stage3_supplements(workspace, receipt):
    workspace = Path(workspace).resolve(strict=True)
    _verify(workspace)
    if not isinstance(receipt, dict):
        raise SupplementError("roster receipt must be an object")
    supplied = dict(receipt)
    recorded_hash = supplied.pop("receipt_sha256", None)
    if not recorded_hash or _hash_value(supplied) != recorded_hash:
        raise SupplementError("roster receipt hash mismatch")
    keys = receipt.get("keys")
    if not isinstance(keys, list) or len(keys) != len(set(keys)) or keys != sorted(keys):
        raise SupplementError("roster keys must be a sorted unique list")
    inventory = json.loads((workspace / "CANONICAL_INPUTS.json").read_text())
    if not set(keys) <= set(inventory.get("stage1_keys") or []):
        raise SupplementError("roster contains a key outside the canonical queue")
    branch_name, paused = _branch(len(keys))
    if (receipt.get("branch") or {}).get("name") != branch_name:
        raise SupplementError("roster branch does not match roster size")

    missing, items = [], []
    for key in keys:
        initial = workspace / "outputs" / "validated" / f"{key}.json"
        if not initial.is_file():
            raise SupplementError(f"missing initial validated output: {key}")
        record = json.loads(initial.read_text(encoding="utf-8"))
        if record.get("paper_key") != key:
            raise SupplementError(f"initial output key mismatch: {key}")
        if record.get("stage3") is None:
            missing.append(key)
            items.append({
                "paper_key": key,
                "initial_output_sha256": _sha256(initial),
                "original_level_3b": ((record.get("stage1") or {}).get("level_3b") or {}).get("value"),
            })
    plan = {
        "roster_version": receipt.get("roster_version"),
        "roster_receipt_sha256": recorded_hash,
        "roster_size": len(keys),
        "branch": receipt.get("branch"),
        "blocked": paused,
        "reason": "Corpus-B size exceeds 60; Level-B work paused" if paused else None,
        "keys": missing,
        "authorized_keys": [] if paused else missing,
        "items": items,
    }
    _atomic_json(workspace / "state" / "stage3_supplement_plan.json", plan)
    for name, value in (
        ("stage3_supplement_proposed.json", None),
        ("stage3_supplement_active.json", None),
        ("stage3_supplement_completed.json", []),
        ("stage3_supplement_failed.json", []),
    ):
        path = workspace / "state" / name
        if not path.exists():
            _atomic_json(path, value)
    (workspace / "state" / "stage3_supplement_batches").mkdir(exist_ok=True)
    return plan


def _supplement_paths(workspace):
    state = Path(workspace) / "state"
    return {
        "plan": state / "stage3_supplement_plan.json",
        "proposed": state / "stage3_supplement_proposed.json",
        "active": state / "stage3_supplement_active.json",
        "completed": state / "stage3_supplement_completed.json",
        "failed": state / "stage3_supplement_failed.json",
        "batches": state / "stage3_supplement_batches",
    }


def supplement_status(workspace):
    workspace = Path(workspace).resolve(strict=True)
    _verify(workspace)
    paths = _supplement_paths(workspace)
    return {
        "plan": _load(paths["plan"]),
        "proposed": _load(paths["proposed"]) if paths["proposed"].is_file() else None,
        "active": _load(paths["active"]) if paths["active"].is_file() else None,
        "completed": _load(paths["completed"]) if paths["completed"].is_file() else [],
        "failed": _load(paths["failed"]) if paths["failed"].is_file() else [],
    }


def propose_supplement_batch(workspace, *, size=5):
    workspace = Path(workspace).resolve(strict=True)
    _verify(workspace)
    if size not in (1, 2, 3, 4, 5, 10):
        raise SupplementError("supplement batch size must be 1-5 or gated size 10")
    paths = _supplement_paths(workspace)
    with _locked(workspace):
        plan = _load(paths["plan"])
        if plan.get("blocked"):
            raise SupplementError(plan.get("reason") or "supplement plan is blocked")
        if _load(paths["active"]) is not None:
            raise SupplementError("an active supplement batch already exists")
        if _load(paths["proposed"]) is not None:
            raise SupplementError("a supplement proposal already awaits approval")
        completed, failed = set(_load(paths["completed"])), set(_load(paths["failed"]))
        remaining = [key for key in plan.get("authorized_keys") or [] if key not in completed | failed]
        if not remaining:
            raise SupplementError("no Stage-3 supplements remain")
        if size == 10:
            histories = [
                _load(path) for path in sorted((workspace / "state" / "batches").glob("batch-*.json"))
            ]
            if len(histories) < 2 or not all(row.get("green") for row in histories[-2:]):
                raise SupplementError("size 10 requires two consecutive green initial batches")
        number = len(list(paths["batches"].glob("supplement-*.json"))) + 1
        proposal = {
            "batch_id": f"supplement-{number:04d}",
            "status": "proposed",
            "requested_size": size,
            "keys": remaining[:size],
            "proposed_at": _now(),
            "authorized_at": None,
            "authorized_by": None,
            "papers": {},
        }
        _atomic_json(paths["proposed"], proposal)
        _atomic_json(paths["batches"] / f"{proposal['batch_id']}.json", proposal)
        return proposal


def approve_supplement_proposal(workspace, batch_id, *, authorized_by, fixture=False):
    workspace = Path(workspace).resolve(strict=True)
    _verify(workspace, require_production=not fixture)
    paths = _supplement_paths(workspace)
    with _locked(workspace):
        proposal = _load(paths["proposed"])
        if proposal is None or proposal.get("batch_id") != batch_id:
            raise SupplementError("supplement proposal id does not match")
        if _load(paths["active"]) is not None:
            raise SupplementError("an active supplement batch already exists")
        active = dict(proposal)
        active.update({
            "status": "active",
            "authorized_at": _now(),
            "authorized_by": authorized_by,
            "fixture_mode": bool(fixture),
            "papers": {key: {"status": "assigned", "attempts": {}} for key in proposal["keys"]},
        })
        _atomic_json(paths["active"], active)
        _atomic_json(paths["proposed"], None)
        _atomic_json(paths["batches"] / f"{batch_id}.json", active)
        return active


def _validate_raw(workspace, plan, key, attempt):
    raw = workspace / "outputs" / "raw" / f"{key}.stage3-supplement.attempt-{attempt:02d}.json"
    if not raw.is_file():
        return None, None, None
    try:
        record = json.loads(raw.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = {
            "valid": False, "paper_key": key, "attempt": attempt,
            "errors": [f"invalid raw JSON: {exc}"], "warnings": [],
            "grounding": {"checked": 0, "results": []},
        }
    else:
        bundle = _load(workspace / "inputs" / "stage0" / f"{key}.json")
        report = validate_stage3_supplement(
            record,
            bundle,
            plan,
            expected_key=key,
            expected_attempt=attempt,
            schema_path=workspace / "schemas" / "stage3_supplement.schema.json",
        )
    return raw, report, _sha256(raw)


def _promote(workspace, key, raw):
    target = workspace / "outputs" / "validated" / f"{key}.stage3-supplement.json"
    data = raw.read_bytes()
    if target.exists():
        if target.read_bytes() != data:
            raise SupplementError(f"validated supplement is immutable and differs: {key}")
        return
    with target.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def finalize_supplement_batch(workspace, *, fixture=False):
    workspace = Path(workspace).resolve(strict=True)
    _verify(workspace, require_production=not fixture)
    paths = _supplement_paths(workspace)
    with _locked(workspace):
        plan, active = _load(paths["plan"]), _load(paths["active"])
        if active is None:
            raise SupplementError("no active supplement batch")
        completed, failed, repair, waiting = [], [], [], []
        for key in active["keys"]:
            paper = active["papers"][key]
            raw1, report1, hash1 = _validate_raw(workspace, plan, key, 1)
            raw2, report2, hash2 = _validate_raw(workspace, plan, key, 2)
            if raw1 is None:
                waiting.append(key)
                paper["status"] = "awaiting_attempt_1"
                continue
            paper["attempts"]["1"] = {"raw_sha256": hash1, **report1}
            raw, report, accepted_attempt = raw1, report1, 1
            if not report1["valid"]:
                if raw2 is None:
                    repair.append(key)
                    paper["status"] = "repair_required"
                    _atomic_json(
                        workspace / "outputs" / "validation_reports"
                        / f"{key}.stage3-supplement.attempt-01.json",
                        report1,
                    )
                    continue
                paper["attempts"]["2"] = {"raw_sha256": hash2, **report2}
                raw, report, accepted_attempt = raw2, report2, 2
            _atomic_json(
                workspace / "outputs" / "validation_reports"
                / f"{key}.stage3-supplement.attempt-{accepted_attempt:02d}.json",
                report,
            )
            if report["valid"]:
                _promote(workspace, key, raw)
                paper.update({"status": "completed", "accepted_attempt": accepted_attempt})
                completed.append(key)
            else:
                paper.update({"status": "failed", "accepted_attempt": None})
                failed.append(key)
                _atomic_json(
                    workspace / "outputs" / "quarantine" / f"{key}.stage3-supplement.json",
                    {
                        "paper_key": key,
                        "reason": "Stage-3 supplement invalid after one repair; blind-first fallback required",
                        "attempts": paper["attempts"],
                        "quarantined_at": _now(),
                    },
                )
        if waiting:
            status = "active"
        elif repair:
            status = "repair_required"
        else:
            status = "completed_with_failures" if failed else "completed"
        active["status"] = status
        if status in ("completed", "completed_with_failures"):
            active["completed_at"] = _now()
            active["green"] = not failed and all(
                active["papers"][key].get("accepted_attempt") == 1 for key in active["keys"]
            )
            all_completed = sorted(set(_load(paths["completed"])) | set(completed))
            all_failed = sorted(set(_load(paths["failed"])) | set(failed))
            _atomic_json(paths["completed"], all_completed)
            _atomic_json(paths["failed"], all_failed)
            _atomic_json(paths["active"], None)
        else:
            _atomic_json(paths["active"], active)
        _atomic_json(paths["batches"] / f"{active['batch_id']}.json", active)
        return {
            "batch_id": active["batch_id"], "status": status,
            "completed": completed, "failed": failed,
            "repair_required": repair, "waiting": waiting,
        }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--fixture", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    plan = sub.add_parser("plan")
    plan.add_argument("receipt", type=Path)
    propose = sub.add_parser("propose")
    propose.add_argument("--size", type=int, default=5)
    approve = sub.add_parser("approve")
    approve.add_argument("batch_id")
    approve.add_argument("--authorized-by", required=True)
    sub.add_parser("finalize")
    args = parser.parse_args(argv)
    if args.command == "status":
        result = supplement_status(args.workspace)
    elif args.command == "plan":
        result = plan_stage3_supplements(args.workspace, _load(args.receipt))
    elif args.command == "propose":
        result = propose_supplement_batch(args.workspace, size=args.size)
    elif args.command == "approve":
        result = approve_supplement_proposal(
            args.workspace,
            args.batch_id,
            authorized_by=args.authorized_by,
            fixture=args.fixture,
        )
    else:
        result = finalize_supplement_batch(args.workspace, fixture=args.fixture)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
