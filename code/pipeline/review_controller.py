"""Isolated reviewer-side import, reconciliation, and Corpus-B roster locking."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import random
from pathlib import Path

from pack_verifier import VerificationError, verify_twin_packs
from reconcile import reconcile_record


MEMBERSHIP_FIELDS = {"methodological_eligibility", "level_3b"}
REMAINING_TIER1_FIELDS = {"paper_type", "borderline_review_synthesis_eligibility"}
INITIAL_FILE = re.compile(r"^rayyan-\d+\.json$")
SUPPLEMENT_FILE = re.compile(r"^rayyan-\d+\.stage3-supplement\.json$")


class ReviewError(RuntimeError):
    """Reviewer inputs are incomplete, inconsistent, or non-immutable."""


def _now():
    import datetime as dt
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


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
    path.parent.mkdir(parents=True, exist_ok=True)
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
        raise ReviewError(f"invalid reviewer input {path}: {exc}") from exc


def import_validated_outputs(production_root):
    production_root = Path(production_root).resolve(strict=True)
    try:
        verify_twin_packs(production_root)
    except VerificationError as exc:
        raise ReviewError(str(exc)) from exc
    reviewer = production_root / "reviewer_workspace"
    counts, manifests, supplement_manifests = {}, {}, {}
    for family in ("chatgpt", "claude"):
        source_dir = production_root / family / "outputs" / "validated"
        target_dir = reviewer / "imports" / family
        target_dir.mkdir(parents=True, exist_ok=True)
        rows = {}
        for source in sorted(path for path in source_dir.glob("rayyan-*.json") if INITIAL_FILE.fullmatch(path.name)):
            target = target_dir / source.name
            data = source.read_bytes()
            if target.exists():
                if target.read_bytes() != data:
                    raise ReviewError(f"immutable import differs: {family}/{source.name}")
            else:
                with target.open("xb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            rows[source.stem] = _sha256(source)
        counts[family] = len(rows)
        manifests[family] = rows
        supplement_rows = {}
        supplement_target = target_dir / "supplements"
        supplement_target.mkdir(exist_ok=True)
        for source in sorted(
            path for path in source_dir.glob("rayyan-*.stage3-supplement.json")
            if SUPPLEMENT_FILE.fullmatch(path.name)
        ):
            target = supplement_target / source.name
            data = source.read_bytes()
            if target.exists():
                if target.read_bytes() != data:
                    raise ReviewError(f"immutable supplement import differs: {family}/{source.name}")
            else:
                with target.open("xb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            supplement_rows[source.stem] = _sha256(source)
        supplement_manifests[family] = supplement_rows
    _atomic_json(reviewer / "state" / "import_manifest.json", {
        "imported_at": _now(), "counts": counts, "sha256": manifests,
        "supplement_sha256": supplement_manifests,
    })
    return counts


def _value(envelope):
    return envelope.get("value") if isinstance(envelope, dict) else envelope


def _value_record(record):
    stage1 = record.get("stage1") or {}
    eligibility = {
        "methodological_eligibility": _value(stage1.get("methodological_eligibility")),
        "paper_type": _value(stage1.get("paper_type")),
        "borderline_review_synthesis_eligibility": stage1.get(
            "borderline_review_synthesis_eligibility"
        ),
        "level_3b": _value(stage1.get("level_3b")),
    }
    return {
        "key": record.get("paper_key"),
        "eligibility": eligibility,
        "level_a": {name: _value(env) for name, env in (record.get("stage2") or {}).items()},
        "level_b": {name: _value(env) for name, env in (record.get("stage3") or {}).items()},
    }


def reconcile_imports(reviewer_workspace):
    reviewer = Path(reviewer_workspace).resolve(strict=True)
    files = {
        family: {
            path.stem: path
            for path in (reviewer / "imports" / family).glob("rayyan-*.json")
            if INITIAL_FILE.fullmatch(path.name)
        }
        for family in ("chatgpt", "claude")
    }
    common = sorted(set(files["chatgpt"]) & set(files["claude"]))
    only = {
        "chatgpt": sorted(set(files["chatgpt"]) - set(files["claude"])),
        "claude": sorted(set(files["claude"]) - set(files["chatgpt"])),
    }
    queues = {
        "tier1_membership": [],
        "tier1_remaining": [],
        "tier2": [],
        "tier2_pending_model_coverage": [],
        "tier3": [],
    }
    summaries = {}
    recon_dir = reviewer / "state" / "reconciled"
    recon_dir.mkdir(parents=True, exist_ok=True)
    for key in common:
        chat = _load(files["chatgpt"][key])
        claude = _load(files["claude"][key])
        reconciliation = reconcile_record(_value_record(chat), _value_record(claude))
        _atomic_json(recon_dir / f"{key}.json", reconciliation)
        summaries[key] = reconciliation["summary"]
        both_stage3 = isinstance(chat.get("stage3"), dict) and isinstance(claude.get("stage3"), dict)
        if not both_stage3 and (chat.get("stage3") is not None or claude.get("stage3") is not None):
            queues["tier2_pending_model_coverage"].append(key)
        for field in reconciliation["fields"]:
            if field["agree"]:
                continue
            item = {
                "paper_key": key,
                "section": field["section"],
                "field": field["field"],
                "chatgpt": field["a"],
                "claude": field["b"],
                "tier": field["tier"],
            }
            if field["field"] in MEMBERSHIP_FIELDS:
                queues["tier1_membership"].append(item)
            elif field["field"] in REMAINING_TIER1_FIELDS:
                queues["tier1_remaining"].append(item)
            elif field["tier"] == 2:
                if both_stage3:
                    queues["tier2"].append(item)
            else:
                queues["tier3"].append(item)
    for name, values in queues.items():
        _atomic_json(reviewer / "queues" / f"{name}.json", values)
    result = {
        "reconciled_at": _now(),
        "common_keys": len(common),
        "missing_counterpart": only,
        "queue_counts": {name: len(values) for name, values in queues.items()},
        "summaries": summaries,
    }
    _atomic_json(reviewer / "state" / "reconciliation_summary.json", result)
    return result


def corpus_b_branch(size):
    if not isinstance(size, int) or size < 0:
        raise ReviewError("Corpus-B size must be a non-negative integer")
    if size <= 40:
        return {
            "name": "integral_blind_first",
            "roster_size": size,
            "blind_first_n": size,
            "prefill_verification_n": 0,
            "n_sub": max(0, size - 25) if size > 25 else 0,
            "paused": False,
        }
    if size <= 60:
        return {
            "name": "hybrid",
            "roster_size": size,
            "blind_first_n": 40,
            "prefill_verification_n": size - 40,
            "n_sub": 15,
            "paused": False,
        }
    return {
        "name": "paused_over_60",
        "roster_size": size,
        "blind_first_n": 0,
        "prefill_verification_n": size,
        "n_sub": None,
        "paused": True,
    }


def select_level_b_assignments(records, *, missing_comparison_keys=(), seed=44):
    """Select C-2.3 Tier-2 blind/verification routes from a locked roster.

    `records` contains key, sector_of_activity, and year for every roster item.
    Missing model coverage forces blind-first fallback even if the item would
    otherwise be in the non-blind verification remainder.
    """
    records = list(records)
    keys = [row.get("key") for row in records]
    if any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
        raise ReviewError("Level-B roster records require unique string keys")
    branch = corpus_b_branch(len(records))
    if branch["paused"]:
        raise ReviewError("Corpus-B branch is paused over 60 before Level-B work")

    def priority(row):
        sector = str(row.get("sector_of_activity") or "").lower()
        group = 0 if "refin" in sector else 1 if "petrochem" in sector else 2
        try:
            year = int(row.get("year") or 0)
        except (TypeError, ValueError):
            year = 0
        return (group, 0 if year >= 2020 else 1, -year, row["key"])

    ordered = sorted(records, key=priority)
    if len(records) <= 25:
        head = ordered
        sampled = []
    else:
        head = ordered[:25]
        remainder = sorted(row["key"] for row in ordered[25:])
        n_sub = min(15, len(remainder))
        sampled = sorted(random.Random(seed).sample(remainder, n_sub))
    priority_keys = [row["key"] for row in head]
    blind = set(priority_keys) | set(sampled)
    verification = set(keys) - blind
    fallback = verification & set(missing_comparison_keys)
    blind |= fallback
    verification -= fallback
    return {
        "branch": branch,
        "seed": seed,
        "priority_head_keys": priority_keys,
        "random_subsample_keys": sampled,
        "fallback_blind_keys": sorted(fallback),
        "blind_first_keys": sorted(blind),
        "verification_keys": sorted(verification),
    }


def _form_schema():
    here = Path(__file__).resolve().parent
    candidates = (here / "extraction_tool" / "schema.py", here.parent / "extraction_tool" / "schema.py")
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        raise ReviewError("reviewer form schema is unavailable")
    spec = importlib.util.spec_from_file_location("c23_reviewer_form_schema", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SCHEMA


def _empty_form_blocks():
    blocks = {}
    for section, section_spec in _form_schema().items():
        blocks[section] = {
            field["name"]: [] if field["type"] in ("multienum", "list_str", "list_obj") else None
            for field in section_spec["fields"]
        }
    return blocks


def materialize_review_assignments(
    reviewer_workspace, assignments, *, canonical_root=None
):
    """Create auditable reviewer forms and separate dual-model sidecars.

    Blind assignments leave targeted values empty and withhold both sidecars.
    Verification assignments prefill only target cells on which both models
    agree; divergent target cells stay empty while both model values are shown.
    """
    reviewer = Path(reviewer_workspace).resolve(strict=True)
    lock = _load(reviewer / "REVIEWER_LOCK.json")
    root = Path(canonical_root or lock.get("canonical_root", "")).resolve(strict=True)
    if Path(lock.get("canonical_root", "")).resolve(strict=False) != root:
        raise ReviewError("canonical root does not match REVIEWER_LOCK")
    valid_fields = {
        f"{section}.{field['name']}"
        for section, spec in _form_schema().items() for field in spec["fields"]
    }
    created, reused, manifest = 0, 0, []
    for assignment in assignments:
        key = assignment.get("paper_key")
        phase = assignment.get("phase")
        wave = assignment.get("wave")
        fields = sorted(set(assignment.get("review_fields") or []))
        if not re.fullmatch(r"rayyan-\d+", str(key)):
            raise ReviewError(f"invalid review paper key: {key}")
        if phase not in ("blind", "verification"):
            raise ReviewError(f"invalid review phase: {phase}")
        if wave is not None and not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", str(wave)):
            raise ReviewError(f"invalid review wave: {wave}")
        if not fields or not set(fields) <= valid_fields:
            raise ReviewError(f"invalid or empty review fields for {key}")
        bundle = _load(root / "output" / "stage0" / f"{key}.json")
        model_values = {}
        for family in ("chatgpt", "claude"):
            path = reviewer / "imports" / family / f"{key}.json"
            if not path.is_file():
                raise ReviewError(f"missing reviewer import: {family}/{key}")
            initial = _load(path)
            supplement_path = (
                reviewer / "imports" / family / "supplements"
                / f"{key}.stage3-supplement.json"
            )
            supplement = _load(supplement_path) if supplement_path.is_file() else None
            model_values[family] = _value_record(initial)
            if model_values[family]["level_b"] == {} and supplement is not None:
                model_values[family]["level_b"] = {
                    name: _value(envelope)
                    for name, envelope in (supplement.get("stage3") or {}).items()
                }
        blocks = _empty_form_blocks()
        methodological = [
            model_values[family]["eligibility"].get("methodological_eligibility")
            for family in ("chatgpt", "claude")
        ]
        if methodological[0] == methodological[1] and "eligibility.methodological_eligibility" not in fields:
            blocks["eligibility"]["methodological_eligibility"] = methodological[0]
        if phase == "verification":
            for fq in fields:
                section, field = fq.split(".", 1)
                pair = [model_values[family].get(section, {}).get(field) for family in ("chatgpt", "claude")]
                if pair[0] == pair[1]:
                    blocks[section][field] = copy.deepcopy(pair[0])
        metadata = bundle.get("metadata") or {}
        template = {
            "key": key,
            "_phase": phase,
            "_blind_required": phase == "blind",
            "_review_fields": fields,
            "metadata": {
                "title": metadata.get("title", key),
                "authors": metadata.get("authors", ""),
                "year": metadata.get("year"),
                "source": metadata.get("source", ""),
                "rayyan_decision": metadata.get("rayyan_decision", ""),
            },
            **blocks,
            "reviewer_notes": "",
            "reviewer_evidence": {},
            "_done": False,
        }
        sidecar = {"models": model_values}
        target_dir = reviewer / "reviews" / (str(wave) if wave else "") / phase
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{key}.json"
        ai_target = target_dir / f"{key}.ai.json"
        if target.exists() or ai_target.exists():
            if not target.is_file() or not ai_target.is_file():
                raise ReviewError(f"partial reviewer assignment exists: {phase}/{key}")
            if target.read_bytes() != _canonical(template) or ai_target.read_bytes() != _canonical(sidecar):
                raise ReviewError(f"reviewer assignment already exists and differs: {phase}/{key}")
            reused += 1
        else:
            _atomic_json(target, template)
            _atomic_json(ai_target, sidecar)
            created += 1
        manifest.append({
            "paper_key": key,
            "wave": wave,
            "phase": phase,
            "review_fields": fields,
            "template_sha256": _sha256(target),
            "model_sidecar_sha256": _sha256(ai_target),
        })
    result = {"created": created, "reused": reused, "assignments": manifest}
    _atomic_json(reviewer / "state" / "review_assignment_manifest.json", result)
    return result


def lock_corpus_b_roster(reviewer_workspace, *, decisions, fn_census, version):
    reviewer = Path(reviewer_workspace).resolve(strict=True)
    if not version:
        raise ReviewError("roster version is required")
    if not isinstance(fn_census, dict) or fn_census.get("closed") is not True:
        raise ReviewError("FN census is not closed")
    recon_dir = reviewer / "state" / "reconciled"
    reconciliations = {path.stem: _load(path) for path in recon_dir.glob("rayyan-*.json")}
    if not reconciliations:
        raise ReviewError("no reconciled records")
    roster = set()
    used_decisions = {}
    for key, reconciliation in sorted(reconciliations.items()):
        fields = {field["field"]: field for field in reconciliation["fields"]}
        resolved = {}
        for name in ("methodological_eligibility", "level_3b"):
            field = fields[name]
            if field["agree"]:
                resolved[name] = field["a"]
            else:
                supplied = (decisions.get(key) or {}).get(name)
                if not isinstance(supplied, bool):
                    raise ReviewError(f"missing human decision: {key}.{name}")
                resolved[name] = supplied
                used_decisions.setdefault(key, {})[name] = supplied
        if resolved["methodological_eligibility"] is True and resolved["level_3b"] is True:
            roster.add(key)
    for key in fn_census.get("confirmed_corpus_b_keys") or []:
        if key not in reconciliations:
            raise ReviewError(f"FN census key is outside reconciled corpus: {key}")
        roster.add(key)

    keys = sorted(roster)
    decision_manifest = {
        "membership_decisions": used_decisions,
        "fn_census": fn_census,
        "reconciliation_sha256": {
            key: _sha256(recon_dir / f"{key}.json") for key in sorted(reconciliations)
        },
    }
    decision_hash = _hash_value(decision_manifest)
    _atomic_json(reviewer / "state" / f"roster_decisions.{version}.json", decision_manifest)
    receipt = {
        "roster_version": version,
        "decision_timestamp": _now(),
        "keys": keys,
        "roster_size": len(keys),
        "branch": corpus_b_branch(len(keys)),
        "source_decision_manifest_sha256": decision_hash,
    }
    receipt["receipt_sha256"] = _hash_value(receipt)
    _atomic_json(reviewer / "roster_exports" / f"corpus_b.{version}.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    imported = sub.add_parser("import")
    imported.add_argument("--production-root", type=Path, required=True)
    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("--reviewer-workspace", type=Path, default=Path.cwd())
    lock = sub.add_parser("lock-roster")
    lock.add_argument("--reviewer-workspace", type=Path, default=Path.cwd())
    lock.add_argument("--decisions", type=Path, required=True)
    lock.add_argument("--fn-census", type=Path, required=True)
    lock.add_argument("--version", required=True)
    materialize = sub.add_parser("materialize")
    materialize.add_argument("--reviewer-workspace", type=Path, default=Path.cwd())
    materialize.add_argument("--assignments", type=Path, required=True)
    materialize.add_argument("--canonical-root", type=Path)
    args = parser.parse_args(argv)
    if args.command == "import":
        result = import_validated_outputs(args.production_root)
    elif args.command == "reconcile":
        result = reconcile_imports(args.reviewer_workspace)
    elif args.command == "lock-roster":
        result = lock_corpus_b_roster(
            args.reviewer_workspace,
            decisions=_load(args.decisions),
            fn_census=_load(args.fn_census),
            version=args.version,
        )
    else:
        result = materialize_review_assignments(
            args.reviewer_workspace,
            _load(args.assignments),
            canonical_root=args.canonical_root,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
