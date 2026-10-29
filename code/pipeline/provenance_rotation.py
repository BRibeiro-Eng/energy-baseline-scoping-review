"""provenance_rotation.py — surface-segment rotation for the interactive packs.

Validation Protocol C-2.3 sec 3-Step-1 requires, per run, the "application
version, model label exactly as displayed by the surface, runtime
configuration, run dates and per-paper timestamps". The consumer-subscription
surfaces update on the vendor's schedule, not ours, so a run spanning weeks
crosses application versions. run_initializer.initialize_run is one-time by
design and refuses any change -- correctly: an orchestrator session must never
be able to rewrite its own provenance.

Rotation is therefore an OPERATOR action and lives here, in the canonical code
repo, outside both packs' immutable manifests. It is strictly additive:

  * execution_surfaces.<executor>.surface_segments becomes the authoritative
    per-segment record; nothing already recorded is ever overwritten;
  * the scalar app_version/model_label continue to describe the CURRENT
    segment, which is what pack_verifier._runtime_blockers reads and what the
    next batch will actually run under.

Closing a segment without opening a new one is not supported: a pack with a
closed-but-unopened segment would verify while denoting no runtime at all.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path

EXECUTORS = ("chatgpt", "claude")


class RotationError(RuntimeError):
    """The requested rotation would corrupt or falsify the provenance record."""


def _now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _atomic_json(path, value):
    """Byte-format identical to run_initializer._atomic_json."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _seed_segment(surface, run, batches):
    """Reconstruct segment 1 from a pack that predates segmentation."""
    return {
        "segment": 1,
        "app_version": surface.get("app_version"),
        "model_label": surface.get("model_label"),
        "opened_at": run.get("started_at"),
        "closed_at": None,
        "first_batch": batches[0]["batch_id"] if batches else None,
        "last_batch": None,
        "note": "reconstructed at first rotation; this pack was initialized before surface_segments existed",
    }


def _batch_history(metadata):
    return [b for b in ((metadata.get("run") or {}).get("batches") or []) if b.get("batch_id")]


def rotate_surface(
    workspace,
    *,
    executor,
    app_version,
    model_label,
    observed_at=None,
    reason,
    authorized_by,
):
    """Close the open segment at the last finalized batch and open a new one."""
    workspace = Path(workspace).expanduser().resolve(strict=True)
    if executor not in EXECUTORS or workspace.name != executor:
        raise RotationError(
            f"executor {executor!r} does not match workspace {workspace.name!r}"
        )
    if not all(isinstance(v, str) and v.strip() for v in (
        app_version, model_label, reason, authorized_by
    )):
        raise RotationError("app_version, model_label, reason and authorized_by are required")
    observed_at = observed_at or _now()

    metadata_path = workspace / "run_metadata.json"
    lock_path = workspace / "state" / ".run-metadata.lock"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        run = metadata.get("run") or {}
        if run.get("executor") != executor:
            raise RotationError("run metadata is not initialized for this executor")
        surface = (metadata.get("execution_surfaces") or {}).get(executor)
        if not surface or not surface.get("app_version") or not surface.get("model_label"):
            raise RotationError("surface provenance is not initialized; run run_initializer first")

        # An unterminated batch would land in the wrong segment.
        state = workspace / "state"
        for name in ("active_batch.json", "proposed_batch.json"):
            if json.loads((state / name).read_text(encoding="utf-8")) is not None:
                raise RotationError(f"{name} is not null; terminate it before rotating")

        batches = _batch_history(metadata)
        segments = surface.get("surface_segments") or [_seed_segment(surface, run, batches)]
        open_segments = [s for s in segments if s.get("closed_at") is None]
        if len(open_segments) != 1:
            raise RotationError(f"expected exactly one open segment, found {len(open_segments)}")
        current = open_segments[0]

        if (current.get("app_version"), current.get("model_label")) == (app_version, model_label):
            return {"rotated": False, "reason": "surface unchanged", "segments": segments}
        for past in segments:
            if past is current:
                continue
            if (past.get("app_version"), past.get("model_label")) == (app_version, model_label):
                raise RotationError(
                    f"surface {app_version}/{model_label} already occupies segment "
                    f"{past.get('segment')}; a reverted surface needs its own explicit segment id"
                )

        last = batches[-1] if batches else None
        current.update({
            "closed_at": last.get("completed_at") if last else run.get("started_at"),
            "last_batch": last.get("batch_id") if last else None,
            "closed_because": reason,
            "closure_observed_at": observed_at,
        })
        segments.append({
            "segment": len(segments) + 1,
            "app_version": app_version,
            "model_label": model_label,
            "opened_at": observed_at,
            "closed_at": None,
            "first_batch": None,
            "last_batch": None,
            "opened_because": reason,
            "authorized_by": authorized_by,
        })
        surface["surface_segments"] = segments
        surface["app_version"] = app_version
        surface["model_label"] = model_label
        surface["_provenance_note"] = (
            "app_version/model_label describe the CURRENT segment only. This run spans "
            "multiple surface segments; surface_segments is the authoritative per-segment "
            "record. Rotated by output/provenance_rotation.py (operator action) -- never by "
            "run_initializer.py, which is one-time by design."
        )
        _atomic_json(metadata_path, metadata)
        return {"rotated": True, "closed": current, "opened": segments[-1], "segments": segments}


