import hashlib
import json
from pathlib import Path

import pytest

from field_contract import build_article_output_schema, build_stage3_supplement_schema
from pack_builder import BuildError, build_workspaces


REVISIONS = {
    "documentation_commit": "d" * 40,
    "code_commit": "c" * 40,
    "prompt_commit": "p" * 40,
    "prompt_tag": "v2.3.1-operational",
}


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _schema_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _fixture_root(tmp_path, *, filed=False, under="LocalResearch", n_proceeding=1):
    root = tmp_path / under / "level3_extraction"
    for name in ("PROTOCOL.md", "VALIDATION_PROTOCOL_C.md", "OSF_AMENDMENT_DRAFT.md"):
        _write(root / name, f"# {name}\n")

    for name in (
        "START_HERE.md",
        "MODEL_START_PROMPT.md",
        "SESSION_INSTRUCTIONS.md",
        "ORCHESTRATOR_PROTOCOL.md",
        "ARTICLE_AGENT_PROTOCOL.md",
    ):
        _write(root / "config" / name, f"# {name}\n")
    _write(
        root / "config" / "article_output.schema.json",
        _schema_text(build_article_output_schema()),
    )
    _write(
        root / "config" / "stage3_supplement.schema.json",
        _schema_text(build_stage3_supplement_schema()),
    )
    _write(root / "config" / "REPILOT_7_KEYS.json", '["rayyan-1"]\n')
    metadata = {
        "template_version": "1.0",
        "schema_version": "2.2.1",
        "validation_protocol": "C-2.3",
        "reviewer_gate": {
            "c23_signoff_date": "2026-07-14" if filed else None,
            "signed_by": "Bernardo Ribeiro",
        },
        "osf": {
            "registration_doi": "10.17605/OSF.IO/TDW6C",
            "amendment_filed_date": "2026-07-14" if filed else None,
            "amendment_url": "https://osf.io/example" if filed else None,
        },
        "source": {
            "documentation_commit": None,
            "code_commit": None,
            "prompt_commit": None,
            "prompt_tag": "v2.3.1-operational",
            "pack_manifest_sha256": None,
        },
        "execution_surfaces": {
            "claude": {"app_version": None, "model_label": None},
            "chatgpt": {"app_version": None, "model_label": None},
        },
        "run": {
            "run_id": None,
            "executor": None,
            "started_at": None,
            "working_directory": str(root),
            "batches": [],
        },
    }
    _write(root / "config" / "run_metadata_template.json", json.dumps(metadata))

    for name in ("stage1_system.md", "stage2_system.md", "stage3_system.md", "VERSION"):
        _write(root / "prompts" / name, f"{name}\n")

    for name in (
        "pack_builder.py",
        "pack_verifier.py",
        "batch_controller.py",
        "output_validator.py",
        "field_contract.py",
        "supplement_controller.py",
        "run_initializer.py",
        "review_controller.py",
        "repilot_revalidate.py",
        "local_storage.py",
        "grounding.py",
        "reconcile.py",
        "stage4_consolidate.py",
        "cross_checks.py",
        "audit_sampler.py",
        "residual_report.py",
        "fn_hunt.py",
        "review_evidence.py",
    ):
        _write(root / "output" / name, f"# {name}\n")
    for name in ("__init__.py", "README.md", "serve.py", "schema.py", "index.html", "app.js"):
        _write(root / "output" / "extraction_tool" / name, f"fixture {name}\n")

    for number in range(1, n_proceeding + 1):
        key = f"rayyan-{number}"
        pdf = root / "data" / "pdfs" / f"{key}.pdf"
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(f"fixture pdf {number}".encode())
        bundle = {
            "key": key,
            "proceeds_to_stage1": True,
            "pdf": {
                "available": True,
                "path": f"data/pdfs/{key}.pdf",
                "md5": hashlib.md5(pdf.read_bytes()).hexdigest(),
                "pages": [
                    {"page": 1, "text": "This eligible study applies a baseline model in a petroleum refinery."},
                    {
                        "page": 2,
                        "text": "The model uses production and temperature. R2 was 0.736.",
                    },
                ],
            },
        }
        _write(root / "output" / "stage0" / f"{key}.json", json.dumps(bundle))
    unavailable_number = n_proceeding + 1
    bundle_unavailable = {
        "key": f"rayyan-{unavailable_number}",
        "proceeds_to_stage1": False,
        "pdf": {"available": False, "path": None},
    }
    _write(
        root / "output" / "stage0" / f"rayyan-{unavailable_number}.json",
        json.dumps(bundle_unavailable),
    )
    return root


