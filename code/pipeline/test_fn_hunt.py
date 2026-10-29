"""Tests for fn_hunt.py — FN candidate-union CENSUS for Corpus B
(VALIDATION_PROTOCOL_C.md C-2 sec 3 step 4; supersedes the capture-recapture
detector-2 role).

Scans the text of records the consensus placed OUTSIDE Corpus B for
continuous-process terminology, unions three detectors into the census
work-list, and iterates closure passes. Deliberately over-inclusive: missing a
genuine Corpus B paper (false negative) is the costliest error for SQ2-4; a
human empties the list.
"""
from fn_hunt import scan_text, hunt, candidate_union, closure_pass


def test_scan_finds_continuous_process_term():
    assert "refinery" in scan_text("applied at an oil refinery in Texas")


def test_scan_is_case_insensitive():
    assert "cement" in scan_text("A CEMENT plant case study")


def test_scan_respects_word_boundaries():
    # "paper" alone (a research paper) must NOT trigger
    assert scan_text("this research paper studies office HVAC") == []


def test_scan_matches_multiword_term():
    assert "pulp and paper" in scan_text("the pulp and paper industry baseline")


def test_scan_returns_empty_for_clean_text():
    assert scan_text("a study of office buildings energy use") == []


def test_hunt_flags_excluded_record_with_term():
    items = [
        {"key": "a", "level_3b": False, "text": "energy audit at a steel mill"},
        {"key": "b", "level_3b": False, "text": "office building energy study"},
    ]
    out = hunt(items)
    assert {r["key"] for r in out} == {"a"}
    assert "steel" in out[0]["terms"]


def test_hunt_ignores_already_corpus_b():
    items = [{"key": "a", "level_3b": True, "text": "refinery application"}]
    assert hunt(items) == []


def test_hunt_accepts_extra_terms_for_closure_expansion():
    items = [{"key": "a", "level_3b": False, "text": "an aluminium smelter EnPI"}]
    assert hunt(items) == []  # not in the base lexicon
    out = hunt(items, extra_terms=["aluminium smelter"])
    assert out and out[0]["key"] == "a"


def test_candidate_union_merges_three_detectors_with_provenance():
    union = candidate_union(
        model_flagged=["a", "b"],
        lexicon_hits=[{"key": "b", "terms": ["refinery"]}, {"key": "c", "terms": ["kiln"]}],
        recall_flagged=["d"],
    )
    by_key = {u["key"]: u for u in union}
    assert set(by_key) == {"a", "b", "c", "d"}
    assert by_key["b"]["detectors"] == ["lexicon", "model_flags"]
    assert by_key["b"]["terms"] == ["refinery"]
    assert by_key["d"]["detectors"] == ["recall_pass"]


def test_closure_pass_returns_only_new_candidates():
    items = [
        {"key": "a", "level_3b": False, "text": "a glass melting furnace"},
        {"key": "b", "level_3b": False, "text": "an aluminium smelter"},
    ]
    # 'a' already reviewed; lexicon expanded with the confirmed FN's vocabulary
    new = closure_pass(items, reviewed_keys=["a"], extra_terms=["aluminium smelter"])
    assert [h["key"] for h in new] == ["b"]


def test_closure_pass_empty_means_census_closed():
    items = [{"key": "a", "level_3b": False, "text": "office HVAC retrofit"}]
    assert closure_pass(items, reviewed_keys=[], extra_terms=[]) == []
