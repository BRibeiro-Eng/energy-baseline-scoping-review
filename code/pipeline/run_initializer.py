"""One-time, atomic provenance initialization for an interactive model pack."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path

from pack_verifier import VerificationError, verify_workspace


class InitializationError(RuntimeError):
    pass


def _atomic_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def initialize_run(
    workspace,
    *,
    run_id,
    executor,
    app_version,
    model_label,
    started_at=None,
):
    workspace = Path(workspace).expanduser().resolve(strict=True)
    try:
        verify_workspace(workspace)
    except VerificationError as exc:
        raise InitializationError(str(exc)) from exc
    if executor not in ("chatgpt", "claude") or workspace.name != executor:
        raise InitializationError(
            f"executor {executor!r} does not match workspace {workspace.name!r}"
        )
    if not all(isinstance(value, str) and value.strip() for value in (
        run_id, app_version, model_label
    )):
        raise InitializationError("run_id, app_version, and model_label are required")
    started_at = started_at or dt.datetime.now().astimezone().isoformat(timespec="seconds")
    if not isinstance(started_at, str) or not started_at.strip():
        raise InitializationError("started_at must be a non-empty ISO-8601 string")

    metadata_path = workspace / "run_metadata.json"
    lock_path = workspace / "state" / ".run-metadata.lock"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        run = metadata.setdefault("run", {})
        surface = metadata.setdefault("execution_surfaces", {}).setdefault(executor, {})
        requested = {
            "run_id": run_id,
            "executor": executor,
            "started_at": started_at,
            "app_version": app_version,
            "model_label": model_label,
        }
        existing = {
            "run_id": run.get("run_id"),
            "executor": run.get("executor"),
            "started_at": run.get("started_at"),
            "app_version": surface.get("app_version"),
            "model_label": surface.get("model_label"),
        }
        if any(value is not None for value in existing.values()):
            if existing == requested:
                return {"initialized": False, **requested}
            raise InitializationError("run metadata is already initialized and differs")
        run.update({
            "run_id": run_id,
            "executor": executor,
            "started_at": started_at,
            "working_directory": str(workspace),
        })
        surface.update({"app_version": app_version, "model_label": model_label})
        _atomic_json(metadata_path, metadata)
    return {"initialized": True, **requested}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--executor", choices=("chatgpt", "claude"), required=True)
    parser.add_argument("--app-version", required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--started-at")
    args = parser.parse_args(argv)
    result = initialize_run(
        args.workspace,
        run_id=args.run_id,
        executor=args.executor,
        app_version=args.app_version,
        model_label=args.model_label,
        started_at=args.started_at,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
