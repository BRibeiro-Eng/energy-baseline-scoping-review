"""Deterministic C-2.3 Stage-4 consolidation and lineage reporting.

Consumes immutable reviewer imports, a locked Corpus-B roster, and finalised
targeted human decisions. It never edits model outputs or human review files.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
from pathlib import Path

from audit_sampler import select_audit
from cross_checks import cross_checks
from grounding import ground_quote
from local_storage import is_prohibited
from reconcile import reconcile_record
from review_evidence import (
    ABSENCE_EVIDENCE_MODE,
    evidence_mode,
    is_absence_like,
)


INITIAL_FILE = re.compile(r"^rayyan-\d+\.json$")
REVIEW_SECTIONS = ("eligibility", "level_a", "level_b")
_MISSING = object()


class Stage4Error(RuntimeError):
    pass


def _now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Stage4Error(f"invalid Stage-4 input {path}: {exc}") from exc


def _atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _atomic_json(path, value):
    _atomic_bytes(path, _canonical(value))


def _value(envelope):
    return envelope.get("value") if isinstance(envelope, dict) else envelope


def _supplement(reviewer, family, key):
    path = reviewer / "imports" / family / "supplements" / f"{key}.stage3-supplement.json"
    return _load(path) if path.is_file() else None


def _model_values(record, supplement=None):
    stage1 = record.get("stage1") or {}
    stage3 = record.get("stage3")
    if stage3 is None and supplement is not None:
        stage3 = supplement.get("stage3")
    return {
        "key": record.get("paper_key"),
        "eligibility": {
            "methodological_eligibility": _value(stage1.get("methodological_eligibility")),
            "ineligibility_reason": stage1.get("ineligibility_reason"),
            "borderline_review_synthesis_eligibility": stage1.get(
                "borderline_review_synthesis_eligibility"
            ),
            "paper_type": _value(stage1.get("paper_type")),
            "level_3b": _value(stage1.get("level_3b")),
        },
        "level_a": {
            name: _value(envelope) for name, envelope in (record.get("stage2") or {}).items()
        },
        "level_b": {name: _value(envelope) for name, envelope in (stage3 or {}).items()},
    }


def _model_envelope(record, supplement, section, field):
    if section == "eligibility":
        return (record.get("stage1") or {}).get(field)
    stage = record.get("stage2") if section == "level_a" else record.get("stage3")
    if section == "level_b" and stage is None and supplement is not None:
        stage = supplement.get("stage3")
    return (stage or {}).get(field)


def _select_field(field_row, human_values):
    """Apply the ordinary human-then-concordance selection precedence."""
    fq = f"{field_row['section']}.{field_row['field']}"
    human_value = human_values.get(fq, _MISSING)
    if human_value is not _MISSING:
        return human_value, "human", True
    if field_row["agree"]:
        return field_row["a"], "model_concordance", True
    return None, "unresolved", False


def _latest_roster(reviewer):
    paths = list((reviewer / "roster_exports").glob("corpus_b.*.json"))
    if not paths:
        raise Stage4Error("no locked Corpus-B roster receipt")
    path = max(paths, key=lambda p: p.stat().st_mtime_ns)
    receipt = _load(path)
    supplied = dict(receipt)
    recorded = supplied.pop("receipt_sha256", None)
    actual = hashlib.sha256(_canonical(supplied)).hexdigest()
    if not recorded or actual != recorded:
        raise Stage4Error("Corpus-B roster receipt hash mismatch")
    return path, receipt


def _human_reviews(reviewer, canonical_root):
    reviews, input_paths = {}, []
    for path in sorted((reviewer / "reviews").rglob("rayyan-*.json")):
        if not INITIAL_FILE.fullmatch(path.name):
            continue
        record = _load(path)
        key = record.get("key")
        state_path = path.with_name(path.stem + ".state.json")
        state = _load(state_path) if state_path.is_file() else {}
        if state.get("state") != "finalised" or record.get("_done") is not True:
            continue
        bundle_path = canonical_root / "output" / "stage0" / f"{key}.json"
        bundle = _load(bundle_path)
        pages = (bundle.get("pdf") or {}).get("pages") or []
        values, evidence_results = {}, {}
        for fq in record.get("_review_fields") or []:
            try:
                section, field = fq.split(".", 1)
            except ValueError as exc:
                raise Stage4Error(f"invalid human review field: {fq}") from exc
            if section not in REVIEW_SECTIONS:
                raise Stage4Error(f"invalid human review section: {fq}")
            if field not in (record.get(section) or {}):
                raise Stage4Error(f"human review omits targeted field: {key}.{fq}")
            evidence = (record.get("reviewer_evidence") or {}).get(fq) or {}
            value = (record.get(section) or {}).get(field)
            if evidence_mode(evidence) == ABSENCE_EVIDENCE_MODE:
                if not is_absence_like(value) or not str(evidence.get("rule") or "").strip():
                    raise Stage4Error(f"invalid human absence evidence: {key}.{fq}")
                if evidence.get("quote") or evidence.get("page") is not None:
                    raise Stage4Error(f"invalid human absence evidence: {key}.{fq}")
                result = {
                    "grounded": False,
                    "method": "human_full_text_absence_review",
                    "page_unverified": False,
                }
            else:
                result = ground_quote(evidence.get("quote"), evidence.get("page"), pages)
                if not result.get("grounded"):
                    raise Stage4Error(f"human evidence is not grounded: {key}.{fq}")
            values[fq] = value
            evidence_results[fq] = {**evidence, "grounding": result}
        combined = reviews.setdefault(key, {
            "values": {}, "evidence": {}, "notes": [],
            "blind_commits": [], "states": [], "paths": [],
        })
        overlap = set(combined["values"]) & set(values)
        if overlap:
            raise Stage4Error(
                f"human review field appears in multiple finalised episodes: {key}.{sorted(overlap)[0]}"
            )
        combined["values"].update(values)
        combined["evidence"].update(evidence_results)
        combined["notes"].append(record.get("reviewer_notes", ""))
        blind_path = path.with_name(path.stem + ".blind.json")
        if blind_path.is_file():
            combined["blind_commits"].append(_load(blind_path))
            input_paths.append(blind_path)
        combined["states"].append(state)
        combined["paths"].append(str(path))
        input_paths.extend([path, state_path, bundle_path])
    return reviews, input_paths


def _flatten(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(json.dumps(item, ensure_ascii=False, sort_keys=True)
                         if isinstance(item, (dict, list)) else str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _csv_bytes(records):
    fields = {"key", "title", "year"}
    for record in records:
        for section in REVIEW_SECTIONS:
            for field in (record.get(section) or {}):
                fields.add(f"{section}.{field}")
    ordered = ["key", "title", "year"] + sorted(fields - {"key", "title", "year"})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=ordered)
    writer.writeheader()
    for record in records:
        row = {
            "key": record["key"],
            "title": (record.get("metadata") or {}).get("title"),
            "year": (record.get("metadata") or {}).get("year"),
        }
        for section in REVIEW_SECTIONS:
            for field, value in (record.get(section) or {}).items():
                row[f"{section}.{field}"] = _flatten(value)
        writer.writerow(row)
    return stream.getvalue().encode("utf-8")


def consolidate(reviewer_workspace, *, canonical_root=None):
    reviewer = Path(reviewer_workspace).expanduser().resolve(strict=True)
    lock = _load(reviewer / "REVIEWER_LOCK.json")
    root = Path(canonical_root or lock.get("canonical_root", "")).expanduser().resolve(strict=True)
    if is_prohibited(reviewer) or is_prohibited(root):
        raise Stage4Error("prohibited reviewer or canonical root")
    if Path(lock.get("canonical_root", "")).resolve(strict=False) != root:
        raise Stage4Error("canonical root does not match REVIEWER_LOCK")

    roster_path, receipt = _latest_roster(reviewer)
    roster = set(receipt.get("keys") or [])
    models, source_paths = {}, [reviewer / "REVIEWER_LOCK.json", roster_path]
    for family in ("chatgpt", "claude"):
        paths = {
            path.stem: path for path in (reviewer / "imports" / family).glob("rayyan-*.json")
            if INITIAL_FILE.fullmatch(path.name)
        }
        models[family] = paths
        source_paths.extend(paths.values())
    if set(models["chatgpt"]) != set(models["claude"]):
        raise Stage4Error("model import key sets differ")

    human, human_paths = _human_reviews(reviewer, root)
    source_paths.extend(human_paths)
    merged, reconciled, unresolved, flags = [], {}, [], []
    for key in sorted(models["chatgpt"]):
        raw = {family: _load(models[family][key]) for family in models}
        supplements = {family: _supplement(reviewer, family, key) for family in models}
        for family, supplement in supplements.items():
            if supplement is not None:
                source_paths.append(
                    reviewer / "imports" / family / "supplements"
                    / f"{key}.stage3-supplement.json"
                )
        values = {
            family: _model_values(raw[family], supplements[family]) for family in models
        }
        if key not in roster:
            # Preserve false-positive Stage-3 material in model provenance/imports,
            # but never let it enter Level-B reconciliation or analytical data.
            for family in values:
                values[family]["level_b"] = {}
        reconciliation = reconcile_record(values["chatgpt"], values["claude"])
        reconciled[key] = reconciliation
        final = {"eligibility": {}, "level_a": {}, "level_b": {}}
        provenance = {}
        human_values = (human.get(key) or {}).get("values", {})
        methodological_row = next(
            row for row in reconciliation["fields"]
            if row["section"] == "eligibility"
            and row["field"] == "methodological_eligibility"
        )
        methodological_value, _, methodological_resolved = _select_field(
            methodological_row, human_values
        )
        for field_row in reconciliation["fields"]:
            section, field = field_row["section"], field_row["field"]
            fq = f"{section}.{field}"
            selected, source, resolved = _select_field(field_row, human_values)
            if methodological_resolved and methodological_value is False and section == "level_a":
                selected, source, resolved = None, "structural_not_applicable", True
            elif (
                methodological_resolved
                and methodological_value is False
                and section == "eligibility"
                and field == "ineligibility_reason"
                and not resolved
            ):
                selected = next(
                    (value for value in (field_row["a"], field_row["b"])
                     if isinstance(value, str) and value.strip()),
                    None,
                )
                source, resolved = "model_narrative_precedence", True
            if not resolved:
                unresolved.append({"paper_key": key, **field_row})
            final[section][field] = selected
            provenance[fq] = {
                "selected_source": source,
                "chatgpt": _model_envelope(raw["chatgpt"], supplements["chatgpt"], section, field),
                "claude": _model_envelope(raw["claude"], supplements["claude"], section, field),
                "human_evidence": (human.get(key) or {}).get("evidence", {}).get(fq),
            }
        if key not in roster:
            final["level_b"] = None
            provenance = {name: item for name, item in provenance.items()
                          if not name.startswith("level_b.")}
        bundle = _load(root / "output" / "stage0" / f"{key}.json")
        record = {
            "key": key,
            "metadata": bundle.get("metadata") or {},
            **final,
            "corpus_b_roster_version": receipt.get("roster_version") if key in roster else None,
            "flags": [],
            "provenance": provenance,
        }
        record["flags"] = cross_checks(record)
        flags.extend({"paper_key": key, **flag} for flag in record["flags"])
        merged.append(record)

    audit_frame = [
        {
            "key": record["key"],
            "level_3b": (record.get("eligibility") or {}).get("level_3b"),
            "borderline_review_synthesis_eligibility": (record.get("eligibility") or {}).get(
                "borderline_review_synthesis_eligibility"
            ),
        }
        for record in merged
        if (record.get("eligibility") or {}).get("methodological_eligibility") is True
    ]
    audit = select_audit(audit_frame)
    report_dir = reviewer / "reports" / "final"
    input_hashes = {
        str(path.relative_to(root) if root in path.parents else path.relative_to(reviewer)): _sha256(path)
        for path in sorted(set(source_paths)) if path.is_file()
    }
    lineage = {
        "generated_at": _now(),
        "source": lock.get("source"),
        "canonical_input_inventory_sha256": lock.get("canonical_input_inventory_sha256"),
        "roster_version": receipt.get("roster_version"),
        "roster_receipt_sha256": receipt.get("receipt_sha256"),
        "input_sha256": input_hashes,
    }
    summary = {
        "records": len(merged),
        "corpus_b": len(roster),
        "human_finalised_records": len(human),
        "unresolved_fields": len(unresolved),
        "cross_check_flags": len(flags),
        "audit": audit,
        "validation_components_pending": ["FN census report", "human SRS audit results", "test-retest", "canary"],
    }
    _atomic_json(report_dir / "merged.json", merged)
    _atomic_bytes(report_dir / "merged.csv", _csv_bytes(merged))
    _atomic_json(report_dir / "unresolved.json", unresolved)
    _atomic_json(report_dir / "cross_check_report.json", flags)
    _atomic_json(report_dir / "audit_srs_sample.json", audit)
    _atomic_json(report_dir / "stage4_lineage.json", lineage)
    needs = ["# Needs review", ""] + [
        f"- {row['paper_key']} — {row['section']}.{row['field']}: unresolved model divergence"
        for row in unresolved
    ] + [f"- {row['paper_key']} — {row['check']}: {row['detail']}" for row in flags]
    _atomic_bytes(report_dir / "needs_review.md", ("\n".join(needs) + "\n").encode())
    validation = (
        "# C-2.3 Stage-4 validation report\n\n"
        f"- Records consolidated: {summary['records']}\n"
        f"- Locked Corpus B: {summary['corpus_b']}\n"
        f"- Finalised human review records: {summary['human_finalised_records']}\n"
        f"- Unresolved fields: {summary['unresolved_fields']}\n"
        f"- Cross-check flags: {summary['cross_check_flags']}\n"
        f"- Level-A SRS frame/draw: {audit['frame_size']}/{audit['n_drawn']} (seed 44)\n\n"
        "This is an interim deterministic consolidation. FN-census closure, audited "
        "per-field error intervals, test-retest, and canary results remain separate "
        "hard gates before a thesis-ready final validation report.\n"
    )
    _atomic_bytes(report_dir / "validation_report.md", validation.encode())
    if unresolved:
        raise Stage4Error(f"Stage 4 has {len(unresolved)} unresolved field divergence(s)")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-workspace", type=Path, default=Path.cwd())
    parser.add_argument("--canonical-root", type=Path)
    args = parser.parse_args(argv)
    result = consolidate(args.reviewer_workspace, canonical_root=args.canonical_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
