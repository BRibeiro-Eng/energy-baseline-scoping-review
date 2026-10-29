"""Fail-closed verifier for generated interactive extraction workspaces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from local_storage import is_dataless, is_prohibited


MANIFEST_EXCLUDED_TOP = {"inputs", "outputs", "state"}
MANIFEST_EXCLUDED_FILES = {"run_metadata.json", "MANIFEST.sha256", "PACK_LOCK.json"}


class VerificationError(RuntimeError):
    """A workspace, manifest, input, or runtime gate is invalid."""


def _sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_hash(value):
    data = (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"invalid JSON {path}: {exc}") from exc


def _manifest_rows(workspace: Path):
    manifest = workspace / "MANIFEST.sha256"
    if not manifest.is_file() or is_dataless(manifest):
        raise VerificationError("missing or dataless MANIFEST.sha256")
    rows = []
    for number, line in enumerate(manifest.read_text().splitlines(), 1):
        try:
            expected, rel = line.split("  ", 1)
        except ValueError as exc:
            raise VerificationError(f"malformed manifest line {number}") from exc
        supplied = Path(rel)
        if supplied.is_absolute() or ".." in supplied.parts:
            raise VerificationError(f"unsafe manifest path: {rel}")
        path = workspace / supplied
        if not path.is_file() or is_dataless(path):
            raise VerificationError(f"missing or dataless immutable file: {rel}")
        actual = _sha256(path)
        if actual != expected:
            raise VerificationError(f"immutable hash mismatch: {rel}")
        rows.append(rel)
    manifested = set(rows)
    discovered = set()
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(workspace)
        if "__pycache__" in rel.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
            continue
        if rel.parts[0] in MANIFEST_EXCLUDED_TOP or rel.as_posix() in MANIFEST_EXCLUDED_FILES:
            continue
        discovered.add(rel.as_posix())
    extras = sorted(discovered - manifested)
    missing = sorted(manifested - discovered)
    if extras:
        raise VerificationError(f"unmanifested immutable file: {extras[0]}")
    if missing:
        raise VerificationError(f"manifest lists undiscoverable immutable file: {missing[0]}")
    return manifest, rows


def _runtime_blockers(metadata, lock):
    blockers = list(lock.get("gate_blockers") or [])
    run = metadata.get("run") or {}
    executor = run.get("executor")
    for name, value in (
        ("run.run_id", run.get("run_id")),
        ("run.executor", executor),
        ("run.started_at", run.get("started_at")),
    ):
        if not value:
            blockers.append(name)
    if executor in ("claude", "chatgpt"):
        surface = (metadata.get("execution_surfaces") or {}).get(executor) or {}
        if not surface.get("app_version"):
            blockers.append(f"execution_surfaces.{executor}.app_version")
        if not surface.get("model_label"):
            blockers.append(f"execution_surfaces.{executor}.model_label")
    elif executor:
        blockers.append("run.executor.invalid")
    return sorted(set(blockers))


def _verify_inputs(workspace: Path, inventory, lock):
    canonical_root = Path(inventory.get("canonical_root", "")).expanduser().resolve(strict=False)
    if is_prohibited(canonical_root):
        raise VerificationError(f"prohibited canonical root: {canonical_root}")
    expected_links = {
        "pdfs": canonical_root / "data" / "pdfs",
        "stage0": canonical_root / "output" / "stage0",
    }
    for name, expected in expected_links.items():
        link = workspace / "inputs" / name
        if not link.is_symlink() or link.resolve(strict=False) != expected:
            raise VerificationError(f"input link mismatch: {name}")
        if not expected.is_dir() or is_prohibited(expected):
            raise VerificationError(f"missing or prohibited input directory: {expected}")

    pdf_rows = inventory.get("pdf_sha256") or {}
    stage0_rows = inventory.get("stage0_sha256") or {}
    if len(list(expected_links["pdfs"].glob("*.pdf"))) != len(pdf_rows):
        raise VerificationError("canonical PDF count mismatch")
    if len(list(expected_links["stage0"].glob("rayyan-*.json"))) != len(stage0_rows):
        raise VerificationError("canonical Stage-0 count mismatch")
    for key, expected_hash in pdf_rows.items():
        path = expected_links["pdfs"] / f"{key}.pdf"
        if not path.is_file() or is_dataless(path) or _sha256(path) != expected_hash:
            raise VerificationError(f"canonical PDF hash mismatch: {key}")
    for key, expected_hash in stage0_rows.items():
        path = expected_links["stage0"] / f"{key}.json"
        if not path.is_file() or is_dataless(path) or _sha256(path) != expected_hash:
            raise VerificationError(f"canonical Stage-0 hash mismatch: {key}")

    embedded = dict(inventory)
    recorded = embedded.pop("inventory_sha256", None)
    actual = _canonical_hash(embedded)
    if not recorded or recorded != actual:
        raise VerificationError("canonical inventory self-hash mismatch")
    if lock.get("canonical_input_inventory_sha256") != recorded:
        raise VerificationError("PACK_LOCK canonical inventory hash mismatch")


def verify_workspace(workspace, *, require_production=False):
    workspace = Path(workspace).expanduser()
    if is_prohibited(workspace):
        raise VerificationError(f"prohibited workspace: {workspace}")
    try:
        workspace = workspace.resolve(strict=True)
    except OSError as exc:
        raise VerificationError(f"missing workspace: {workspace}") from exc
    if is_prohibited(workspace):
        raise VerificationError(f"prohibited workspace: {workspace}")

    lock = _load_json(workspace / "PACK_LOCK.json")
    manifest, rows = _manifest_rows(workspace)
    manifest_hash = _sha256(manifest)
    if manifest_hash != lock.get("immutable_manifest_sha256"):
        raise VerificationError("PACK_LOCK manifest hash mismatch")

    inventory = _load_json(workspace / "CANONICAL_INPUTS.json")
    _verify_inputs(workspace, inventory, lock)
    metadata = _load_json(workspace / "run_metadata.json")
    source = metadata.get("source") or {}
    for field in ("documentation_commit", "code_commit", "prompt_commit", "prompt_tag"):
        if source.get(field) != (lock.get("source") or {}).get(field):
            raise VerificationError(f"run metadata/source mismatch: {field}")
    if source.get("pack_manifest_sha256") != manifest_hash:
        raise VerificationError("run metadata manifest mismatch")

    blockers = _runtime_blockers(metadata, lock)
    if require_production and blockers:
        raise VerificationError("production gate blocked: " + ", ".join(blockers))
    return {
        "ok": True,
        "workspace": str(workspace),
        "immutable_files": len(rows),
        "immutable_manifest_sha256": manifest_hash,
        "canonical_input_inventory_sha256": inventory["inventory_sha256"],
        "counts": inventory["counts"],
        "production_ready": not blockers,
        "runtime_blockers": blockers,
    }


def verify_twin_packs(production_root, *, require_production=False):
    production_root = Path(production_root)
    chatgpt = verify_workspace(production_root / "chatgpt", require_production=require_production)
    claude = verify_workspace(production_root / "claude", require_production=require_production)
    if chatgpt["immutable_manifest_sha256"] != claude["immutable_manifest_sha256"]:
        raise VerificationError("twin immutable manifest hashes differ")
    if (production_root / "chatgpt" / "MANIFEST.sha256").read_bytes() != (
        production_root / "claude" / "MANIFEST.sha256"
    ).read_bytes():
        raise VerificationError("twin manifest contents differ")
    if chatgpt["canonical_input_inventory_sha256"] != claude["canonical_input_inventory_sha256"]:
        raise VerificationError("twin canonical inventories differ")
    return {
        "ok": True,
        "equal_manifests": True,
        "immutable_manifest_sha256": chatgpt["immutable_manifest_sha256"],
        "chatgpt": chatgpt,
        "claude": claude,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--production-root", type=Path)
    parser.add_argument("--require-production", action="store_true")
    args = parser.parse_args(argv)
    if bool(args.workspace) == bool(args.production_root):
        parser.error("provide exactly one of --workspace or --production-root")
    if args.workspace:
        result = verify_workspace(args.workspace, require_production=args.require_production)
    else:
        result = verify_twin_packs(args.production_root, require_production=args.require_production)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
