"""Tests for audit_sampler.py — C-2.2 audit split (VALIDATION_PROTOCOL_C.md sec 4):
sampling unit = paper, error unit = cell (sec 4a). The SRS frame is ALL papers —
3B/borderline papers are NOT excluded (their other Level-A fields need audit
coverage; the C-2.1 paper-level exclusion was a defect). Census rosters (sec 4b)
are still reported. Per-field denominators n_v count concordant level_a cells
among sampled papers.
"""
from audit_sampler import census_rosters, per_field_denominators, select_audit


def _rec(key, l3b=False, borderline=False):
    return {"key": key, "level_3b": l3b,
            "borderline_review_synthesis_eligibility": borderline}


def _fld(field, a, b, agree, section="level_a", tier=3):
    return {"section": section, "field": field, "a": a, "b": b,
            "agree": agree, "tier": tier}


# --- census rosters (sec 4b) — still reported, no longer shrink the frame ---

def test_concordant_3b_censused_exhaustively():
    recs = [_rec(f"k{i}", l3b=True) for i in range(7)] + [_rec("x")]
    out = select_audit(recs)
    assert set(out["censuses"]["concordant_3b"]) == {f"k{i}" for i in range(7)}


def test_borderline_censused_exhaustively():
    recs = [_rec("a", borderline=True), _rec("b")]
    out = select_audit(recs)
    assert out["censuses"]["borderline"] == ["a"]


# --- frame semantics (sec 4a): frame = ALL papers passed in ---

def test_censused_papers_remain_in_srs_frame():
    recs = ([_rec(f"c{i}", l3b=True) for i in range(3)]
            + [_rec("bl", borderline=True)]
            + [_rec(f"k{i}") for i in range(100)])
    out = select_audit(recs, n=40, seed=44)
    assert out["frame_size"] == 104  # NO paper-level census exclusion


def test_frame_of_only_3b_papers_still_yields_sample():
    recs = [_rec(f"c{i}", l3b=True) for i in range(10)]
    out = select_audit(recs, n=40)
    assert out["frame_size"] == 10
    assert out["n_drawn"] == 10
    assert sorted(out["srs_sample"]) == sorted(f"c{i}" for i in range(10))


# --- SRS mechanics: n=40 default, seed 44, no duplicates, cap ---

def test_srs_draws_n_40_by_default():
    recs = [_rec(f"k{i}") for i in range(200)]
    out = select_audit(recs)
    assert out["n_requested"] == 40
    assert len(out["srs_sample"]) == 40


def test_srs_capped_at_frame_size():
    recs = [_rec(f"k{i}") for i in range(25)]
    out = select_audit(recs, n=40)
    assert out["n_drawn"] == 25
    assert len(out["srs_sample"]) == 25


def test_selection_is_deterministic_for_seed_44():
    recs = [_rec(f"k{i}") for i in range(100)]
    assert select_audit(recs, seed=44)["srs_sample"] == select_audit(recs, seed=44)["srs_sample"]


def test_sample_is_subset_without_duplicates():
    recs = [_rec(f"k{i}") for i in range(80)]
    sel = select_audit(recs)["srs_sample"]
    assert len(sel) == len(set(sel))
    assert set(sel) <= {f"k{i}" for i in range(80)}


# --- per-field denominators n_v (sec 4a) ---

def test_per_field_denominators_counts_concordant_level_a_cells():
    reconciled = {
        "p1": {"key": "p1", "fields": [_fld("year", 2020, 2020, True),
                                       _fld("country", "pt", "pt", True)]},
        "p2": {"key": "p2", "fields": [_fld("year", 2021, 2021, True)]},
    }
    assert per_field_denominators(["p1", "p2"], reconciled) == {"country": 1, "year": 2}


def test_per_field_denominators_excludes_divergent_cells():
    reconciled = {
        "p1": {"key": "p1", "fields": [_fld("year", 2020, 2019, False),
                                       _fld("country", "pt", "pt", True)]},
    }
    out = per_field_denominators(["p1"], reconciled)
    assert out["country"] == 1
    assert out["year"] == 0  # field seen, all cells divergent -> n_v = 0


def test_per_field_denominators_counts_null_null_concordant():
    # sec 4a error definitions: a concordant null-null cell IS auditable
    # (the auditor checks whether the PDF truly lacks the datum).
    reconciled = {
        "p1": {"key": "p1", "fields": [_fld("doi", None, None, True)]},
    }
    assert per_field_denominators(["p1"], reconciled) == {"doi": 1}


def test_per_field_denominators_ignores_non_level_a_sections():
    reconciled = {
        "p1": {"key": "p1", "fields": [
            _fld("level_3b", True, True, True, section="eligibility", tier=1),
            _fld("outcome_metric", "eii", "eii", True, section="level_b", tier=2),
            _fld("year", 2020, 2020, True),
        ]},
    }
    assert per_field_denominators(["p1"], reconciled) == {"year": 1}


def test_per_field_denominators_skips_keys_missing_from_reconciled():
    reconciled = {
        "p1": {"key": "p1", "fields": [_fld("year", 2020, 2020, True)]},
    }
    assert per_field_denominators(["p1", "ghost"], reconciled) == {"year": 1}


def test_per_field_denominators_on_real_reconcile_record_output():
    from reconcile import reconcile_record
    rec_a = {"key": "p1",
             "eligibility": {"level_3b": True},
             "level_a": {"year": 2020, "country": "Portugal", "doi": None},
             "level_b": {"outcome_metric": "EII"}}
    rec_b = {"key": "p1",
             "eligibility": {"level_3b": True},
             "level_a": {"year": 2021, "country": "portugal", "doi": None},
             "level_b": {"outcome_metric": "EII"}}
    reconciled = {"p1": reconcile_record(rec_a, rec_b)}
    out = per_field_denominators(["p1"], reconciled)
    # country concordant (case-normalised), doi concordant (null-null),
    # year divergent -> 0; eligibility/level_b sections ignored.
    assert out == {"country": 1, "doi": 1, "year": 0}


def test_per_field_denominators_is_sorted_by_field():
    reconciled = {
        "p1": {"key": "p1", "fields": [_fld("year", 2020, 2020, True),
                                       _fld("country", "pt", "pt", True),
                                       _fld("authors", "x", "x", True)]},
    }
    assert list(per_field_denominators(["p1"], reconciled)) == ["authors", "country", "year"]
