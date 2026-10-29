"""Canonical extraction field contract and generated JSON Schema snapshots.

This module is the single machine-readable source of truth for model outputs,
the reviewer form projection, validation, and reconciliation.  Keep protocol
labels and help text in the UI layer; types and controlled vocabularies live
here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


PAPER_TYPE = [
    "single applied case",
    "multi-case study",
    "review/synthesis",
    "maturity model or framework",
    "methodological/theoretical",
    "tool/software design",
    "other",
]

ORGANISATION_TYPE = [
    "continuous process",
    "discrete manufacturing",
    "services",
    "buildings",
    "mixed",
    "not specified",
]

EMS_STANDARD = ["ISO 50001", "ISO 50002", "ISO 50006", "other-named", "none"]
MV_PROTOCOL = [
    "IPMVP",
    "ASHRAE 14",
    "SEP M&V",
    "BPA MT&R",
    "ISO 17743",
    "other-named",
    "none",
]
REGULATORY_DRIVER = [
    "EU EED",
    "national audit decree",
    "EU-ETS",
    "regional regulation",
    "other-named",
    "none",
]
ENPI_ENB_MODEL_TYPES = [
    "linear regression",
    "multiple regression",
    "physical model",
    "ML",
    "simple intensity ratio",
    "SEC mean",
    "composite index",
    "change-point or SPC",
    "process integration",
    "other",
    "not applicable",
]
COMPLEMENTARY_METHODOLOGIES = [
    "pinch analysis",
    "exergy analysis",
    "thermodynamic modelling",
    "process flowsheet simulation",
    "ML ensemble",
    "multi-criteria decision-making (MCDM/AHP/TOPSIS/Fuzzy)",
    "none",
]
VALIDATION_TYPES = ["empirical", "simulation", "theoretical", "statistical", "none reported"]
SCALE_OF_APPLICATION = [
    "equipment",
    "sub-system / utility system",
    "unit",
    "facility",
    "organisation",
]
SPECIFIC_LIMITATIONS = [
    "non-stationarity",
    "fouling",
    "catalyst deactivation",
    "feedstock variability",
    "other",
]
ADAPTATION_TYPES = [
    "dynamic time window",
    "segmented baseline",
    "hybrid physical model",
    "other",
]
NORMATIVE_FRAMING = ["ISO 50001/50006 explicit", "implicit", "absent"]
DATA_TYPE = ["continuous time series", "audit data", "simulation", "unspecified or not stated"]
PERFORMANCE_METRICS = [
    "R²",
    "adjusted R²",
    "RMSE",
    "MAE",
    "MAPE",
    "CV-RMSE",
    "% energy savings",
    "F-statistic",
    "p-value",
    "other-named",
]

QUOTE_SCHEMA = {
    "oneOf": [
        {"type": "string"},
        {"type": "array", "minItems": 1, "items": {"type": "string"}},
        {"type": "null"},
    ]
}
PAGE_SCHEMA = {
    "oneOf": [
        {"type": "integer", "minimum": 1},
        {"type": "array", "minItems": 1, "items": {"type": "integer", "minimum": 1}},
        {"type": "null"},
    ]
}


def _scalar(type_: str, *, nullable: bool = False, max_length: int | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": [type_, "null"] if nullable else type_}
    if max_length is not None:
        schema["maxLength"] = max_length
    return schema


def _enum(options: list[Any]) -> dict[str, Any]:
    return {"enum": copy.deepcopy(options)}


def _multi_enum(options: list[Any]) -> dict[str, Any]:
    return {
        "type": "array",
        "uniqueItems": True,
        "items": {"enum": copy.deepcopy(options)},
    }


def _list_str() -> dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}}


_PERFORMANCE_ITEM_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "metric",
        "value",
        "unit",
        "period_or_context",
        "evidence_quote",
        "page",
    ],
    "properties": {
        "metric": _enum(PERFORMANCE_METRICS),
        "value": _scalar("string", nullable=True),
        "unit": _scalar("string", nullable=True),
        "period_or_context": _scalar("string", nullable=True),
        "evidence_quote": copy.deepcopy(QUOTE_SCHEMA),
        "page": copy.deepcopy(PAGE_SCHEMA),
        "non_contiguous_evidence": {"type": "boolean"},
    },
}


# Ordered mappings: their insertion order is the frozen field order.
STAGE1_FIELDS: dict[str, dict[str, Any]] = {
    "methodological_eligibility": {"value_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "ineligibility_reason": {"plain_schema": _scalar("string", nullable=True), "reviewer": {"type": "text"}},
    "borderline_review_synthesis_eligibility": {"plain_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "paper_type": {"value_schema": _enum(PAPER_TYPE), "reviewer": {"type": "enum", "options": PAPER_TYPE}},
    "level_3b": {"value_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "notes": {"plain_schema": _scalar("string", nullable=True, max_length=500), "reviewer": {"type": "textarea"}},
}

STAGE2_FIELDS: dict[str, dict[str, Any]] = {
    "multi_site": {"value_schema": {"oneOf": [{"type": "boolean"}, {"const": "not applicable"}]}, "reviewer": {"type": "enum", "options": [True, False, "not applicable"]}},
    "country_region": {"value_schema": _scalar("string", nullable=True), "reviewer": {"type": "text"}},
    "sector_of_activity": {"value_schema": _scalar("string", nullable=True), "reviewer": {"type": "text"}},
    "type_of_organisation": {"value_schema": _enum(ORGANISATION_TYPE), "reviewer": {"type": "enum", "options": ORGANISATION_TYPE}},
    "ems_standard": {"value_schema": _multi_enum(EMS_STANDARD), "reviewer": {"type": "multienum", "options": EMS_STANDARD}},
    "mv_protocol": {"value_schema": _multi_enum(MV_PROTOCOL), "reviewer": {"type": "multienum", "options": MV_PROTOCOL}},
    "regulatory_driver": {"value_schema": _multi_enum(REGULATORY_DRIVER), "reviewer": {"type": "multienum", "options": REGULATORY_DRIVER}},
    "enpi_enb_model_types": {"value_schema": _multi_enum(ENPI_ENB_MODEL_TYPES), "reviewer": {"type": "multienum", "options": ENPI_ENB_MODEL_TYPES}},
    "complementary_methodologies": {"value_schema": _multi_enum(COMPLEMENTARY_METHODOLOGIES), "reviewer": {"type": "multienum", "options": COMPLEMENTARY_METHODOLOGIES}},
}

STAGE3_FIELDS: dict[str, dict[str, Any]] = {
    "normalisation_variables": {"value_schema": _list_str(), "reviewer": {"type": "list_str"}},
    "baseline_period_start": {"value_schema": _scalar("string", nullable=True), "reviewer": {"type": "text"}},
    "baseline_period_end": {"value_schema": _scalar("string", nullable=True), "reviewer": {"type": "text"}},
    "baseline_construction_method": {"value_schema": _scalar("string", nullable=True), "reviewer": {"type": "textarea"}},
    "validation_types": {"value_schema": _multi_enum(VALIDATION_TYPES), "reviewer": {"type": "multienum", "options": VALIDATION_TYPES}},
    "scale_of_application": {"value_schema": _enum(SCALE_OF_APPLICATION), "reviewer": {"type": "enum", "options": SCALE_OF_APPLICATION}},
    "scope_description": {"value_schema": _scalar("string", nullable=True), "reviewer": {"type": "textarea"}},
    "identifies_model_limitations": {"value_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "specific_limitations": {"value_schema": _multi_enum(SPECIFIC_LIMITATIONS), "reviewer": {"type": "multienum", "options": SPECIFIC_LIMITATIONS}},
    "proposes_treatment_mechanism": {"value_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "proposes_adaptations": {"value_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "adaptation_types": {"value_schema": _multi_enum(ADAPTATION_TYPES), "reviewer": {"type": "multienum", "options": ADAPTATION_TYPES}},
    "normative_framing_of_adaptations": {"value_schema": _enum(NORMATIVE_FRAMING), "reviewer": {"type": "enum", "options": NORMATIVE_FRAMING}},
    "empirical_refinery_application": {"value_schema": _scalar("boolean"), "reviewer": {"type": "bool"}},
    "data_type": {"value_schema": _enum(DATA_TYPE), "reviewer": {"type": "enum", "options": DATA_TYPE}},
    "model_parameters_reported": {"value_schema": _list_str(), "reviewer": {"type": "list_str"}},
    "performance_metrics_reported": {
        "value_schema": {"type": "array", "items": _PERFORMANCE_ITEM_SCHEMA},
        "reviewer": {
            "type": "list_obj",
            "item_fields": [
                {"name": "metric", "type": "enum", "options": PERFORMANCE_METRICS},
                {"name": "value", "type": "text"},
                {"name": "unit", "type": "text"},
                {"name": "period_or_context", "type": "text"},
            ],
        },
    },
    "implementation_barriers": {"value_schema": _list_str(), "reviewer": {"type": "list_str"}},
}


def _base_defs() -> dict[str, Any]:
    return {
        "quote": copy.deepcopy(QUOTE_SCHEMA),
        "page": copy.deepcopy(PAGE_SCHEMA),
        "envelope": {
            "type": "object",
            "additionalProperties": False,
            "required": ["value", "evidence_quote", "page", "non_contiguous_evidence", "confidence"],
            "properties": {
                "value": {},
                "evidence_quote": copy.deepcopy(QUOTE_SCHEMA),
                "page": copy.deepcopy(PAGE_SCHEMA),
                "non_contiguous_evidence": {"type": "boolean"},
                "confidence": {
                    "oneOf": [
                        {"type": "number", "minimum": 0, "maximum": 1},
                        {"type": "null"},
                    ]
                },
            },
        },
    }


def _envelope_schema(value_schema: dict[str, Any]) -> dict[str, Any]:
    envelope = copy.deepcopy(_base_defs()["envelope"])
    envelope["properties"]["value"] = copy.deepcopy(value_schema)
    return envelope


def _object_schema(fields: dict[str, dict[str, Any]]) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    for name, definition in fields.items():
        if "plain_schema" in definition:
            properties[name] = copy.deepcopy(definition["plain_schema"])
        else:
            properties[name] = _envelope_schema(definition["value_schema"])
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(fields),
        "properties": properties,
    }


def _all_defs() -> dict[str, Any]:
    definitions = _base_defs()
    definitions.update(
        {
            "stage1Object": _object_schema(STAGE1_FIELDS),
            "stage2Object": _object_schema(STAGE2_FIELDS),
            "stage3Object": _object_schema(STAGE3_FIELDS),
        }
    )
    return definitions


def build_article_output_schema() -> dict[str, Any]:
    """Return the complete strict schema for an initial extraction record."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "article_output.schema.json",
        "title": "Combined article extraction output",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "record_type",
            "paper_key",
            "schema_version",
            "validation_protocol",
            "prompt_tag",
            "attempt",
            "completed_at",
            "stage1",
            "stage2",
            "stage3",
        ],
        "properties": {
            "record_type": {"const": "initial_extraction"},
            "paper_key": {"type": "string", "pattern": "^rayyan-[0-9]+$"},
            "schema_version": {"const": "2.2.1"},
            "validation_protocol": {"const": "C-2.3"},
            "prompt_tag": {"const": "v2.3.1-operational"},
            "attempt": {"type": "integer", "minimum": 1, "maximum": 2},
            "completed_at": {"type": "string", "minLength": 1},
            "stage1": {"$ref": "#/$defs/stage1Object"},
            "stage2": {"oneOf": [{"type": "null"}, {"$ref": "#/$defs/stage2Object"}]},
            "stage3": {"oneOf": [{"type": "null"}, {"$ref": "#/$defs/stage3Object"}]},
        },
        "$defs": _all_defs(),
    }


