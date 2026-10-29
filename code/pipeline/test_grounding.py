"""Tests for grounding.py — Stage 4 evidence-grounding (PROTOCOL.md 12.2).

Every AI-extracted field with an evidence_quote must be a (normalised) fuzzy
substring of the claimed PDF page, with a length-sensitive threshold. This is the
structural defence against hallucinated quotes.

Covers the frozen v2.2.1 contract (PROTOCOL.md 6.3; Validation Protocol C-2):
the eight ordered normalisation rules, the Greek-beta fi/fl fallback retry,
non-contiguous evidence (list quote + parallel list page), and failure-context
logging for the >2-similar-failures extension trigger.
"""
from grounding import collect_failure_patterns, ground_quote, normalize_text

PAGES = [
    {"page": 1, "text": "The energy baseline was built using multiple regression."},
    {"page": 2, "text": "We report an R2 of 0.95 for the model fit."},
]


def test_exact_quote_grounded_on_claimed_page():
    out = ground_quote("multiple regression", 1, PAGES)
    assert out["grounded"] is True
    assert out["locator"] == 1
    assert out["page_unverified"] is False


def test_absent_quote_is_not_grounded():
    out = ground_quote("catalyst deactivation in the reactor unit", 1, PAGES)
    assert out["grounded"] is False
    assert out["locator"] is None


def test_quote_on_wrong_page_flagged_unverified():
    out = ground_quote("R2 of 0.95", 1, PAGES)  # claimed page 1, really page 2
    assert out["grounded"] is True
    assert out["locator"] == 2
    assert out["page_unverified"] is True


def test_linebreak_hyphenation_is_normalised():
    pages = [{"page": 1, "text": "the regres-\nsion model was validated"}]
    out = ground_quote("regression model", 1, pages)
    assert out["grounded"] is True


def test_short_quote_requires_high_similarity():
    pages = [{"page": 1, "text": "the value of beta was high"}]
    out = ground_quote("gamma", 1, pages)  # 5 chars, not present
    assert out["grounded"] is False


def test_normalize_collapses_whitespace_and_case():
    assert normalize_text("  Multiple   Regression\n Model ") == "multiple regression model"


# --- 6.3 v2.2.1 normalisation rules, one test per rule, in protocol order ---

def test_rule1_control_characters_stripped_except_lf_tab():
    # U+0000-U+001F stripped (e.g. U+0003 ETX from Symbol-font fallbacks) ...
    assert normalize_text("mod\x03el \x00fit\x1f") == "model fit"
    # ... except LF and TAB, which survive rule 1 (then collapse under rule 7)
    assert normalize_text("a\tb\nc") == "a b c"
    # CR is not exempted: stripped, not turned into whitespace
    assert normalize_text("energy\rbaseline") == "energybaseline"


def test_rule2_soft_hyphen_removed():
    assert normalize_text("regres­sion") == "regression"


def test_rule3_linebreak_hyphenation_joined():
    assert normalize_text("vari-\n  ables") == "variables"
    # order sensitivity: rule 1 (CR strip) runs first, so Windows line
    # endings still join
    assert normalize_text("vari-\r\n  ables") == "variables"


def test_rule4_ligatures_unified():
    assert normalize_text("eﬃcient") == "efficient"   # U+FB03 ffi
    assert normalize_text("ﬁt") == "fit"              # U+FB01 fi
    assert normalize_text("workﬂow") == "workflow"    # U+FB02 fl
    assert normalize_text("oﬀset") == "offset"        # U+FB00 ff
    assert normalize_text("baﬄe") == "baffle"         # U+FB04 ffl


def test_rule4_greek_beta_symbol_maps_to_fi_by_default_fl_on_request():
    assert normalize_text("signiϐcant") == "significant"
    assert normalize_text("workϐow", beta_variant="fl") == "workflow"


def test_rule5_dashes_unified():
    assert normalize_text("2010–2015") == "2010-2015"  # en dash
    assert normalize_text("a—b") == "a-b"              # em dash
    assert normalize_text("a‒b") == "a-b"              # figure dash
    assert normalize_text("−5 kwh") == "-5 kwh"        # minus sign


def test_rule6_quotes_unified():
    assert normalize_text("“model”") == '"model"'   # curly double
    assert normalize_text("„model") == '"model'          # low double quote
    assert normalize_text("don’t ‘x’") == "don't 'x'"  # curly single
    assert normalize_text("don‚t") == "don't"            # low single quote
    assert normalize_text("don¶t") == "don't"            # pilcrow artefact
    assert normalize_text("don¹t") == "don't"            # superscript-1 artefact


def test_rule7_whitespace_collapsed():
    assert normalize_text("a  b\t\tc \n d") == "a b c d"


def test_rule8_lowercase_and_strip():
    assert normalize_text("  MODEL Fit  ") == "model fit"


