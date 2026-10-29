"""residual_report.py — Validation Protocol C-2 sections 5-6.

Per-field audited error counts with EXACT Clopper-Pearson 95% CIs, plus the
pre-registered threshold trigger (>=3/n errors on a Level-A field -> scripted
corpus-wide recheck). Metrics are reported per field / per instrument, NEVER
pooled: C-1.0's composite R-hat (which multiplied a bias-dominated and a
noise-dominated term into one number) and Gwet's AC1 are deleted
(REVIEW_ROUND2_C2.md, confirmed defects 1/5 + red-team A6).
"""
import math

LEVEL_A_ERROR_TRIGGER = 3  # C-2.2 sec 6a: ABSOLUTE count e_v >= 3 on any Level-A field (n_v reported alongside; sensitivity varies with n_v)


def _beta_ppf(q, a, b, tol=1e-10):
    """Inverse regularized incomplete beta via bisection (deterministic, stdlib-only)."""
    lo, hi = 0.0, 1.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if _beta_cdf(mid, a, b) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta (Numerical Recipes, Lentz)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
    h = d
    for m in range(1, 200):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1.0 + aa / (c if abs(c) > 1e-30 else 1e-30)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1.0 + aa / (c if abs(c) > 1e-30 else 1e-30)
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def _beta_cdf(x, a, b):
    """Regularized incomplete beta I_x(a,b) (Numerical Recipes betai)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                + a * math.log(x) + b * math.log(1.0 - x))
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def clopper_pearson_ci(errors, n, alpha=0.05):
    """Exact (Clopper-Pearson) two-sided CI for a binomial proportion.
    Empty sample -> (0, 1) (uninformative)."""
    if n == 0:
        return (0.0, 1.0)
    if errors == 0:
        low = 0.0
    else:
        low = _beta_ppf(alpha / 2, errors, n - errors + 1)
    if errors == n:
        high = 1.0
    else:
        high = _beta_ppf(1 - alpha / 2, errors + 1, n - errors)
    return (low, high)


def rule_of_three_upper(n):
    """One-sided 95% upper bound when 0 errors observed in n (~3/n)."""
    return 1.0 - 0.05 ** (1.0 / n) if n > 0 else 1.0


def field_audit_result(field, errors, n, unaudited_concordant, trigger=LEVEL_A_ERROR_TRIGGER):
    """C-2 sec 5 item 3: per-field audited error count + exact CI + trigger flag.

    unaudited_concordant is reported alongside so the reader sees what the bound
    covers; it is NOT multiplied into a composite (no residual-rate product).
    """
    low, high = clopper_pearson_ci(errors, n)
    return {
        "field": field,
        "errors": errors,
        "audited_n": n,
        "error_rate": errors / n if n else None,
        "ci_low": low,
        "ci_high": high,
        "zero_error_upper_bound": rule_of_three_upper(n) if errors == 0 else None,
        "unaudited_concordant": unaudited_concordant,
        "recheck_triggered": errors >= trigger,  # pre-registered sec 6a action
    }