def test_development_build_creates_equal_model_packs_and_fail_closed_gate(tmp_path):
    root = _fixture_root(tmp_path, filed=False)
    result = build_workspaces(root, development=True, revisions=REVISIONS)

    chatgpt = root / "production" / "chatgpt"
    claude = root / "production" / "claude"
    assert result["production_ready"] is False
    assert "osf.amendment_filed_date" in result["gate_blockers"]
    assert (chatgpt / "AGENTS.md").read_bytes() == (chatgpt / "CLAUDE.md").read_bytes()
    assert (chatgpt / "MANIFEST.sha256").read_bytes() == (claude / "MANIFEST.sha256").read_bytes()
    assert json.loads((chatgpt / "state" / "pending_keys.json").read_text()) == ["rayyan-1"]
    inventory = json.loads((chatgpt / "CANONICAL_INPUTS.json").read_text())
    assert inventory["counts"] == {"pdfs": 1, "stage0_bundles": 2, "stage1_queue": 1}
    assert (chatgpt / "inputs" / "pdfs").resolve() == root / "data" / "pdfs"
    assert (chatgpt / "inputs" / "stage0").resolve() == root / "output" / "stage0"
    reviewer = root / "production" / "reviewer_workspace"
    assert (reviewer / "extraction_tool" / "serve.py").is_file()
    assert (reviewer / "extraction_tool" / "local_storage.py").is_file()
    assert (reviewer / "scripts" / "review_controller.py").is_file()
    assert (reviewer / "scripts" / "repilot_revalidate.py").is_file()
    assert (reviewer / "scripts" / "output_validator.py").is_file()
    assert (chatgpt / "scripts" / "field_contract.py").is_file()
    assert (reviewer / "field_contract.py").is_file()
    assert (reviewer / "review_evidence.py").is_file()
    assert (reviewer / "schemas" / "article_output.schema.json").is_file()


def test_builder_rejects_schema_snapshot_drift(tmp_path):
    root = _fixture_root(tmp_path, filed=False)
    _write(root / "config" / "article_output.schema.json", "{}\n")
    with pytest.raises(BuildError, match="schema snapshot drift"):
        build_workspaces(root, development=True, revisions=REVISIONS)


def test_production_build_refuses_unfiled_amendment(tmp_path):
    root = _fixture_root(tmp_path, filed=False)
    with pytest.raises(BuildError, match="amendment_filed_date"):
        build_workspaces(root, development=False, revisions=REVISIONS)


def test_production_build_accepts_filed_amendment(tmp_path):
    root = _fixture_root(tmp_path, filed=True)
    result = build_workspaces(root, development=False, revisions=REVISIONS)
    assert result["production_ready"] is True
    assert result["gate_blockers"] == []


def test_builder_rejects_desktop_or_icloud_source(tmp_path):
    with pytest.raises(BuildError, match="prohibited"):
        build_workspaces(
            Path("/Users/bernardoribeiro/Desktop/Screening/level3_extraction"),
            development=False,
            revisions=REVISIONS,
        )


def test_rebuild_archives_previous_workspaces(tmp_path):
    root = _fixture_root(tmp_path, filed=False)
    build_workspaces(root, development=True, revisions=REVISIONS, build_id="first")
    marker = root / "production" / "chatgpt" / "outputs" / "raw" / "marker.txt"
    _write(marker, "preserve me")
    build_workspaces(root, development=True, revisions=REVISIONS, build_id="second")
    archived = list((root / "production" / "archive").glob("*/chatgpt/outputs/raw/marker.txt"))
    assert len(archived) == 1
    assert archived[0].read_text() == "preserve me"


def test_development_repilot_queue_is_an_explicit_canonical_subset(tmp_path):
    root = _fixture_root(tmp_path, filed=False, n_proceeding=3)
    result = build_workspaces(
        root,
        development=True,
        revisions=REVISIONS,
        queue_keys=["rayyan-3", "rayyan-1"],
    )
    pending = json.loads(
        (root / "production" / "chatgpt" / "state" / "pending_keys.json").read_text()
    )
    assert pending == ["rayyan-1", "rayyan-3"]
    assert result["counts"]["stage1_queue"] == 2
    assert result["counts"]["canonical_stage1_queue"] == 3
    with pytest.raises(BuildError, match="development-only"):
        build_workspaces(
            root,
            development=False,
            revisions=REVISIONS,
            queue_keys=["rayyan-1"],
        )


def test_reviewer_workspace_ships_every_module_its_form_imports(tmp_path):
    """The reviewer form could not start at all from a built workspace (2026-08-24):
    pack_builder copied local_storage.py into extraction_tool/ but never shipped
    review_evidence.py, which serve.py resolves from the workspace root."""
    import ast
    import pack_builder

    tool = Path(pack_builder.__file__).resolve().parent / "extraction_tool" / "serve.py"
    tree = ast.parse(tool.read_text(encoding="utf-8"))
    bare = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            bare.add(node.module.split(".")[0])
    local = {m for m in bare if (tool.parent.parent / f"{m}.py").is_file()}
    assert "review_evidence" in local, "guard is stale: serve.py no longer imports it"

    src = Path(pack_builder.__file__).read_text(encoding="utf-8")
    for module in sorted(local):
        shipped = (
            f'path / "{module}.py"' in src
            or f'tool / "{module}.py"' in src
            or f'"{module}.py"' in src and "REVIEWER_SCRIPTS" in src
        )
        assert shipped, f"pack_builder never copies {module}.py into the reviewer workspace"
