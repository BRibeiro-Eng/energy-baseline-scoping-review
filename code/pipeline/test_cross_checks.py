"""Tests for cross_checks.py — Stage 4 deterministic consistency checks
(PROTOCOL.md 12.3, v2.1-revised one-way implication)."""
from cross_checks import cross_checks


def _rec(elig=True, l3b=False, org="buildings", la=None, lb=None):
    base_la = {"country_region": "Portugal", "type_of_organisation": org}
    if la:
        base_la.update(la)
    return {
        "eligibility": {"methodological_eligibility": elig, "level_3b": l3b},
        "level_a": base_la if elig else {},
        "level_b": lb or {},
    }


def _checks(rec):
    return {f["check"] for f in cross_checks(rec)}


def test_level_3b_requires_continuous_or_mixed_org():
    assert "level_3b_org_consistency" in _checks(_rec(l3b=True, org="buildings"))


def test_level_3b_with_continuous_org_is_clean():
    assert "level_3b_org_consistency" not in _checks(_rec(l3b=True, org="continuous process"))


def test_ineligible_with_populated_level_a_is_critical():
    rec = {"eligibility": {"methodological_eligibility": False, "level_3b": False},
           "level_a": {"country_region": "Spain"}, "level_b": {}}
    flags = cross_checks(rec)
    assert any(f["check"] == "ineligible_levela_scoping" and f["severity"] == "critical"
               for f in flags)


def test_b5_false_but_limitations_present_flags():
    rec = _rec(l3b=True, org="continuous process",
               lb={"identifies_model_limitations": False, "specific_limitations": ["fouling"]})
    assert "b5_b6_consistency" in _checks(rec)


def test_b8_false_but_adaptations_present_flags():
    rec = _rec(l3b=True, org="continuous process",
               lb={"proposes_adaptations": False, "adaptation_types": ["dynamic time window"]})
    assert "b8_b9_consistency" in _checks(rec)


def test_consistent_record_has_no_flags():
    assert cross_checks(_rec(elig=True, l3b=False, org="buildings")) == []
