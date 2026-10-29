"""Tests for reconcile.py — Validation Protocol C field-level reconciliation.

Reconciles two value-only extraction records (model A vs model B) for the same
paper into a per-field {a, b, agree, tier} table + summary. Agreement is judged
AFTER normalisation, so format-only differences (Codex `"true"` vs Claude `True`;
enum labels `"multiple regression (>=2 IVs)"` vs `"multiple regression"`) do NOT
count as divergences — only genuine disagreements do.
"""
import json
import os

from reconcile import fields_agree, tier_of, reconcile_record

HERE = os.path.dirname(__file__)
ABT = os.path.join(HERE, "pilot_30", "ai_blind_test")


def _pair(key):
    cx = json.load(open(os.path.join(ABT, f"{key}.json")))
    cl = json.load(open(os.path.join(ABT, "claude", f"{key}.json")))
    return cx, cl


# --- fields_agree: format-only differences must NOT count as divergence ---

def test_string_bool_equals_real_bool():
    assert fields_agree("true", True) is True
    assert fields_agree("false", False) is True


def test_string_bool_genuine_difference_is_divergence():
    assert fields_agree("true", False) is False


def test_enum_parenthetical_stripped_in_lists():
    assert fields_agree(["multiple regression (>=2 IVs)"], ["multiple regression"]) is True


def test_scalar_parenthetical_elaboration_agrees():
    assert fields_agree("multiple regression (>=2 IVs)", "multiple regression") is True


def test_parenthetical_only_difference_is_divergence():
    # regression: both stripped to "other" and registered false concordance,
    # silently skipping blind-first adjudication of a real divergence
    assert fields_agree("other (refinery)", "other (hospital)") is False
    assert fields_agree(["other (refinery)"], ["other (hospital)"]) is False


def test_fully_parenthetical_values_do_not_collapse():
    # regression: both stripped to "" and registered false concordance
    assert fields_agree("(unclear)", "(not reported)") is False


def test_bool_vs_int_is_divergence():
    # regression: Python True == 1 made bool/count confusions concordant
    assert fields_agree(True, 1) is False
    assert fields_agree(False, 0) is False


def test_list_agreement_is_order_insensitive():
    assert fields_agree(["a", "b"], ["b", "a"]) is True


def test_partial_list_overlap_is_divergence():
    # Claude added "physical model" that Codex did not have.
    assert fields_agree(["simple intensity ratio"],
                        ["simple intensity ratio", "physical model"]) is False


def test_genuine_scalar_difference_is_divergence():
    assert fields_agree("continuous process", "buildings") is False


def test_none_agrees_with_none():
    assert fields_agree(None, None) is True


def test_mapping_key_order_is_irrelevant():
    assert fields_agree(
        {"metric": "R²", "value": "0.7"},
        {"value": "0.7", "metric": "R²"},
    ) is True


def test_list_of_objects_is_order_insensitive():
    a = [{"metric": "R²", "value": "0.7"}, {"metric": "MAE", "value": "2"}]
    b = [{"value": "2", "metric": "MAE"}, {"value": "0.7", "metric": "R²"}]
    assert fields_agree(a, b) is True


def test_b13b_comparison_ignores_only_nested_evidence_metadata():
    a = [{
        "metric": "R²", "value": "0.7", "unit": None, "period_or_context": "2022",
        "evidence_quote": "first quote", "page": 1,
    }]
    b = [{
        "period_or_context": "2022", "unit": None, "value": "0.7", "metric": "R²",
        "evidence_quote": "different quote", "page": 9, "non_contiguous_evidence": False,
    }]
    assert fields_agree(a, b, field="performance_metrics_reported") is True
    b[0]["value"] = "0.8"
    assert fields_agree(a, b, field="performance_metrics_reported") is False


def test_country_normalization_handles_article_and_separator_variants():
    assert fields_agree(
        "The Netherlands, Italy", "Italy; Netherlands", field="country_region"
    ) is True


def test_country_rule_does_not_leak_into_other_free_text():
    assert fields_agree(
        "The Netherlands, Italy", "Italy; Netherlands", field="sector_of_activity"
    ) is False


def test_reconcile_record_passes_field_context_to_normalizer():
    a = {"key": "rayyan-1", "level_a": {"country_region": "The Netherlands, Italy"}}
    b = {"key": "rayyan-1", "level_a": {"country_region": "Italy; Netherlands"}}
    result = reconcile_record(a, b)
    assert result["fields"][0]["agree"] is True


# --- tier_of: per Validation Protocol C section 2 ---

def test_consequential_fields_are_tier1():
    assert tier_of("eligibility", "methodological_eligibility") == 1
    assert tier_of("eligibility", "level_3b") == 1
    assert tier_of("eligibility", "paper_type") == 1


def test_level_b_fields_are_tier2():
    assert tier_of("level_b", "baseline_construction_method") == 2


def test_level_a_fields_are_tier3():
    assert tier_of("level_a", "country_region") == 3


def test_non_consequential_eligibility_field_is_not_tier1():
    # free-text context field, not one of the 4 consequential gates
    assert tier_of("eligibility", "ineligibility_reason") != 1


# --- reconcile_record on the real 535734 pair (the grave divergence) ---

def test_reconcile_flags_real_eligibility_divergence():
    cx, cl = _pair("rayyan-472535734")
    out = reconcile_record(cx, cl)
    by = {(f["section"], f["field"]): f for f in out["fields"]}
    assert by[("eligibility", "methodological_eligibility")]["agree"] is False
    assert by[("eligibility", "level_3b")]["agree"] is False
    assert by[("eligibility", "paper_type")]["agree"] is True  # both "single applied case"


def test_reconcile_summary_counts_tier1_divergences():
    cx, cl = _pair("rayyan-472535734")
    out = reconcile_record(cx, cl)
    assert out["key"] == "rayyan-472535734"
    # exactly methodological_eligibility + level_3b diverge among the Tier-1 gates
    assert out["summary"]["tier1_divergences"] == 2


def test_reconcile_concordant_pair_has_zero_tier1_divergences():
    # 536487: both models agree elig=true, 3b=true, multi-case study
    cx, cl = _pair("rayyan-472536487")
    out = reconcile_record(cx, cl)
    assert out["summary"]["tier1_divergences"] == 0
