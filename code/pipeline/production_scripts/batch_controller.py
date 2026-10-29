"""Atomic, approval-gated batch state for interactive article extraction."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path

from output_validator import validate_initial_output
from pack_verifier import VerificationError, verify_workspace


class BatchError(RuntimeError):
    """The requested batch transition violates controller invariants."""


def _now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BatchError(f"invalid state file {path}: {exc}") from exc


def _atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextlib.contextmanager
def _locked(workspace: Path):
    lock_path = workspace / "state" / ".controller.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _verified(workspace, require_production=False):
    try:
        return verify_workspace(workspace, require_production=require_production)
    except VerificationError as exc:
        raise BatchError(str(exc)) from exc


def _verified_run_mode(workspace, *, fixture=False, repilot=False):
    if fixture and repilot:
        raise BatchError("fixture and repilot modes are mutually exclusive")
    report = _verified(workspace, require_production=not (fixture or repilot))
    if repilot:
        lock = _load(Path(workspace) / "PACK_LOCK.json")
        inventory = _load(Path(workspace) / "CANONICAL_INPUTS.json")
        if lock.get("development_build") is not True:
            raise BatchError("repilot mode requires a development build")
        if inventory.get("queue_scope") != "development_subset":
            raise BatchError("repilot mode requires an explicit development queue subset")
        metadata = _load(Path(workspace) / "run_metadata.json")
        run = metadata.get("run") or {}
        executor = run.get("executor")
        surface = (metadata.get("execution_surfaces") or {}).get(executor) or {}
        if (
            executor != Path(workspace).name
            or not run.get("run_id")
            or not run.get("started_at")
            or not surface.get("app_version")
            or not surface.get("model_label")
        ):
            raise BatchError("repilot surface provenance is not initialized")
    return report


def _paths(workspace: Path):
    state = workspace / "state"
    return {
        "pending": state / "pending_keys.json",
        "completed": state / "completed_keys.json",
        "failed": state / "failed_keys.json",
        "active": state / "active_batch.json",
        "proposed": state / "proposed_batch.json",
        "progress": state / "progress_summary.json",
        "next": state / "NEXT_SESSION.md",
        "batches": state / "batches",
    }


def _state(workspace: Path):
    paths = _paths(workspace)
    pending = _load(paths["pending"])
    completed = _load(paths["completed"])
    failed = _load(paths["failed"])
    active = _load(paths["active"])
    proposed = _load(paths["proposed"])
    for name, value in (("pending", pending), ("completed", completed), ("failed", failed)):
        if not isinstance(value, list) or len(value) != len(set(value)):
            raise BatchError(f"{name}_keys must be a unique list")
    sets = [set(pending), set(completed), set(failed)]
    if any(sets[i] & sets[j] for i in range(3) for j in range(i + 1, 3)):
        raise BatchError("pending/completed/failed indexes overlap")
    active_keys = set((active or {}).get("keys") or [])
    if active_keys & set(pending) or active_keys & set(completed) or active_keys & set(failed):
        raise BatchError("active keys overlap aggregate indexes")
    proposed_keys = set((proposed or {}).get("keys") or [])
    if proposed_keys and not proposed_keys <= set(pending):
        raise BatchError("proposed keys are not pending")
    inventory = _load(workspace / "CANONICAL_INPUTS.json")
    allowed = set(inventory.get("stage1_keys") or [])
    if not (set(pending) | set(completed) | set(failed) | active_keys) <= allowed:
        raise BatchError("state contains a key outside the canonical Stage-1 queue")
    return {
        "pending": pending,
        "completed": completed,
        "failed": failed,
        "active": active,
        "proposed": proposed,
        "paths": paths,
    }


def _progress(st):
    return {
        "pending": len(st["pending"]),
        "active": len((st["active"] or {}).get("keys") or []),
        "completed": len(st["completed"]),
        "failed": len(st["failed"]),
    }


def workspace_status(workspace):
    workspace = Path(workspace).resolve(strict=True)
    verification = _verified(workspace)
    with _locked(workspace):
        st = _state(workspace)
        return {
            "workspace": str(workspace),
            "pack": verification,
            "progress": _progress(st),
            "pending_keys": st["pending"],
            "completed_keys": st["completed"],
            "failed_keys": st["failed"],
            "active_batch": st["active"],
            "proposed_batch": st["proposed"],
        }


def _batch_files(paths):
    return sorted(paths["batches"].glob("batch-*.json"))


def _ten_allowed(paths):
    histories = [_load(path) for path in _batch_files(paths)]
    return len(histories) >= 2 and all(row.get("green") is True for row in histories[-2:])


def propose_batch(workspace, *, size=5):
    workspace = Path(workspace).resolve(strict=True)
    _verified(workspace)
    if size not in (1, 2, 3, 4, 5, 10):
        raise BatchError("batch size must be 1-5, or 10 after the green-batch gate")
    with _locked(workspace):
        st = _state(workspace)
        if st["active"] is not None:
            raise BatchError("an active batch must terminate before a proposal")
        if st["proposed"] is not None:
            raise BatchError("a proposed batch already awaits approval")
        if size == 10 and not _ten_allowed(st["paths"]):
            raise BatchError("size 10 requires two consecutive green batches")
        if not st["pending"]:
            raise BatchError("no pending papers remain")
        batch_number = len(_batch_files(st["paths"])) + 1
        proposal = {
            "batch_id": f"batch-{batch_number:04d}",
            "mode": "initial",
            "status": "proposed",
            "requested_size": size,
            "keys": st["pending"][:size],
            "proposed_at": _now(),
            "authorized_at": None,
            "authorized_by": None,
            "papers": {},
        }
        _atomic_json(st["paths"]["proposed"], proposal)
        _atomic_json(st["paths"]["batches"] / f"{proposal['batch_id']}.json", proposal)
        return proposal


def approve_proposal(
    workspace, batch_id, *, authorized_by, fixture=False, repilot=False
):
    workspace = Path(workspace).resolve(strict=True)
    _verified_run_mode(workspace, fixture=fixture, repilot=repilot)
    if not authorized_by:
        raise BatchError("authorized_by is required")
    with _locked(workspace):
        st = _state(workspace)
        if st["active"] is not None:
            raise BatchError("an active batch already exists")
        proposal = st["proposed"]
        if proposal is None or proposal.get("batch_id") != batch_id:
            raise BatchError("proposal id does not match")
        active = dict(proposal)
        active.update({
            "status": "active",
            "authorized_at": _now(),
            "authorized_by": authorized_by,
            "fixture_mode": bool(fixture),
            "repilot_mode": bool(repilot),
            "papers": {key: {"status": "assigned", "attempts": {}} for key in proposal["keys"]},
        })
        st["pending"] = [key for key in st["pending"] if key not in set(active["keys"])]
        _atomic_json(st["paths"]["pending"], st["pending"])
        _atomic_json(st["paths"]["active"], active)
        _atomic_json(st["paths"]["proposed"], None)
        _atomic_json(st["paths"]["batches"] / f"{batch_id}.json", active)
        st["active"] = active
        st["proposed"] = None
        _atomic_json(st["paths"]["progress"], _progress(st))
        return active


def recover_active_batch(workspace):
    workspace = Path(workspace).resolve(strict=True)
    _verified(workspace)
    with _locked(workspace):
        st = _state(workspace)
        if st["active"] is None:
            return {"status": "none", "active_batch": None}
        active = st["active"]
        raw = workspace / "outputs" / "raw"
        presence = {
            key: {
                "attempt_1": (raw / f"{key}.attempt-01.json").is_file(),
                "attempt_2": (raw / f"{key}.attempt-02.json").is_file(),
            }
            for key in active["keys"]
        }
        return {"status": active["status"], "active_batch": active, "raw_presence": presence}


def _validate_raw(workspace, key, attempt):
    raw = workspace / "outputs" / "raw" / f"{key}.attempt-{attempt:02d}.json"
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
        report = validate_initial_output(
            record, bundle, expected_key=key, expected_attempt=attempt,
            schema_path=workspace / "schemas" / "article_output.schema.json",
        )
    return raw, report, _sha256(raw)


def _preserve_validated(workspace, key, raw):
    target = workspace / "outputs" / "validated" / f"{key}.json"
    data = raw.read_bytes()
    if target.exists():
        if target.read_bytes() != data:
            raise BatchError(f"validated output is immutable and differs: {key}")
        return
    with target.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _record_attempt(paper, attempt, raw_hash, report):
    attempts = paper.setdefault("attempts", {})
    key = str(attempt)
    previous = attempts.get(key)
    if previous and previous.get("raw_sha256") != raw_hash:
        raise BatchError(f"raw attempt changed after validation: attempt {attempt}")
    attempts[key] = {
        "raw_sha256": raw_hash,
        "valid": report["valid"],
        "errors": report["errors"],
        "warnings": report["warnings"],
        "validated_at": _now(),
    }


def _append_run_metadata(workspace, summary):
    path = workspace / "run_metadata.json"
    data = _load(path)
    data.setdefault("run", {}).setdefault("batches", []).append(summary)
    _atomic_json(path, data)


def finalize_active_batch(workspace, *, fixture=False, repilot=False):
    workspace = Path(workspace).resolve(strict=True)
    _verified_run_mode(workspace, fixture=fixture, repilot=repilot)
    with _locked(workspace):
        st = _state(workspace)
        active = st["active"]
        if active is None:
            raise BatchError("no active batch")
        if active.get("status") not in ("active", "repair_required"):
            raise BatchError(f"batch cannot be finalized from {active.get('status')}")

        completed, failed, repair_required, waiting = [], [], [], []
        for key in active["keys"]:
            paper = active["papers"][key]
            raw2, report2, hash2 = _validate_raw(workspace, key, 2)
            raw1, report1, hash1 = _validate_raw(workspace, key, 1)
            if raw1 is None:
                waiting.append(key)
                paper["status"] = "awaiting_attempt_1"
                continue
            _record_attempt(paper, 1, hash1, report1)
            chosen_raw, chosen_report, chosen_attempt = raw1, report1, 1
            if not report1["valid"]:
                if raw2 is None:
                    repair_required.append(key)
                    paper["status"] = "repair_required"
                    _atomic_json(
                        workspace / "outputs" / "validation_reports" / f"{key}.attempt-01.json",
                        report1,
                    )
                    continue
                _record_attempt(paper, 2, hash2, report2)
                chosen_raw, chosen_report, chosen_attempt = raw2, report2, 2

            _atomic_json(
                workspace / "outputs" / "validation_reports" / f"{key}.attempt-{chosen_attempt:02d}.json",
                chosen_report,
            )
            if chosen_report["valid"]:
                _preserve_validated(workspace, key, chosen_raw)
                paper.update({"status": "completed", "accepted_attempt": chosen_attempt})
                completed.append(key)
            else:
                paper.update({"status": "failed", "accepted_attempt": None})
                failed.append(key)
                _atomic_json(workspace / "outputs" / "quarantine" / f"{key}.json", {
                    "paper_key": key,
                    "reason": "invalid after one repair",
                    "attempts": paper["attempts"],
                    "quarantined_at": _now(),
                })

        if waiting:
            status = "active"
        elif repair_required:
            status = "repair_required"
        else:
            status = "completed_with_failures" if failed else "completed"
        active["status"] = status
        active["updated_at"] = _now()

        terminal = status in ("completed", "completed_with_failures")
        if terminal:
            active["completed_at"] = _now()
            active["green"] = not failed and all(
                active["papers"][key].get("accepted_attempt") == 1
                and not active["papers"][key]["attempts"]["1"].get("warnings")
                for key in active["keys"]
            )
            st["completed"] = sorted(set(st["completed"]) | set(completed))
            st["failed"] = sorted(set(st["failed"]) | set(failed))
            _atomic_json(st["paths"]["completed"], st["completed"])
            _atomic_json(st["paths"]["failed"], st["failed"])
            _atomic_json(st["paths"]["active"], None)
            _atomic_json(st["paths"]["proposed"], None)
            _atomic_json(st["paths"]["batches"] / f"{active['batch_id']}.json", active)
            st["active"] = None
            st["proposed"] = None
            st["paths"]["next"].write_text(
                f"Batch {active['batch_id']} terminated as {status}. A new proposal requires new approval.\n",
                encoding="utf-8",
            )
            _append_run_metadata(workspace, {
                "batch_id": active["batch_id"], "status": status,
                "completed_at": active["completed_at"], "green": active["green"],
                "completed": completed, "failed": failed,
            })
        else:
            _atomic_json(st["paths"]["active"], active)
            _atomic_json(st["paths"]["batches"] / f"{active['batch_id']}.json", active)
            st["active"] = active
        _atomic_json(st["paths"]["progress"], _progress(st))
        return {
            "batch_id": active["batch_id"],
            "status": status,
            "completed": completed,
            "failed": failed,
            "repair_required": repair_required,
            "waiting": waiting,
        }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--repilot", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    propose = sub.add_parser("propose")
    propose.add_argument("--size", type=int, default=5)
    approve = sub.add_parser("approve")
    approve.add_argument("batch_id")
    approve.add_argument("--authorized-by", required=True)
    sub.add_parser("recover")
    sub.add_parser("finalize")
    args = parser.parse_args(argv)
    if args.command == "status":
        result = workspace_status(args.workspace)
    elif args.command == "propose":
        result = propose_batch(args.workspace, size=args.size)
    elif args.command == "approve":
        result = approve_proposal(
            args.workspace,
            args.batch_id,
            authorized_by=args.authorized_by,
            fixture=args.fixture,
            repilot=args.repilot,
        )
    elif args.command == "recover":
        result = recover_active_batch(args.workspace)
    else:
        result = finalize_active_batch(
            args.workspace, fixture=args.fixture, repilot=args.repilot
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
