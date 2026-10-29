"""cross_checks.py — Stage 4 deterministic consistency checks (PROTOCOL.md 12.3).

Returns a list of violated-rule flags for a merged record. v2.1-revised: the
level_3b<->org rule is a ONE-WAY implication (level_3b=true => org in
{continuous process, mixed}); the inverse is legitimate and not flagged.
"""


def cross_checks(record):
    """Return [{check, severity, detail}] for each violated consistency rule."""
    flags = []
    el = record.get("eligibility", {}) or {}
    la = record.get("level_a", {}) or {}
    lb = record.get("level_b", {}) or {}

    elig = el.get("methodological_eligibility")
    l3b = el.get("level_3b")
    org = la.get("type_of_organisation")

    # level_3b=true => org in {continuous process, mixed} (one-way)
    if l3b and org not in ("continuous process", "mixed"):
        flags.append({"check": "level_3b_org_consistency", "severity": "flag",
                      "detail": f"level_3b=true but type_of_organisation={org!r}"})

    # methodological_eligibility=false => all Level A null/empty (C2 scoping rule)
    if elig is False:
        populated = sorted(k for k, v in la.items() if v not in (None, "", [], {}))
        if populated:
            flags.append({"check": "ineligible_levela_scoping", "severity": "critical",
                          "detail": f"eligibility=false but level_a populated: {populated}"})

    # B5=false => B6 empty
    if lb.get("identifies_model_limitations") is False and lb.get("specific_limitations"):
        flags.append({"check": "b5_b6_consistency", "severity": "flag",
                      "detail": "identifies_model_limitations=false but specific_limitations non-empty"})

    # B8=false => B9 empty
    if lb.get("proposes_adaptations") is False and lb.get("adaptation_types"):
        flags.append({"check": "b8_b9_consistency", "severity": "flag",
                      "detail": "proposes_adaptations=false but adaptation_types non-empty"})

    # B11 refinery => org continuous process AND sector mentions refinery/petrochemical
    if lb.get("empirical_refinery_application") is True:
        sector = (la.get("sector_of_activity") or "").lower()
        if org != "continuous process" or not any(t in sector for t in ("refin", "petrochem")):
            flags.append({"check": "b11_refinery_consistency", "severity": "flag",
                          "detail": "empirical_refinery_application=true but org/sector inconsistent"})

    return flags
