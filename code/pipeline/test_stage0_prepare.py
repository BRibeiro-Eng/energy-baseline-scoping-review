"""
Unit tests for the deterministic decision functions of stage0_prepare.py.

These cover the pure logic specified in PROTOCOL.md:
  §8.1 notes parsing (rayyan decision, source string, snowball)
  §8.5 text-quality gates
  §8.6 retraction scan
  §8.7 composite garbled detection
  §8.8 deterministic eligibility gates
  §8.9 title/DOI vs metadata cross-check (wrong-PDF detection)
  §12.2 text normalisation (shared with grounding)
  document-type inference (§5.1 / §8.1)

Runnable standalone (no pytest needed):  python3 output/test_stage0_prepare.py
Also pytest-compatible:                   pytest output/test_stage0_prepare.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage0_prepare as s0


# ---------------------------------------------------------------- §12.2 normalise_text
def test_normalise_dehyphenates_end_of_line():
    assert s0.normalise_text("Imple-\nmenting energy") == "implementing energy"

def test_normalise_collapses_whitespace_and_lowercases():
    assert s0.normalise_text("THE   QUICK\t\nBrown") == "the quick brown"


# ---------------------------------------------------------------- §8.1 parse_notes
def test_parse_notes_included():
    n = 'Export Date: 24 February 2026 | RAYYAN-INCLUSION: {"Bernardo"=>"Included"}'
    r = s0.parse_notes(n)
    assert r["rayyan_decision"] == "Included"
    assert r["source_string"] is None        # no STRING-A/B markers in this export
    assert r["via_snowballing"] is False

def test_parse_notes_maybe_with_usernotes():
    n = '... | RAYYAN-INCLUSION: {"Bernardo"=>"Maybe"} | USER-NOTES: {"Bernardo"=>["x"]}'
    assert s0.parse_notes(n)["rayyan_decision"] == "Maybe"

def test_parse_notes_no_decision():
    assert s0.parse_notes("Export Date: x; Cited By: 0")["rayyan_decision"] is None

def test_parse_notes_string_markers_if_present():
    # real data has none, but the parser must classify correctly if they ever appear
    assert s0.parse_notes("foo STRING-A bar")["source_string"] == "A"
    assert s0.parse_notes("foo STRING-B bar")["source_string"] == "B"
    assert s0.parse_notes("STRING-A and STRING-B")["source_string"] == "both"

def test_parse_notes_snowball():
    assert s0.parse_notes("added via snowballing")["via_snowballing"] is True


# ---------------------------------------------------------------- §8.5 text quality
def test_text_quality_clean():
    pages = [{"page": 1, "text": "a" * 3000}, {"page": 2, "text": "b" * 3000}]
    q = s0.compute_text_quality(pages)
    assert q["total_chars"] == 6000
    assert q["mean_chars_per_page"] == 3000
    assert q["has_extractable_text"] is True

def test_text_quality_truncated_total_too_low():
    q = s0.compute_text_quality([{"page": 1, "text": "x" * 1000}])
    assert q["total_chars"] == 1000
    assert q["has_extractable_text"] is False   # total < 5000

def test_text_quality_image_only_mean_too_low():
    pages = [{"page": i, "text": "y" * 50} for i in range(200)]   # total 10000, mean 50
    q = s0.compute_text_quality(pages)
    assert q["mean_chars_per_page"] == 50
    assert q["has_extractable_text"] is False   # mean < 100

def test_text_quality_empty_no_crash():
    q = s0.compute_text_quality([])
    assert q["total_chars"] == 0
    assert q["mean_chars_per_page"] == 0
    assert q["has_extractable_text"] is False


# ---------------------------------------------------------------- §8.7 garbled detection
GOOD = ("This is the energy system and the process model based on the data analysis "
        "of performance in this industrial study with results from the method. ") * 5

def test_garbled_clean_text():
    g = s0.detect_garbled(GOOD)
    assert g["common_word_matches"] >= 8
    assert g["garbled_bytes"] is False
    assert g["garbled_glyphs"] is False

def test_garbled_glyphs_ascii_ok_but_no_words():
    # glyph remap: still ASCII letters, but no real English words
    text = "Lpsohphqwlqj hqhujb vbvwhp surfhvv prgho gdwd dqdobvlv uhvxowv phwkrg " * 5
    g = s0.detect_garbled(text)
    assert g["ascii_letter_fraction"] >= 0.45
    assert g["common_word_matches"] < 8
    assert g["garbled_glyphs"] is True
    assert g["garbled_bytes"] is False

def test_garbled_bytes_low_ascii_no_words():
    text = "\x00\x01\x02\x03\x04" + "±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃ€‚ƒ„…†‡ˆ‰Š‹ŒŽ" * 50
    g = s0.detect_garbled(text)
    assert g["ascii_letter_fraction"] < 0.45
    assert g["common_word_matches"] < 8
    assert g["garbled_bytes"] is True
    assert g["garbled_glyphs"] is False

def test_garbled_figure_heavy_false_positive_guard():
    # data_quality_report §2.5: low ASCII fraction (figures/numbers) but clean text.
    # Composite rule must NOT flag because common_word_matches >= 8.
    numbers = " ".join(str(i) for i in range(1, 900))   # pushes ascii-letter fraction down
    text = "the of and in to is for energy system process model data analysis " + numbers
    g = s0.detect_garbled(text)
    assert g["ascii_letter_fraction"] < 0.45
    assert g["common_word_matches"] >= 8
    assert g["garbled_bytes"] is False
    assert g["garbled_glyphs"] is False


# ---------------------------------------------------------------- §8.7b control-char glyph corruption
# Root cause (2026-07-23 investigation): a broken embedded-font ToUnicode CMap
# remaps glyphs into C0/C1 control codepoints. The composite garbled heuristic
# (detect_garbled) can't see it: a clean cover page or interleaved clean runs
# keep common_word_matches >= 8, which vetoes BOTH garbled_bytes and
# garbled_glyphs. ascii_letter_fraction is the WRONG lever (low for Japanese,
# ligatures, TOC dot-leaders). The right signal is per-page control-char fraction.
def _ctrl_page(frac, length=1000):
    """A page that is `frac` C1 control chars (\\x90), remainder ASCII letters."""
    n = int(round(length * frac))
    return "\x90" * n + "e" * (length - n)

def test_control_char_fraction_clean_text_is_zero():
    assert s0.control_char_fraction("The energy management system, ISO 50001.\n") == 0.0

def test_control_char_fraction_counts_c0_and_c1_controls():
    # \x03 (C0), \x90 \x87 \x9a (C1), \x01 (C0) = 5 controls out of 10 chars
    assert s0.control_char_fraction("\x03\x90\x87\x9a\x01abcde") == 0.5

def test_control_char_fraction_ignores_whitespace_controls():
    # tab/LF/CR/FF/VT are legitimate and must NOT count as corruption
    assert s0.control_char_fraction("abc\t\n\r\f\v") == 0.0

def test_control_char_fraction_non_latin_and_typography_are_clean():
    # real Japanese + fi-ligature + curly quotes carry ZERO control chars
    assert s0.control_char_fraction("日本建築 eﬁciency “quote” ©") == 0.0

def test_glyph_corruption_hard_flag_on_control_heavy_body():
    # clean cover page, garbled body (rayyan-472535370 shape)
    pages = [{"page": 1, "text": "clean cover page title " * 30},
             {"page": 2, "text": _ctrl_page(0.70)}]
    a = s0.assess_glyph_corruption(pages)
    assert a["garbled_control_glyphs"] is True
    assert a["max_page_control_fraction"] >= s0.PAGE_CONTROL_HARD

def test_glyph_corruption_localized_single_page_in_long_doc():
    # 1 garbled table page (28%) buried in a 14-page doc: whole-doc fraction is
    # ~2%, but per-page MAX must still flag it (rayyan-472536390 shape)
    pages = [{"page": i, "text": "clean prose text here " * 40} for i in range(1, 15)]
    pages[7]["text"] = _ctrl_page(0.28)
    a = s0.assess_glyph_corruption(pages)
    assert a["garbled_control_glyphs"] is True

def test_glyph_corruption_soft_band_flags_review_not_ocr():
    # 8% single page: localized (formula/table) -> soft review flag, NOT hard
    a = s0.assess_glyph_corruption([{"page": 1, "text": _ctrl_page(0.08)}])
    assert a["garbled_control_glyphs"] is False
    assert a["partial_glyph_corruption"] is True

def test_glyph_corruption_clean_pages_no_flags():
    a = s0.assess_glyph_corruption([{"page": 1, "text": "the energy system model " * 30}])
    assert a["garbled_control_glyphs"] is False
    assert a["partial_glyph_corruption"] is False
    assert a["max_page_control_fraction"] == 0.0

def test_glyph_corruption_japanese_paper_not_flagged():
    # bilingual JP/EN paper (rayyan-472536448): lots of non-Latin, no controls
    jp = "日本建築学会環境系論文集 " * 40 + "Building Envelope Design regression " * 20
    a = s0.assess_glyph_corruption([{"page": 1, "text": jp}])
    assert a["garbled_control_glyphs"] is False
    assert a["partial_glyph_corruption"] is False

def test_glyph_corruption_empty_pages_no_crash():
    a = s0.assess_glyph_corruption([])
    assert a["max_page_control_fraction"] == 0.0
    assert a["garbled_control_glyphs"] is False

def test_is_garbled_includes_control_glyphs():
    # a control-glyph corruption must trigger the fallback chain even when the
    # first-5000 composite (garbled_bytes/glyphs) reads clean
    g = {"garbled_bytes": False, "garbled_glyphs": False, "garbled_control_glyphs": True}
    assert s0.is_garbled(g) is True

def test_is_garbled_soft_flag_alone_does_not_trigger_fallback():
    # extract_text puts only the HARD flag into the dict; soft-only stays put
    g = {"garbled_bytes": False, "garbled_glyphs": False, "garbled_control_glyphs": False}
    assert s0.is_garbled(g) is False

# (cid:N) is the SAME broken-font failure as control codes, but rendered by
# pdfminer/pdfplumber as literal ASCII placeholder tokens — so control_char_
# fraction reads it as clean. Since pdfplumber sits BEFORE tesseract in the §8.4
# chain, undetected (cid:N) garbage gets ACCEPTED and OCR never runs.
def test_cid_token_fraction_clean_text_is_zero():
    assert s0.cid_token_fraction("Normal energy management text, no glyph tokens.") == 0.0

def test_cid_token_fraction_counts_placeholder_tokens():
    # three 9-char (cid:N) tokens (27 chars) + 3 real letters (30 total) -> 0.9
    assert s0.cid_token_fraction("(cid:146)(cid:145)(cid:150)abc") == 27 / 30

def test_glyph_corruption_flags_cid_token_garbage_as_hard():
    # pdfplumber "recovery" of a broken font = pages of (cid:N) tokens; must be
    # HARD so the fallback chain advances to OCR instead of accepting it
    body = "".join(f"(cid:{100 + i % 50})" for i in range(400))
    a = s0.assess_glyph_corruption([{"page": 1, "text": "clean cover title " * 20},
                                    {"page": 2, "text": body}])
    assert a["garbled_control_glyphs"] is True
    assert a["max_page_control_fraction"] >= s0.PAGE_CONTROL_HARD

def test_glyph_corruption_cid_and_control_share_one_signal():
    # both unresolved-glyph representations feed the same per-page maximum
    ctrl_pg = {"page": 1, "text": _ctrl_page(0.05)}          # soft on its own
    cid_pg = {"page": 2, "text": "(cid:70)(cid:71)" * 300}   # hard
    a = s0.assess_glyph_corruption([ctrl_pg, cid_pg])
    assert a["garbled_control_glyphs"] is True


# ---------------------------------------------------------------- §8.6 retraction scan
def test_retraction_first_page_marker():
    pages = [{"page": 1, "text": "RETRACTED ARTICLE: foo"}, {"page": 2, "text": "ok"}]
    assert s0.scan_retraction(pages) is True

def test_retraction_last_page_phrase_case_insensitive():
    pages = [{"page": i, "text": "clean"} for i in range(1, 6)]
    pages[-1]["text"] = "this article has been retracted by the publisher"
    assert s0.scan_retraction(pages) is True

def test_retraction_marker_only_in_middle_page_not_scanned():
    # markers only scanned on first 2 + last 2 pages; a 6-page doc with marker on p4 -> not found
    pages = [{"page": i, "text": "clean"} for i in range(1, 7)]
    pages[3]["text"] = "RETRACTED"
    assert s0.scan_retraction(pages) is False

def test_retraction_clean():
    pages = [{"page": 1, "text": "normal energy paper"}, {"page": 2, "text": "more"}]
    assert s0.scan_retraction(pages) is False

def test_retraction_en16001_withdrawn_is_not_a_retraction():
    # regression (reviewer 2026-06-18): "EN 16001 was withdrawn" describes the STANDARD
    # being superseded by ISO 50001, NOT an article retraction. Must NOT flag.
    pages = [{"page": 1, "text": "ISO 50001 was published in 2011, with EN 16001 being "
                                  "withdrawn the following year."},
             {"page": 2, "text": "energy baseline construction follows."}]
    assert s0.scan_retraction(pages) is False


# ---------------------------------------------------------------- §13.1 form-pilot sampler
def test_form_pilot_strata_counts_and_membership():
    inc = [f"rayyan-{i}" for i in range(100, 120)]
    may = [f"rayyan-{i}" for i in range(200, 220)]
    picks = s0.select_form_pilot(inc, may, seed=42, n_inc=3, n_maybe=2)
    assert len(picks) == 5
    assert sum(1 for p in picks if p in inc) == 3
    assert sum(1 for p in picks if p in may) == 2

def test_form_pilot_deterministic():
    inc = [f"rayyan-{i}" for i in range(100, 120)]
    may = [f"rayyan-{i}" for i in range(200, 220)]
    assert s0.select_form_pilot(inc, may) == s0.select_form_pilot(inc, may)

def test_form_pilot_order_independent_of_input_order():
    # sorting inside the sampler makes the result independent of input ordering
    inc = [f"rayyan-{i}" for i in range(100, 120)]
    may = [f"rayyan-{i}" for i in range(200, 220)]
    assert s0.select_form_pilot(inc, may) == s0.select_form_pilot(list(reversed(inc)),
                                                                  list(reversed(may)))


# ---------------------------------------------------------------- §8.9 title/DOI cross-check
TITLE = "A methodological framework to benchmark and monitor energy performance in textile SMEs"
DOI = "10.1016/j.esd.2022.11.001"

def test_wrong_pdf_correct_paper_title_and_doi_present():
    first = f"{TITLE}\nKasturi & Ayalur\nhttps://doi.org/{DOI}"
    r = s0.title_doi_match(TITLE, DOI, first, first, image_only=False)
    assert r["title_match_score"] >= 70
    assert r["doi_found_in_text"] is True
    assert r["wrong_pdf_likely"] is False

def test_wrong_pdf_flag_when_title_and_doi_absent():
    other = "Variable Vehicle Handling Using Four-Wheel Steer-by-Wire IEEE Trans Control"
    r = s0.title_doi_match(TITLE, DOI, other, other, image_only=False)
    assert r["title_match_score"] < 70
    assert r["doi_found_in_text"] is False
    assert r["wrong_pdf_likely"] is True

def test_wrong_pdf_doi_rescues_low_title():
    other = f"Some unrelated heading text but DOI present {DOI}"
    r = s0.title_doi_match(TITLE, DOI, other, other, image_only=False)
    assert r["wrong_pdf_likely"] is False     # DOI found -> accept

def test_wrong_pdf_not_flagged_when_image_only():
    other = "garbled or empty"
    r = s0.title_doi_match(TITLE, DOI, other, other, image_only=True)
    assert r["wrong_pdf_likely"] is False     # §8.9 requires extractable text to flag

def test_wrong_pdf_empty_doi_relies_on_title():
    first = f"{TITLE}\nauthors here"
    r = s0.title_doi_match(TITLE, "", first, first, image_only=False)
    assert r["doi_found_in_text"] is False
    assert r["wrong_pdf_likely"] is False     # title matches


# ---------------------------------------------------------------- §5.1/§8.1 doc-type inference
def test_doctype_conference_from_notes():
    row = {"journal": "Proc. of X", "notes": "Conference name: APMS 2025; Conference date: 2025",
           "publisher": "", "title": "Energy audit"}
    assert s0.infer_document_type(row) == "conference proceedings"

def test_doctype_journal_default():
    row = {"journal": "Applied Energy", "notes": "Export Date: 2026", "publisher": "Elsevier",
           "title": "EnPI for food industry"}
    assert s0.infer_document_type(row) == "journal article"

def test_doctype_dissertation():
    row = {"journal": "", "notes": "", "publisher": "Univ X",
           "title": "Energy management: a doctoral dissertation"}
    assert s0.infer_document_type(row) == "dissertation"

def test_doctype_grey_literature_reference_org():
    row = {"journal": "", "notes": "", "publisher": "International Energy Agency (IEA)",
           "title": "Energy efficiency indicators"}
    assert s0.infer_document_type(row) == "grey literature"


# ---------------------------------------------------------------- §8.8 eligibility gates
def test_doc_type_eligible():
    assert s0.doc_type_eligible("journal article") is True
    assert s0.doc_type_eligible("conference proceedings") is True
    assert s0.doc_type_eligible("dissertation") is True
    assert s0.doc_type_eligible("grey literature") is True
    assert s0.doc_type_eligible("other") is False

def test_year_eligible():
    assert s0.year_eligible(2020, False) is True
    assert s0.year_eligible(1996, False) is True
    assert s0.year_eligible(1995, False) is False
    assert s0.year_eligible(1990, True) is True       # snowball bypasses
    assert s0.year_eligible(None, False) is False

def test_language_eligible():
    assert s0.language_eligible("English", False) is True
    assert s0.language_eligible("German", False) is False
    assert s0.language_eligible("German", True) is True   # manual override


# ---------------------------------------------------------------- v2.2 §8.10 — pdf.pages persistence
def test_v22_bundle_persists_pdf_pages_for_real_extraction():
    """v2.2 tooling fix: build_bundle must include pdf.pages in the bundle so
    that Stage 1/2/3 agents and the §12.2 grounding verifier read the same
    text (the v2.1 omission caused 4 off-by-one page errors + glyph
    corruption in the re-pilot)."""
    import json, os
    # Use an existing stage0 bundle from disk (post-fix re-run)
    sample = os.path.join(os.path.dirname(__file__), "stage0", "rayyan-472535376.json")
    if not os.path.exists(sample):
        return  # Skip when bundles not yet generated; this test runs after stage0 run
    b = json.load(open(sample))
    assert b["pdf"]["available"] is True
    assert "pages" in b["pdf"], "v2.2 fix: pdf.pages MUST be in the bundle"
    pages = b["pdf"]["pages"]
    assert isinstance(pages, list) and len(pages) >= 1
    assert all("page" in p and "text" in p for p in pages), "each entry: {page, text}"
    assert pages[0]["page"] == 1, "page numbering is 1-indexed (PDF physical page)"
    assert len(pages) == b["pdf"]["n_pages"], "pages array length must match n_pages"


def test_v22_bundle_pages_for_ocr_recovered_papers():
    """For OCR-recovered papers (the 5 in ocr_recovered/), pages array has 1
    entry containing the entire OCR text (no page boundaries available).
    The bundle should still have pdf.pages — Stage 1/2/3 won't crash."""
    import json, os
    for key in ("rayyan-472535622", "rayyan-472535635", "rayyan-472535679",
                "rayyan-472536601", "rayyan-472535520"):
        sample = os.path.join(os.path.dirname(__file__), "stage0", f"{key}.json")
        if not os.path.exists(sample):
            return
        b = json.load(open(sample))
        if b["pdf"]["extraction_backend"] != "ocr_recovered_preflight":
            continue
        assert "pages" in b["pdf"], f"{key}: OCR-recovered bundle missing pdf.pages"
        pages = b["pdf"]["pages"]
        assert len(pages) == 1, f"{key}: OCR-recovered bundle should have 1 page entry"
        assert pages[0]["page"] == 1
        assert len(pages[0]["text"]) > 100, f"{key}: OCR text must be non-trivial"


# ---------------------------------------------------------------- standalone runner
def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = failed = 0
    for fn in fns:
        try:
            fn()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({len(fns)} total)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run())
