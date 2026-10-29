"""Corpus B must be a subset of Corpus A (decision 2026-09-17, stage_c/B_SUBSET_A_2026-09-17.md)."""
import os
import pytest
from corpus_profile import enforce_b_subset_a, rosters

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_known_conflicts_are_removed_from_b():
    b, resolved = enforce_b_subset_a({"a1", "a2"}, {"a1", "x"}, resolved={"x"})
    assert b == {"a1"} and resolved == {"x"}


def test_unrecorded_conflict_stops_the_pipeline():
    with pytest.raises(AssertionError):
        enforce_b_subset_a({"a1"}, {"a1", "y"}, resolved={"x"})


@pytest.mark.skipif(not os.path.isdir(f"{ROOT}/production/claude/outputs/validated"), reason="production data absent")
def test_locked_rosters():
    r = rosters()
    a, b = set(r["corpus_a"]), set(r["corpus_b"])
    assert b <= a
    assert len(a) == 331 and len(b) == 40
    assert r["b_outside_a_resolved"] == ["rayyan-472535628", "rayyan-472535750"]