def build_stage3_supplement_schema() -> dict[str, Any]:
    """Return the supplement schema using the identical Stage 3 contract."""
    stage3_schema = copy.deepcopy(build_article_output_schema()["properties"]["stage3"])
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "stage3_supplement.schema.json",
        "title": "Stage-3-only supplement output",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "record_type",
            "paper_key",
            "schema_version",
            "validation_protocol",
            "prompt_tag",
            "roster_version",
            "roster_receipt_sha256",
            "initial_output_sha256",
            "attempt",
            "completed_at",
            "stage3",
        ],
        "properties": {
            "record_type": {"const": "stage3_supplement"},
            "paper_key": {"type": "string", "pattern": "^rayyan-[0-9]+$"},
            "schema_version": {"const": "2.2.1"},
            "validation_protocol": {"const": "C-2.3"},
            "prompt_tag": {"const": "v2.3.1-operational"},
            "roster_version": {"type": "string", "minLength": 1},
            "roster_receipt_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "initial_output_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "attempt": {"type": "integer", "minimum": 1, "maximum": 2},
            "completed_at": {"type": "string", "minLength": 1},
            "stage3": stage3_schema,
        },
        "$defs": _all_defs(),
    }


_REVIEWER_SECTION_TO_STAGE = {
    "eligibility": STAGE1_FIELDS,
    "level_a": STAGE2_FIELDS,
    "level_b": STAGE3_FIELDS,
}