def sync_open_segment(workspace, *, executor):
    """Stamp first_batch/last_batch on the open segment from the batch history.

    rotate_surface opens a segment before its first batch exists, so the batch
    bounds can only be filled in afterwards. Idempotent: re-running after each
    finalized batch just advances last_batch. Membership is decided by
    completed_at >= opened_at, never by batch number, because a segment can open
    while an earlier-numbered batch is still unfinalized in the other twin.
    """
    workspace = Path(workspace).expanduser().resolve(strict=True)
    if executor not in EXECUTORS or workspace.name != executor:
        raise RotationError(
            f"executor {executor!r} does not match workspace {workspace.name!r}"
        )
    metadata_path = workspace / "run_metadata.json"
    lock_path = workspace / "state" / ".run-metadata.lock"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        surface = (metadata.get("execution_surfaces") or {}).get(executor) or {}
        segments = surface.get("surface_segments")
        if not segments:
            return {"synced": False, "reason": "pack has no surface_segments; nothing to stamp"}
        open_segments = [s for s in segments if s.get("closed_at") is None]
        if len(open_segments) != 1:
            raise RotationError(f"expected exactly one open segment, found {len(open_segments)}")
        current = open_segments[0]
        opened = dt.datetime.fromisoformat(current["opened_at"])
        owned = [
            b for b in _batch_history(metadata)
            if b.get("completed_at")
            and dt.datetime.fromisoformat(b["completed_at"]) >= opened
        ]
        if not owned:
            return {"synced": False, "reason": "no batch finalized in the open segment yet"}
        before = (current.get("first_batch"), current.get("last_batch"))
        current["first_batch"] = owned[0]["batch_id"]
        current["last_batch"] = owned[-1]["batch_id"]
        current["batches_in_segment"] = len(owned)
        if before == (current["first_batch"], current["last_batch"]):
            return {"synced": False, "reason": "already current", "segment": current}
        _atomic_json(metadata_path, metadata)
        return {"synced": True, "segment": current}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--executor", choices=EXECUTORS, required=True)
    parser.add_argument("--sync-only", action="store_true",
                        help="stamp first_batch/last_batch on the open segment and exit")
    parser.add_argument("--app-version")
    parser.add_argument("--model-label")
    parser.add_argument("--observed-at")
    parser.add_argument("--reason")
    parser.add_argument("--authorized-by")
    args = parser.parse_args(argv)
    if args.sync_only:
        print(json.dumps(sync_open_segment(args.workspace, executor=args.executor),
                         indent=2, ensure_ascii=False))
        return
    if not (args.app_version and args.model_label and args.reason and args.authorized_by):
        parser.error("--app-version, --model-label, --reason and --authorized-by are required")
    result = rotate_surface(
        args.workspace,
        executor=args.executor,
        app_version=args.app_version,
        model_label=args.model_label,
        observed_at=args.observed_at,
        reason=args.reason,
        authorized_by=args.authorized_by,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