# --- Greek-beta fi/fl fallback retry in ground_quote (6.3 rule 4) ---

def test_beta_symbol_grounds_via_default_fi_substitution():
    pages = [{"page": 1, "text": "a statistically significant effect was found"}]
    out = ground_quote("signiϐcant effect", 1, pages)
    assert out["grounded"] is True
    assert out["page_unverified"] is False


def test_beta_symbol_in_quote_falls_back_to_fl():
    pages = [{"page": 1, "text": "The workflow was validated."}]
    out = ground_quote("workϐow", 1, pages)  # fi fails, fl grounds
    assert out["grounded"] is True
    assert out["locator"] == 1
    assert out["page_unverified"] is False
    assert out["beta_variant"] == "fl"


def test_beta_symbol_in_page_text_triggers_fallback_too():
    pages = [{"page": 1, "text": "The workϐow was validated."}]
    out = ground_quote("workflow", 1, pages)
    assert out["grounded"] is True
    assert out["beta_variant"] == "fl"


def test_beta_symbol_quote_still_fails_when_absent():
    out = ground_quote("workϐow", 1, PAGES)
    assert out["grounded"] is False


# --- Non-contiguous evidence (6.3 v2.2: list quote + parallel list page) ---

def test_non_contiguous_all_substrings_ground():
    out = ground_quote(["multiple regression", "R2 of 0.95"], [1, 2], PAGES)
    assert out["grounded"] is True
    assert out["locator"] == [1, 2]
    assert out["page_unverified"] is False
    assert out["non_contiguous"] is True
    assert len(out["substring_results"]) == 2
    assert all(r["grounded"] for r in out["substring_results"])


def test_non_contiguous_each_substring_checked_against_its_own_page():
    # pages swapped: both substrings ground elsewhere -> page_unverified
    out = ground_quote(["multiple regression", "R2 of 0.95"], [2, 1], PAGES)
    assert out["grounded"] is True
    assert out["locator"] == [1, 2]
    assert out["page_unverified"] is True


def test_non_contiguous_one_failing_substring_fails_the_aggregate():
    out = ground_quote(["multiple regression", "catalyst deactivation"], [1, 2], PAGES)
    assert out["grounded"] is False
    assert out["substring_results"][0]["grounded"] is True
    assert out["substring_results"][1]["grounded"] is False
    assert "failure_context" in out["substring_results"][1]


def test_non_contiguous_length_mismatch_is_clean_failure():
    out = ground_quote(["multiple regression", "R2 of 0.95"], [1], PAGES)
    assert out["grounded"] is False
    assert out["locator"] is None
    assert "error" in out
    assert out["substring_results"] == []


def test_non_contiguous_list_quote_with_scalar_page_is_clean_failure():
    out = ground_quote(["multiple regression"], 1, PAGES)
    assert out["grounded"] is False
    assert "error" in out


def test_non_contiguous_empty_list_is_clean_failure():
    out = ground_quote([], [], PAGES)
    assert out["grounded"] is False
    assert "error" in out


# --- Failure context (6.3 future-proofing note) ---

def test_failure_context_contents():
    quote = "catalyst deactivation in the reactor unit"
    out = ground_quote(quote, 1, PAGES)
    assert out["grounded"] is False
    ctx = out["failure_context"]
    assert ctx["quote"] == quote
    assert ctx["normalized_quote"] == normalize_text(quote)
    assert ctx["score"] == out["score"]
    assert ctx["snippet_page"] in (1, 2)
    # bounded ~200-char snippet of the normalised target-page text
    assert isinstance(ctx["snippet"], str)
    assert len(ctx["snippet"]) <= 200
    target = next(p["text"] for p in PAGES if p["page"] == ctx["snippet_page"])
    assert ctx["snippet"] in normalize_text(target)


# --- collect_failure_patterns (6.3 >2-similar-failures extension trigger) ---

def test_collect_failure_patterns_groups_by_artefact_class():
    failures = [
        ground_quote("catalytϐc reforming", 1, PAGES),
        ground_quote("speciϐc energy use", 2, PAGES),
        ground_quote("ϐxed effects estimator", 1, PAGES),
        ground_quote("the “model” collapsed", 1, PAGES),
        ground_quote(["don¶t know", "R2 of 0.95"], [1, 2], PAGES),
    ]
    assert all(f["grounded"] is False for f in failures)

    report = collect_failure_patterns(failures)
    patterns = report["patterns"]
    assert len(patterns["greek_beta_symbol"]) == 3
    assert len(patterns["curly_quotes"]) == 1
    assert len(patterns["pilcrow_superscript_one"]) == 1
    # >2 similar failures -> candidate for extending the 6.3 spec
    assert report["extension_candidates"] == ["greek_beta_symbol"]


def test_collect_failure_patterns_empty_input():
    report = collect_failure_patterns([])
    assert report["patterns"] == {}
    assert report["extension_candidates"] == []
