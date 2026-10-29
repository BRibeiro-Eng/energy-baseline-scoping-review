"""capture_recapture.py — SUPERSEDED (C-2.0, 2026-07-03). Historical record only.

Deleted from the validation design by Protocol C-2 (REVIEW_ROUND2_C2.md, confirmed
defect 2): the two detectors had MISMATCHED ERROR UNIVERSES (the keyword hunt can
only catch Corpus-B false negatives while the audit catches all error classes,
violating Lincoln-Petersen's closed-population requirement) and n12=0 was the
likely outcome at the expected counts, making Chapman's N-hat decorative. Replaced
by the exhaustible FN candidate-union census with closure rule (fn_hunt.py;
VALIDATION_PROTOCOL_C.md sec 3 step 4) — instead of estimating what the detectors
missed, the union is made broad enough for the human to empty it.

Kept (with tests) as the provenance record of the C-1.0 design. Do NOT wire into
the production pipeline.

Original docstring: bounds the concordant errors that escape BOTH detectors (the
stratified blind audit x the adversarial false-negative hunt) via the Chapman
bias-corrected Lincoln-Petersen estimator, with an independence caveat.
"""
import math


def chapman_estimate(n1, n2, n12):
    """Two-source capture-recapture (Chapman estimator).

    n1  = errors caught by detector 1 (stratified blind audit)
    n2  = errors caught by detector 2 (adversarial FN-hunt / extra detector)
    n12 = errors caught by both (overlap)

    Returns: n_hat (estimated total errors, incl. unseen), missed_hat (caught by
    neither), observed (caught by >=1), se, ci_low, ci_high (95% normal approx).
    """
    n_hat = ((n1 + 1) * (n2 + 1) / (n12 + 1)) - 1
    observed = n1 + n2 - n12
    missed = n_hat - observed
    var = (
        (n1 + 1) * (n2 + 1) * (n1 - n12) * (n2 - n12)
        / (((n12 + 1) ** 2) * (n12 + 2))
    )
    se = math.sqrt(var) if var > 0 else 0.0
    return {
        "n_hat": n_hat,
        "missed_hat": missed,
        "observed": observed,
        "se": se,
        "ci_low": n_hat - 1.96 * se,
        "ci_high": n_hat + 1.96 * se,
    }
