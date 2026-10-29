"""Tests for residual_report.py — C-2 per-field audited error reporting
(VALIDATION_PROTOCOL_C.md sec 5-6). Exact Clopper-Pearson CIs per field, never
pooled; pre-registered >=3/n recheck trigger; NO composite residual estimator.
"""
import math

from residual_report import (clopper_pearson_ci, rule_of_three_upper,
                             field_audit_result)


def test_cp_ci_zero_errors_lower_is_zero():
    low, high = clopper_pearson_ci(0, 40)
    assert low == 0.0
    assert 0 < high < 0.15


def test_cp_ci_zero_errors_n40_upper_near_9_percent():
    # exact two-sided CP upper for 0/40 is 1-(0.025)^(1/40) ~ 0.0881
    _, high = clopper_pearson_ci(0, 40)
    assert math.isclose(high, 1 - 0.025 ** (1 / 40), abs_tol=1e-3)


def test_cp_ci_all_errors_upper_is_one():
    low, high = clopper_pearson_ci(10, 10)
    assert high == 1.0
    assert low > 0.6


def test_cp_ci_within_unit_interval_and_ordered():
    low, high = clopper_pearson_ci(3, 40)
    assert 0 <= low <= 3 / 40 <= high <= 1


def test_cp_ci_empty_sample_is_uninformative():
    assert clopper_pearson_ci(0, 0) == (0.0, 1.0)


def test_cp_ci_2_of_15_regression():
    # locks the symmetry-branch fix in _beta_cdf (was returning upper=0.500)
    low, high = clopper_pearson_ci(2, 15)
    assert math.isclose(low, 0.01658, abs_tol=1e-4)
    assert math.isclose(high, 0.40460, abs_tol=1e-4)


def test_rule_of_three_upper_n40():
    # one-sided 95% upper bound for 0/40 ~ 7.2%
    assert math.isclose(rule_of_three_upper(40), 1 - 0.05 ** (1 / 40), abs_tol=1e-9)
    assert 0.07 < rule_of_three_upper(40) < 0.08


def test_field_result_reports_counts_not_composites():
    out = field_audit_result("year", errors=2, n=40, unaudited_concordant=300)
    assert out["errors"] == 2
    assert out["audited_n"] == 40
    assert math.isclose(out["error_rate"], 0.05)
    assert out["unaudited_concordant"] == 300
    assert "residual_rate" not in out  # composite deleted in C-2


def test_recheck_trigger_fires_at_3_of_40():
    assert field_audit_result("year", 3, 40, 0)["recheck_triggered"] is True
    assert field_audit_result("year", 2, 40, 0)["recheck_triggered"] is False


def test_zero_errors_reports_rule_of_three_bound():
    out = field_audit_result("country", 0, 40, 100)
    assert out["zero_error_upper_bound"] is not None
    assert 0.07 < out["zero_error_upper_bound"] < 0.08
    assert field_audit_result("country", 1, 40, 100)["zero_error_upper_bound"] is None
