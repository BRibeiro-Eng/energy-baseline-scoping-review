"""Tests for capture_recapture.py — bounds the concordant errors that escape
BOTH detectors (stratified audit x adversarial FN-hunt) per
VALIDATION_PROTOCOL_C.md section 5.2. Chapman bias-corrected Lincoln-Petersen.
"""
from capture_recapture import chapman_estimate


def test_chapman_point_estimate_known_case():
    # N_hat = ((n1+1)(n2+1)/(n12+1)) - 1 = (11*9/5)-1 = 18.8
    out = chapman_estimate(n1=10, n2=8, n12=4)
    assert abs(out["n_hat"] - 18.8) < 1e-9


def test_perfect_overlap_implies_no_missed():
    # both detectors caught exactly the same 5 errors -> estimate no hidden ones
    out = chapman_estimate(n1=5, n2=5, n12=5)
    assert abs(out["n_hat"] - 5.0) < 1e-9
    assert abs(out["missed_hat"] - 0.0) < 1e-9


def test_missed_is_nhat_minus_observed():
    out = chapman_estimate(n1=10, n2=8, n12=4)
    observed = 10 + 8 - 4
    assert abs(out["missed_hat"] - (out["n_hat"] - observed)) < 1e-9


def test_no_overlap_implies_large_missed():
    # disjoint detections -> many errors caught by neither
    out = chapman_estimate(n1=5, n2=5, n12=0)
    assert out["missed_hat"] > 10


def test_returns_confidence_interval():
    out = chapman_estimate(n1=10, n2=8, n12=4)
    assert out["ci_low"] <= out["n_hat"] <= out["ci_high"]


def test_zero_errors_is_degenerate_safe():
    out = chapman_estimate(n1=0, n2=0, n12=0)
    assert out["n_hat"] == 0.0
    assert out["missed_hat"] == 0.0
