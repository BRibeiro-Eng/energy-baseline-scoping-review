"""reconcile.py — Validation Protocol C field-level reconciliation.

Compares two value-only extraction records (model A vs model B) for the same
paper, field by field, AFTER normalisation, and partitions each field into
concordant / divergent.

Inter-model agreement is a ROUTING signal only (VALIDATION_PROTOCOL_C.md):
divergences route to blind-first human adjudication, concordances to the
stratified audit. It is never a reliability metric. Normalisation collapses
format-only differences (Codex `"true"` vs Claude `True`; enum labels like
`"multiple regression (>=2 IVs)"` vs `"multiple regression"`) so that only
genuine disagreements are flagged.
"""
import re

# Validation Protocol C section 2 — the consequential (Tier-1) gates.
TIER_1_FIELDS = {
    "methodological_eligibility",
    "level_3b",
    "paper_type",
    "borderline_review_synthesis_eligibility",
}

SECTIONS = ("eligibility", "level_a", "level_b")

_PAREN = re.compile(r"\s*\([^)]*\)")


def _canon_scalar(v, strip_parens=False):
    """Canonicalise a scalar into a type-tagged atom: string-bools -> bool;
    lowercase/collapse-whitespace strings; bools/numbers kept distinct (True
    must NOT silently equal 1). Parentheticals are stripped only when
    strip_parens=True (see fields_agree), and never down to an empty string."""
    if isinstance(v, bool):
        return ("bool", v)
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return ("num", float(v))
    s = str(v).strip()
    if s.lower() in ("true", "false"):
        return ("bool", s.lower() == "true")
    if strip_parens:
        stripped = _PAREN.sub("", s)
        if stripped.strip():  # "(unclear)" must not collapse to ""
            s = stripped
    return ("str", re.sub(r"\s+", " ", s).strip().lower())


def _without_b13b_evidence(value):
    if not isinstance(value, list):
        return value
    ignored = {"evidence_quote", "page", "non_contiguous_evidence"}
    return [
        {key: item for key, item in metric.items() if key not in ignored}
        if isinstance(metric, dict) else metric
        for metric in value
    ]


def _country_tokens(value, strip_parens=False):
    tokens = []
    for part in re.split(r"[,;]", value):
        part = re.sub(r"^the\s+", "", part.strip(), flags=re.IGNORECASE)
        if part:
            tokens.append(_canon_scalar(part, strip_parens))
    return ("countries", frozenset(tokens))


def normalize(value, strip_parens=False, *, field=None):
    """Return a recursively typed, hashable canonical form.

    Mapping key order and list order are immaterial. Country/region receives a
    narrow token normalizer; no other free-text field inherits that rule.
    """
    if field == "performance_metrics_reported":
        value = _without_b13b_evidence(value)
    if field == "country_region" and isinstance(value, str):
        return _country_tokens(value, strip_parens)
    if isinstance(value, dict):
        return (
            "map",
            tuple(
                sorted(
                    (str(key), normalize(item, strip_parens))
                    for key, item in value.items()
                )
            ),
        )
    if isinstance(value, list):
        return ("list", frozenset(normalize(item, strip_parens) for item in value))
    return _canon_scalar(value, strip_parens)


def fields_agree(a, b, *, field=None):
    """True iff two field values agree after normalisation.

    Parenthetical stripping is a FALLBACK comparison, not part of the
    canonical form: values agree when one side's paren-stripped form equals
    the other side's raw form ("multiple regression (>=2 IVs)" elaborates
    "multiple regression"). Stripped-vs-stripped is never compared — that
    collapsed "other (refinery)" and "other (hospital)" into a false
    concordance that would silently skip blind-first human adjudication."""
    if normalize(a, field=field) == normalize(b, field=field):
        return True
    return (
        normalize(a, strip_parens=True, field=field) == normalize(b, field=field)
        or normalize(a, field=field) == normalize(b, strip_parens=True, field=field)
    )


def tier_of(section, field):
    """Tier per Validation Protocol C section 2: the 4 consequential gates are
    Tier 1; all Level-B fields Tier 2; everything else (Level-A descriptive,
    free-text eligibility context) Tier 3."""
    if field in TIER_1_FIELDS:
        return 1
    if section == "level_b":
        return 2
    return 3


def reconcile_record(rec_a, rec_b):
    """Compare two value-only records; return a per-field table + summary.

    Each field entry: {section, field, a, b, agree, tier}.
    Summary: tier1_divergences, total_divergences, n_fields.
    """
    fields = []
    for section in SECTIONS:
        a_sec = rec_a.get(section, {}) or {}
        b_sec = rec_b.get(section, {}) or {}
        for field in sorted(set(a_sec) | set(b_sec)):
            a, b = a_sec.get(field), b_sec.get(field)
            fields.append({
                "section": section,
                "field": field,
                "a": a,
                "b": b,
                "agree": fields_agree(a, b, field=field),
                "tier": tier_of(section, field),
            })
    tier1_div = sum(1 for f in fields if f["tier"] == 1 and not f["agree"])
    total_div = sum(1 for f in fields if not f["agree"])
    return {
        "key": rec_a.get("key") or rec_b.get("key"),
        "fields": fields,
        "summary": {
            "tier1_divergences": tier1_div,
            "total_divergences": total_div,
            "n_fields": len(fields),
        },
    }
