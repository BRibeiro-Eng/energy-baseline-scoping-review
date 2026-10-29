"""Deterministic schema, semantic, and grounding validation for article outputs."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from field_contract import (
    STAGE2_FIELDS,
    STAGE3_FIELDS,
    build_article_output_schema,
    build_stage3_supplement_schema,
)
from grounding import ground_quote

SPECIAL_QUOTES = ("not found in source", "not applicable")


def _schema_path():
    here = Path(__file__).resolve()
    candidates = (
        here.parent.parent / "config" / "article_output.schema.json",
        here.parent.parent / "schemas" / "article_output.schema.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("article_output.schema.json not found")


def _supplement_schema_path():
    here = Path(__file__).resolve()
    candidates = (
        here.parent.parent / "config" / "stage3_supplement.schema.json",
        here.parent.parent / "schemas" / "stage3_supplement.schema.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("stage3_supplement.schema.json not found")


def _path(error):
    return ".".join(str(part) for part in error.absolute_path) or "$"


def _schema_errors(schema, record):
    """Return useful leaf errors instead of opaque top-level oneOf failures."""

    def leaves(error):
        if not error.context:
            return [error]
        descendants = [item for child in error.context for item in leaves(child)]
        deepest = max(len(item.absolute_path) for item in descendants)
        return [item for item in descendants if len(item.absolute_path) == deepest]

    found = []
    validator = Draft202012Validator(schema)
    for error in validator.iter_errors(record):
        found.extend(leaves(error))
    messages = {
        f"schema {_path(error)}: {error.message}"
        for error in found
    }
    return sorted(messages)


def _field_set_errors(stage_name, stage, expected):
    if not isinstance(stage, dict):
        return []
    actual = set(stage)
    expected = set(expected)
    errors = []
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{stage_name}: missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"{stage_name}: unexpected fields: {', '.join(extra)}")
    return errors


def _conditional_errors(record):
    errors = []
    stage1 = record.get("stage1") or {}
    eligible = (stage1.get("methodological_eligibility") or {}).get("value")
    level_3b = (stage1.get("level_3b") or {}).get("value")
    stage2, stage3 = record.get("stage2"), record.get("stage3")
    if eligible is False:
        if level_3b is not False:
            errors.append("level_3b must be false when methodological eligibility is false")
        if stage2 is not None:
            errors.append("stage2 must be null when ineligible")
        if stage3 is not None:
            errors.append("stage3 must be null when ineligible")
    elif eligible is True:
        if stage2 is None:
            errors.append("stage2 is required when eligible")
        else:
            errors += _field_set_errors("stage2", stage2, STAGE2_FIELDS)
        if level_3b is True:
            if stage3 is None:
                errors.append("stage3 is required when level_3b is true")
            else:
                errors += _field_set_errors("stage3", stage3, STAGE3_FIELDS)
        elif level_3b is False:
            if stage3 is not None:
                errors.append("stage3 must be null when level_3b is false")
        else:
            errors.append("level_3b must be true or false for an eligible paper")
    else:
        errors.append("methodological_eligibility must be true or false")
    return errors


def _iter_envelopes(record):
    stage1 = record.get("stage1")
    if isinstance(stage1, dict):
        for field in ("methodological_eligibility", "paper_type", "level_3b"):
            value = stage1.get(field)
            if isinstance(value, dict):
                yield f"stage1.{field}", value
    for stage_name in ("stage2", "stage3"):
        stage = record.get(stage_name)
        if isinstance(stage, dict):
            for field, value in stage.items():
                if isinstance(value, dict):
                    yield f"{stage_name}.{field}", value


def _ground_one(field, quote, page, non_contiguous, pages, *, allow_implicit_lists=False):
    errors, warnings, results = [], [], []
    checked = 0
    if quote is None or (isinstance(quote, str) and quote.lower().startswith(SPECIAL_QUOTES)):
        if page is not None:
            errors.append(f"{field}: special/null evidence must have page=null")
        return checked, results, errors, warnings

    quote_is_list = isinstance(quote, list)
    page_is_list = isinstance(page, list)
    implicit_lists = allow_implicit_lists and non_contiguous is None and (quote_is_list or page_is_list)
    if non_contiguous is True or implicit_lists:
        if not quote_is_list or not page_is_list:
            errors.append(f"{field}: non-contiguous evidence requires quote/page lists")
            return checked, results, errors, warnings
        if len(quote) != len(page):
            errors.append(
                f"{field}: evidence_quote/page length mismatch: {len(quote)} vs {len(page)}"
            )
            return checked, results, errors, warnings
    elif quote_is_list or page_is_list:
        errors.append(f"{field}: quote/page lists require non_contiguous_evidence=true")
        return checked, results, errors, warnings

    checked = 1
    result = ground_quote(quote, page, pages)
    results.append({"field": field, **result})
    if not result.get("grounded"):
        detail = result.get("error")
        suffix = f" ({detail})" if detail else ""
        errors.append(f"{field}: evidence is not grounded{suffix}")
    elif result.get("page_unverified"):
        warnings.append(f"{field}: quote grounded on a different page")
    return checked, results, errors, warnings


def _grounding(record, bundle):
    errors, warnings, results = [], [], []
    pages = (bundle.get("pdf") or {}).get("pages") or []
    checked = 0
    for field, envelope in _iter_envelopes(record):
        count, field_results, field_errors, field_warnings = _ground_one(
            field,
            envelope.get("evidence_quote"),
            envelope.get("page"),
            envelope.get("non_contiguous_evidence"),
            pages,
        )
        checked += count
        results += field_results
        errors += field_errors
        warnings += field_warnings

    stage3 = record.get("stage3")
    if isinstance(stage3, dict):
        metric_envelope = stage3.get("performance_metrics_reported")
        metrics = metric_envelope.get("value") if isinstance(metric_envelope, dict) else None
        if isinstance(metrics, list):
            for index, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    continue
                field = f"stage3.performance_metrics_reported.value[{index}]"
                count, metric_results, metric_errors, metric_warnings = _ground_one(
                    field,
                    metric.get("evidence_quote"),
                    metric.get("page"),
                    metric.get("non_contiguous_evidence"),
                    pages,
                    allow_implicit_lists=True,
                )
                checked += count
                results += metric_results
                errors += metric_errors
                warnings += metric_warnings
    return {"checked": checked, "results": results}, errors, warnings


def validate_initial_output(record, bundle, *, expected_key, expected_attempt, schema_path=None):
    errors, warnings = [], []
    schema = (
        json.loads(Path(schema_path).read_text(encoding="utf-8"))
        if schema_path is not None
        else build_article_output_schema()
    )
    errors += _schema_errors(schema, record)
    if record.get("paper_key") != expected_key:
        errors.append("paper_key does not match assignment")
    if bundle.get("key") != expected_key:
        errors.append("Stage-0 bundle key does not match assignment")
    if record.get("attempt") != expected_attempt:
        errors.append("attempt does not match assignment")
    errors += _conditional_errors(record)
    grounding, grounding_errors, grounding_warnings = _grounding(record, bundle)
    errors += grounding_errors
    warnings += grounding_warnings
    return {
        "valid": not errors,
        "paper_key": expected_key,
        "attempt": expected_attempt,
        "errors": errors,
        "warnings": warnings,
        "grounding": grounding,
    }


def validate_stage3_supplement(
    record, bundle, plan, *, expected_key, expected_attempt, schema_path=None
):
    errors, warnings = [], []
    schema = (
        json.loads(Path(schema_path).read_text(encoding="utf-8"))
        if schema_path is not None
        else build_stage3_supplement_schema()
    )
    errors += _schema_errors(schema, record)
    if plan.get("blocked") is True:
        errors.append("supplement plan is blocked")
    if expected_key not in (plan.get("authorized_keys") or []):
        errors.append("paper key is not authorized by supplement plan")
    if record.get("paper_key") != expected_key:
        errors.append("paper_key does not match assignment")
    if bundle.get("key") != expected_key:
        errors.append("Stage-0 bundle key does not match assignment")
    if record.get("attempt") != expected_attempt:
        errors.append("attempt does not match assignment")
    if record.get("roster_version") != plan.get("roster_version"):
        errors.append("roster version does not match supplement plan")
    if record.get("roster_receipt_sha256") != plan.get("roster_receipt_sha256"):
        errors.append("roster receipt hash does not match supplement plan")
    item = next(
        (row for row in (plan.get("items") or []) if row.get("paper_key") == expected_key),
        None,
    )
    if item is None:
        errors.append("supplement plan has no provenance item for paper")
    elif record.get("initial_output_sha256") != item.get("initial_output_sha256"):
        errors.append("initial output hash does not match supplement plan")
    errors += _field_set_errors("stage3", record.get("stage3"), STAGE3_FIELDS)
    grounding, grounding_errors, grounding_warnings = _grounding(
        {"stage3": record.get("stage3")}, bundle
    )
    errors += grounding_errors
    warnings += grounding_warnings
    return {
        "valid": not errors,
        "paper_key": expected_key,
        "attempt": expected_attempt,
        "errors": errors,
        "warnings": warnings,
        "grounding": grounding,
    }
