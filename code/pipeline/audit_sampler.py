"""audit_sampler.py — Validation Protocol C-2.2 section 4.

C-2.2 sec 4a: sampling unit = PAPER, error unit = CELL. The SRS frame is ALL
eligible papers with reconciled Level-A data — including papers whose
consequential cells are censused (a 3B or borderline paper's *other* Level-A
fields still need audit coverage). The C-2.1 paper-level exclusion was a
defect: it removed whole 3B/borderline papers from the frame, so their
Level-A fields could never be audited.

- Sec 4b CENSUSES (never sampled): concordant level_3b=true; concordant
  borderline_review_synthesis_eligibility=true; FN-detector hits (handled in
  fn_hunt.py). Rosters are reported for the exhaustive censuses but do NOT
  shrink the paper frame.
- Sec 4a SAMPLE: simple random sample of n=40 papers (seed 44), without
  replacement, from the full frame. Per-field denominators n_v are computed
  at audit time as the concordant, evaluable, non-censused CELLS among the
  sampled papers (per_field_denominators); report e_v/n_v, never e_v/40.
  SRS makes the plain per-field binomial interval valid by construction —
  no strata, no weights.
"""
import random

SRS_N = 40           # fixed parameter #1 (C-2 sec 12); overrun floor 30 (sec 6b)
SRS_SEED = 44


def census_rosters(records):
    """Exhaustive census rosters (C-2.2 sec 4b). Reported as complete
    enumerations; they no longer remove papers from the sec 4a frame."""
    return {
        "concordant_3b": sorted(r["key"] for r in records if r.get("level_3b")),
        "borderline": sorted(
            r["key"] for r in records
            if not r.get("level_3b") and r.get("borderline_review_synthesis_eligibility")
        ),
    }


def select_audit(records, n=SRS_N, seed=SRS_SEED):
    """C-2.2 audit selection: census rosters + SRS over ALL papers (sec 4a).

    records: concordant papers, each {key, level_3b, borderline_review_synthesis_eligibility, ...}.
    The frame is every paper passed in — no paper-level census exclusion.
    Returns {srs_sample, censuses, frame_size, n_requested, n_drawn}.
    """
    censuses = census_rosters(records)
    frame = sorted(r["key"] for r in records)

    rng = random.Random(seed)
    n_drawn = min(n, len(frame))
    sample = sorted(rng.sample(frame, n_drawn))

    return {
        "srs_sample": sample,
        "censuses": censuses,
        "frame_size": len(frame),
        "n_requested": n,
        "n_drawn": n_drawn,
    }


def per_field_denominators(sample_keys, reconciled_records):
    """Per-field audit denominators n_v (C-2.2 sec 4a).

    sample_keys: papers drawn by select_audit. reconciled_records: key ->
    reconcile_record() output. Counts, per Level-A field, the sampled cells
    that are concordant (agree=True); divergent cells are excluded (they are
    adjudicated via sec 3-Step-3/3b, not audited). Concordant null-null cells
    ARE counted — sec 4a error definitions make them auditable (the auditor
    checks whether the PDF genuinely lacks the datum). No census exclusion
    applies at Level-A cell level: the sec 4b censuses cover consequential
    Tier-1 cells, which are not level_a section cells. Sampled keys missing
    from reconciled_records are skipped. Returns {field: n_v}, sorted.
    """
    counts = {}
    for key in sample_keys:
        rec = reconciled_records.get(key)
        if rec is None:
            continue
        for f in rec["fields"]:
            if f["section"] != "level_a":
                continue
            counts.setdefault(f["field"], 0)
            if f["agree"]:
                counts[f["field"]] += 1
    return dict(sorted(counts.items()))