def reviewer_field_contract(section: str, field: str) -> dict[str, Any]:
    """Project one canonical field into the human reviewer's value-only form."""
    try:
        definition = _REVIEWER_SECTION_TO_STAGE[section][field]
    except KeyError as exc:
        raise KeyError(f"unknown reviewer field: {section}.{field}") from exc
    return copy.deepcopy(definition["reviewer"])


def _canonical_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def contract_sha256() -> str:
    """Hash both generated schemas in a deterministic order."""
    digest = hashlib.sha256()
    digest.update(_canonical_json(build_article_output_schema()))
    digest.update(_canonical_json(build_stage3_supplement_schema()))
    return digest.hexdigest()


def write_schema_snapshots(root: str | Path) -> list[Path]:
    root_path = Path(root)
    snapshots = {
        root_path / "config" / "article_output.schema.json": build_article_output_schema(),
        root_path / "config" / "stage3_supplement.schema.json": build_stage3_supplement_schema(),
    }
    for path, schema in snapshots.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_canonical_json(schema))
    return list(snapshots)


def check_schema_snapshots(root: str | Path) -> list[Path]:
    root_path = Path(root)
    snapshots = {
        root_path / "config" / "article_output.schema.json": build_article_output_schema(),
        root_path / "config" / "stage3_supplement.schema.json": build_stage3_supplement_schema(),
    }
    drifted = [
        path
        for path, schema in snapshots.items()
        if not path.is_file() or path.read_bytes() != _canonical_json(schema)
    ]
    return drifted


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write-snapshots", action="store_true")
    action.add_argument("--check-snapshots", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.write_snapshots:
        for path in write_schema_snapshots(args.root):
            print(path)
        return 0

    drifted = check_schema_snapshots(args.root)
    if drifted:
        for path in drifted:
            print(f"DRIFT: {path}")
        return 1
    print(f"schema snapshots match contract {contract_sha256()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
