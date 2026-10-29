"""Shared validation rules for targeted human-review evidence."""

QUOTED_EVIDENCE_MODE = "quoted"
ABSENCE_EVIDENCE_MODE = "not_reported_after_full_text_review"
EVIDENCE_MODES = {QUOTED_EVIDENCE_MODE, ABSENCE_EVIDENCE_MODE}

ABSENCE_LABELS = {
    "absent",
    "none",
    "none reported",
    "not applicable",
    "not reported",
    "unspecified or not stated",
}


def evidence_mode(item):
    """Legacy evidence without an explicit mode remains quoted evidence."""
    return (item or {}).get("mode") or QUOTED_EVIDENCE_MODE


def is_absence_like(value):
    """Return whether a reviewed value can legitimately use absence evidence."""
    if value is None or value is False:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ABSENCE_LABELS
    if isinstance(value, list):
        return not value or all(is_absence_like(item) for item in value)
    return False


def evidence_errors(value, item, *, require_complete):
    """Validate evidence semantics and, when requested, completeness."""
    item = item or {}
    mode = evidence_mode(item)
    if mode not in EVIDENCE_MODES:
        return [f"unknown evidence mode: {mode}"]

    quote = str(item.get("quote") or "").strip()
    page = item.get("page")
    rule = str(item.get("rule") or "").strip()

    if mode == ABSENCE_EVIDENCE_MODE:
        errors = []
        if not is_absence_like(value):
            errors.append("absence evidence mode is only valid for an absence-like value")
        if quote or page is not None:
            errors.append("absence evidence must not contain a quote or page")
        if require_complete and not rule:
            errors.append("absence evidence requires a decision rationale")
        return errors

    if not require_complete:
        return []
    errors = []
    if not quote:
        errors.append("quoted evidence requires a literal quote")
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        errors.append("quoted evidence requires a positive physical page")
    return errors
