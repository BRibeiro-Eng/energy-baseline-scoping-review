"""Build identical, file-backed model workspaces for interactive extraction.

Deterministic code only: this module never invokes a model.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from field_contract import check_schema_snapshots
from local_storage import StorageValidationError, is_prohibited, validate_required_paths


PROMPT_TAG = "v2.3.1-operational"
MODEL_PACKS = ("chatgpt", "claude")
DOCS = ("PROTOCOL.md", "VALIDATION_PROTOCOL_C.md", "OSF_AMENDMENT_DRAFT.md")
CONFIG_DOCS = (
    "START_HERE.md",
    "MODEL_START_PROMPT.md",
    "SESSION_INSTRUCTIONS.md",
    "ORCHESTRATOR_PROTOCOL.md",
    "ARTICLE_AGENT_PROTOCOL.md",
)
PROMPTS = ("stage1_system.md", "stage2_system.md", "stage3_system.md", "VERSION")
QUEUE_FILES = ("REPILOT_7_KEYS.json",)
RUNTIME_SCRIPTS = (
    "pack_builder.py",
    "pack_verifier.py",
    "batch_controller.py",
    "output_validator.py",
    "field_contract.py",
    "supplement_controller.py",
    "run_initializer.py",
    "local_storage.py",
    "grounding.py",
    "reconcile.py",
)
REVIEWER_SCRIPTS = (
    "review_controller.py",
    "repilot_revalidate.py",
    "output_validator.py",
    "field_contract.py",
    "reconcile.py",
    "pack_verifier.py",
    "local_storage.py",
    "stage4_consolidate.py",
    "grounding.py",
    "cross_checks.py",
    "audit_sampler.py",
    "residual_report.py",
    "fn_hunt.py",
)
EXTRACTION_TOOL_FILES = ("__init__.py", "README.md", "serve.py", "schema.py", "index.html", "app.js")
MANIFEST_EXCLUDED_TOP = {
    "inputs",
    "outputs",
    "state",
    "run_metadata.json",
    "MANIFEST.sha256",
    "PACK_LOCK.json",
}


class BuildError(RuntimeError):
    """The source tree or production gate cannot produce a valid pack."""


def _json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def _atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as stream:
        stream.write(_json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _md5(path: Path):
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args):
    proc = subprocess.run(
        ["git", "-C", str(root), *args], text=True, capture_output=True
    )
    if proc.returncode:
        raise BuildError(f"git {' '.join(args)} failed in {root}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def source_revisions(root: Path):
    prompt_head = _git(root / "prompts", "rev-parse", "HEAD")
    prompt_tag_head = _git(root / "prompts", "rev-parse", f"{PROMPT_TAG}^{{}}")
    if prompt_head != prompt_tag_head:
        raise BuildError(f"prompt HEAD is not tagged {PROMPT_TAG}")
    return {
        "documentation_commit": _git(root, "rev-parse", "HEAD"),
        "code_commit": _git(root / "output", "rev-parse", "HEAD"),
        "prompt_commit": prompt_head,
        "prompt_tag": PROMPT_TAG,
        "documentation_dirty": bool(_git(root, "status", "--porcelain", "--untracked-files=no")),
        "code_dirty": bool(_git(root / "output", "status", "--porcelain", "--untracked-files=no")),
        "prompt_dirty": bool(_git(root / "prompts", "status", "--porcelain", "--untracked-files=no")),
    }


def _required_sources(root: Path):
    files = [root / name for name in DOCS]
    files += [root / "config" / name for name in CONFIG_DOCS]
    files += [root / "config" / name for name in QUEUE_FILES]
    files += [
        root / "config" / "article_output.schema.json",
        root / "config" / "stage3_supplement.schema.json",
        root / "config" / "run_metadata_template.json",
    ]
    files += [root / "prompts" / name for name in PROMPTS]
    files += [root / "output" / name for name in RUNTIME_SCRIPTS]
    files += [root / "output" / name for name in REVIEWER_SCRIPTS]
    files += [root / "output" / "extraction_tool" / name for name in EXTRACTION_TOOL_FILES]
    return files


def _input_inventory(root: Path, queue_keys=None):
    pdfs = sorted((root / "data" / "pdfs").glob("*.pdf"))
    bundles = sorted((root / "output" / "stage0").glob("rayyan-*.json"))
    try:
        checked = validate_required_paths(root, [*pdfs, *bundles])
    except StorageValidationError as exc:
        raise BuildError(str(exc)) from exc

    queue = []
    bundle_rows = {}
    for path in bundles:
        try:
            bundle = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BuildError(f"invalid Stage-0 bundle {path}: {exc}") from exc
        key = bundle.get("key")
        if path.stem != key:
            raise BuildError(f"Stage-0 key/path mismatch: {path.stem} != {key}")
        if bundle.get("proceeds_to_stage1") is True:
            queue.append(key)
        pdf = bundle.get("pdf") or {}
        if pdf.get("available"):
            expected = root / "data" / "pdfs" / f"{key}.pdf"
            if not expected.is_file():
                raise BuildError(f"available bundle has no canonical PDF: {key}")
            if pdf.get("md5") and _md5(expected) != pdf["md5"]:
                raise BuildError(f"Stage-0/PDF MD5 mismatch: {key}")
        bundle_rows[key] = checked["files"][str(path.relative_to(root))]

    pdf_rows = {
        path.stem: checked["files"][str(path.relative_to(root))] for path in pdfs
    }
    canonical_queue = sorted(queue)
    active_queue = canonical_queue
    queue_scope = "full"
    if queue_keys is not None:
        if not isinstance(queue_keys, (list, tuple)) or any(
            not isinstance(key, str) for key in queue_keys
        ):
            raise BuildError("queue_keys must be a list of paper keys")
        if len(queue_keys) != len(set(queue_keys)):
            raise BuildError("queue_keys contains duplicates")
        unknown = sorted(set(queue_keys) - set(canonical_queue))
        if unknown:
            raise BuildError(f"queue key is outside canonical Stage-1 queue: {unknown[0]}")
        active_queue = sorted(queue_keys)
        queue_scope = "development_subset"
    counts = {
        "pdfs": len(pdfs),
        "stage0_bundles": len(bundles),
        "stage1_queue": len(active_queue),
    }
    if queue_keys is not None:
        counts["canonical_stage1_queue"] = len(canonical_queue)
    inventory = {
        "version": "1.0",
        "canonical_root": str(root),
        "queue_scope": queue_scope,
        "counts": counts,
        "stage1_keys": active_queue,
        "pdf_sha256": pdf_rows,
        "stage0_sha256": bundle_rows,
    }
    inventory["inventory_sha256"] = hashlib.sha256(_json_bytes(inventory)).hexdigest()
    return inventory


def _copy_sources(root: Path, pack: Path):
    for name in DOCS:
        shutil.copy2(root / name, pack / name)
    for name in CONFIG_DOCS:
        target = "AGENTS.md" if name == "SESSION_INSTRUCTIONS.md" else name
        shutil.copy2(root / "config" / name, pack / target)
        if name == "SESSION_INSTRUCTIONS.md":
            shutil.copy2(root / "config" / name, pack / "CLAUDE.md")
    (pack / "config").mkdir()
    shutil.copy2(
        root / "config" / "run_metadata_template.json",
        pack / "config" / "run_metadata_template.json",
    )
    for name in QUEUE_FILES:
        shutil.copy2(root / "config" / name, pack / "config" / name)
    (pack / "schemas").mkdir()
    shutil.copy2(
        root / "config" / "article_output.schema.json",
        pack / "schemas" / "article_output.schema.json",
    )
    shutil.copy2(
        root / "config" / "stage3_supplement.schema.json",
        pack / "schemas" / "stage3_supplement.schema.json",
    )
    (pack / "prompts").mkdir()
    for name in PROMPTS:
        shutil.copy2(root / "prompts" / name, pack / "prompts" / name)
    (pack / "scripts").mkdir()
    for name in RUNTIME_SCRIPTS:
        shutil.copy2(root / "output" / name, pack / "scripts" / name)


def _write_runtime(pack: Path, root: Path, inventory):
    (pack / "inputs").mkdir()
    (pack / "inputs" / "pdfs").symlink_to(root / "data" / "pdfs", target_is_directory=True)
    (pack / "inputs" / "stage0").symlink_to(root / "output" / "stage0", target_is_directory=True)
    for path in (
        pack / "outputs" / "raw",
        pack / "outputs" / "validated",
        pack / "outputs" / "validation_reports",
        pack / "outputs" / "agent_reports",
        pack / "outputs" / "quarantine",
        pack / "state" / "batches",
        pack / "state" / "control_inbox",
    ):
        path.mkdir(parents=True, exist_ok=True)
    state = pack / "state"
    _atomic_json(state / "pending_keys.json", inventory["stage1_keys"])
    _atomic_json(state / "completed_keys.json", [])
    _atomic_json(state / "failed_keys.json", [])
    _atomic_json(state / "active_batch.json", None)
    _atomic_json(state / "proposed_batch.json", None)
    _atomic_json(state / "progress_summary.json", {
        "pending": len(inventory["stage1_keys"]), "active": 0, "completed": 0, "failed": 0
    })
    _atomic_json(state / "stage3_supplement_plan.json", {
        "roster_version": None, "blocked": True, "reason": "no human roster receipt", "keys": []
    })
    (state / "NEXT_SESSION.md").write_text(
        "No batch has been authorized. Verify the pack, inspect status, and propose the next batch.\n",
        encoding="utf-8",
    )


def _manifest(pack: Path):
    rows = []
    for path in sorted(pack.rglob("*")):
        rel = path.relative_to(pack)
        if rel.parts[0] in MANIFEST_EXCLUDED_TOP or not path.is_file():
            continue
        rows.append(f"{_sha256(path)}  {rel.as_posix()}")
    data = ("\n".join(rows) + "\n").encode()
    (pack / "MANIFEST.sha256").write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _gate_blockers(metadata, revisions):
    candidates = {
        "reviewer_gate.c23_signoff_date": (metadata.get("reviewer_gate") or {}).get("c23_signoff_date"),
        "osf.amendment_filed_date": (metadata.get("osf") or {}).get("amendment_filed_date"),
        "osf.amendment_url": (metadata.get("osf") or {}).get("amendment_url"),
        "source.documentation_commit": revisions.get("documentation_commit"),
        "source.code_commit": revisions.get("code_commit"),
        "source.prompt_commit": revisions.get("prompt_commit"),
        "source.prompt_tag": revisions.get("prompt_tag"),
    }
    blockers = [name for name, value in candidates.items() if not value]
    blockers += [
        f"source.{name}" for name in ("documentation_dirty", "code_dirty", "prompt_dirty")
        if revisions.get(name)
    ]
    return blockers


def _reviewer_workspace(path: Path, root: Path, revisions, inventory, build_id):
    for name in ("imports/chatgpt", "imports/claude", "queues", "roster_exports", "reviews", "reports", "state"):
        (path / name).mkdir(parents=True, exist_ok=True)
    (path / "README.md").write_text(
        "# Reviewer workspace\n\n"
        "Model outputs are imported here only by deterministic review tooling.\n\n"
        "## Deterministic sequence\n\n"
        "```bash\n"
        "python3 scripts/review_controller.py import --production-root ..\n"
        "python3 scripts/review_controller.py reconcile --reviewer-workspace .\n"
        "# Prepare decisions/FN-census/assignment JSON only at the applicable protocol gate.\n"
        "python3 scripts/review_controller.py materialize --reviewer-workspace . "
        "--assignments assignments.json --canonical-root ../..\n"
        "```\n\n"
        "Run the local reviewer UI against one materialized leaf dataset, for example:\n\n"
        "```bash\n"
        "python3 extraction_tool/serve.py --canonical-root ../.. "
        "--data-root reviews/membership/blind\n"
        "```\n\n"
        "After all required reviews and the roster/supplement gates close:\n\n"
        "```bash\n"
        "python3 scripts/stage4_consolidate.py --reviewer-workspace . --canonical-root ../..\n"
        "```\n",
        encoding="utf-8",
    )
    _atomic_json(path / "REVIEWER_LOCK.json", {
        "build_id": build_id,
        "source": revisions,
        "canonical_input_inventory_sha256": inventory["inventory_sha256"],
        "canonical_root": str(root),
    })
    scripts = path / "scripts"
    scripts.mkdir()
    for name in REVIEWER_SCRIPTS:
        shutil.copy2(root / "output" / name, scripts / name)
    shutil.copy2(root / "output" / "field_contract.py", path / "field_contract.py")
    # extraction_tool/serve.py resolves review_evidence via Path(__file__).parent.parent,
    # i.e. the workspace root -- same placement rule as field_contract above. Omitting it
    # produced a workspace whose reviewer form could not start at all (2026-08-24).
    shutil.copy2(root / "output" / "review_evidence.py", path / "review_evidence.py")
    schemas = path / "schemas"
    schemas.mkdir()
    for name in ("article_output.schema.json", "stage3_supplement.schema.json"):
        shutil.copy2(root / "config" / name, schemas / name)
    tool = path / "extraction_tool"
    tool.mkdir()
    for name in EXTRACTION_TOOL_FILES:
        shutil.copy2(root / "output" / "extraction_tool" / name, tool / name)
    shutil.copy2(root / "output" / "local_storage.py", tool / "local_storage.py")


def build_workspaces(
    source_root, *, development=False, revisions=None, build_id=None, queue_keys=None
):
    source_root = Path(source_root).expanduser()
    if is_prohibited(source_root):
        raise BuildError(f"prohibited source root: {source_root}")
    try:
        root = source_root.resolve(strict=True)
    except OSError as exc:
        raise BuildError(f"missing source root: {source_root}") from exc
    if is_prohibited(root):
        raise BuildError(f"prohibited source root: {root}")
    if queue_keys is not None and not development:
        raise BuildError("a queue subset is development-only")

    drifted = check_schema_snapshots(root)
    if drifted:
        relative = ", ".join(str(path.relative_to(root)) for path in drifted)
        raise BuildError(f"schema snapshot drift: {relative}")

    try:
        validate_required_paths(root, _required_sources(root))
    except StorageValidationError as exc:
        raise BuildError(str(exc)) from exc

    revisions = dict(revisions or source_revisions(root))
    metadata = json.loads((root / "config" / "run_metadata_template.json").read_text())
    blockers = _gate_blockers(metadata, revisions)
    if blockers and not development:
        raise BuildError("production gate blocked: " + ", ".join(blockers))

    inventory = _input_inventory(root, queue_keys=queue_keys)
    build_id = build_id or dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    if not build_id.replace("-", "").replace("_", "").replace("+", "").isalnum():
        raise BuildError(f"invalid build_id: {build_id}")

    production = root / "production"
    production.mkdir(exist_ok=True)
    temp_root = production / f".build-{build_id}"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    temp_root.mkdir()
    try:
        manifest_hash = None
        for family in MODEL_PACKS:
            pack = temp_root / family
            pack.mkdir()
            _copy_sources(root, pack)
            _atomic_json(pack / "CANONICAL_INPUTS.json", inventory)
            _write_runtime(pack, root, inventory)
            current_manifest = _manifest(pack)
            if manifest_hash is None:
                manifest_hash = current_manifest
            elif current_manifest != manifest_hash:
                raise BuildError("model-pack immutable manifests differ during build")
            run_metadata = json.loads((pack / "config" / "run_metadata_template.json").read_text())
            run_metadata["source"].update(revisions)
            run_metadata["source"]["pack_manifest_sha256"] = current_manifest
            run_metadata["run"]["working_directory"] = str(production / family)
            _atomic_json(pack / "run_metadata.json", run_metadata)
            _atomic_json(pack / "PACK_LOCK.json", {
                "build_id": build_id,
                "development_build": bool(development),
                "production_ready": not blockers,
                "gate_blockers": blockers,
                "source": revisions,
                "schema_version": "2.2.1",
                "validation_protocol": "C-2.3",
                "prompt_tag": PROMPT_TAG,
                "immutable_manifest_sha256": current_manifest,
                "canonical_input_inventory_sha256": inventory["inventory_sha256"],
                "queue_scope": inventory["queue_scope"],
            })

        _reviewer_workspace(temp_root / "reviewer_workspace", root, revisions, inventory, build_id)

        existing = [name for name in (*MODEL_PACKS, "reviewer_workspace") if (production / name).exists()]
        if existing:
            archive = production / "archive" / f"pre-{build_id}"
            archive.mkdir(parents=True, exist_ok=False)
            for name in existing:
                os.replace(production / name, archive / name)
        for name in (*MODEL_PACKS, "reviewer_workspace"):
            os.replace(temp_root / name, production / name)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)

    return {
        "build_id": build_id,
        "production_root": str(production),
        "production_ready": not blockers,
        "gate_blockers": blockers,
        "immutable_manifest_sha256": manifest_hash,
        "canonical_input_inventory_sha256": inventory["inventory_sha256"],
        "counts": inventory["counts"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--queue-file", type=Path)
    args = parser.parse_args(argv)
    queue_keys = None
    if args.queue_file:
        loaded = json.loads(args.queue_file.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            queue_keys = loaded.get("selected_keys_total") or loaded.get("selected_keys")
        else:
            queue_keys = loaded
    result = build_workspaces(
        args.source_root, development=args.development, queue_keys=queue_keys
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
