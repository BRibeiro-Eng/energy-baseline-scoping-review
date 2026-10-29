#!/usr/bin/env python3
"""Stage C grounding — three separate checks, exact-match acceptance.

`output/grounding.py` stays untouched: its behaviour is recorded in the provenance of the
v2.2.1 corpus-wide check and changing it would invalidate that result.

WHAT THIS VERSION FIXES, after synthetic reproductions showed the previous one accepted
content changes:

  * RULE 9 NO LONGER DELETES NUMBERS FROM RUNNING TEXT. The previous pattern erased any
    standalone 2-5 digit integer from BOTH the quote and the page, so 'The model used 90
    samples' was accepted against a page saying 20. Line numbers are now stripped only where
    they actually occur — alone on a line, or at a line's start or end — on the RAW text,
    before whitespace is collapsed. A digit run inside a sentence is never touched, so every
    number in a quote is still verified against the source.

  * RULE 10 NO LONGER ACCEPTS. Column-interleaving tolerance was letting any word-deletion of
    a real passage through, including meaning inversions: 'the rolling window does improve the
    error' was accepted against '... does not improve ...'. Rule 10 is now a ROUTING class:
    it produces `review_candidate`, never a pass. Only an exact match after normalisation is
    a pass. One genuinely two-column paper therefore needs its quotes read by a human, which
    is the correct price.

  * A NEGATION GUARD rejects outright any candidate span whose negation tokens the quote does
    not carry. A dropped 'not' is a fabrication, not a near-miss.

  * A VALUE WITHOUT A QUOTE IS A FAILURE, NOT AN ABSENCE. The previous version counted any
    missing quote as `absent_no_quote`, so a record of substantive values all marked
    `direct statement` with no evidence at all passed clean. Only values whose content IS an
    absence may omit a quote.

  * LIST-VALUED ABSENCES are recognised: `["not reported"]` is an absence.

  * BOTH LIGATURE VARIANTS are tried, as the frozen checker does.

  * G3 counts only values that can carry a `support_class`.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grounding import normalize_text  # noqa: E402

# rule 9 — line numbering is detected, never guessed from position.
#
# The previous version stripped any short digit run sitting at a line edge, which accepted
# '90 samples were used.' against a source saying '20 samples were used.' A number at a line
# boundary may be content, or an ordinary PDF line break. So: decide whether THIS PAGE is
# line-numbered by looking at the whole page, and only then remove the numbering it actually
# has. An ambiguous figure is always preserved and therefore always verified.
_LEAD_NUM = re.compile(r"^[ \t]*(\d{1,5})(?=[ \t]|$)")
_TRAIL_NUM = re.compile(r"(?:^|[ \t])(\d{1,5})[ \t]*$")


def detect_line_numbering(raw):
    """Returns 'leading' | 'trailing' | None. A page is line-numbered only if most of its
    non-trivial lines carry an integer at the same edge AND those integers ascend in small
    steps — which content figures do not do."""
    lines = [l for l in (raw or "").splitlines() if l.strip()]
    # The edge modes below need line structure to look at; the inline mode does not, and must
    # not be skipped by this guard -- a page whose numbers landed mid-text is exactly a page
    # whose line structure the extraction lost, so it often arrives as one long line.
    if len(lines) < 8:
        return "inline" if _inline_run(raw) else None
    for where, rx in (("leading", _LEAD_NUM), ("trailing", _TRAIL_NUM)):
        nums, hits = [], 0
        for l in lines:
            m = rx.search(l)
            if m:
                hits += 1
                nums.append(int(m.group(1)))
        if hits < max(8, int(0.6 * len(lines))):
            continue
        asc = sum(1 for a, b in zip(nums, nums[1:]) if 0 < b - a <= 3)
        if asc >= 0.8 * (len(nums) - 1):
            return where
    return "inline" if _inline_run(raw) else None


# Defect 9 (production, 2026-09-15). The two modes above require the integer at a LINE EDGE.
# Some extractions put the line number in the middle of the flowing text instead --
# "this study reports on 17 an electrical energy management system ... at minimal 18 cost." --
# so neither regex fires, the page is never stripped, and every quote that crosses a numbered
# boundary comes back `interleaved`: the router correctly reports words in order with insertions
# and asks for human reading, on a sentence that is in fact contiguous and whole. On
# rayyan-472535585 that was 21 of 34 dossier quotes.
#
# The evidence used here is the one the docstring above already trusts -- a long run of integers
# ascending in small steps -- with the edge requirement dropped and two guards in its place:
# the run must be SPREAD through the prose (a table column has its numbers adjacent, a line
# numbering has ~8+ words between them), and only the token occurrences that form the run are
# removed, never every instance of those numbers elsewhere on the page.
_INT_TOKEN = re.compile(r"(?<!\S)(\d{1,4})(?!\S)")


def _inline_run(raw, min_len=8, min_gap=4):
    """Returns the list of (start, end) spans to drop, or [] when the page is not numbered."""
    if not raw:
        return []
    toks = [(m.start(1), m.end(1), int(m.group(1))) for m in _INT_TOKEN.finditer(raw)]
    if len(toks) < min_len:
        return []
    # The chain must tolerate INTERLOPERS. A numbered page also carries years, figure numbers
    # and a running header ("manuscript accepted ... 21"), and an earlier version reset the run
    # on any of them: on rayyan-472535585 page 22 the numbering 492-495 was there and visible,
    # broken into fragments shorter than the minimum, so the page went undetected and two good
    # quotes were still reported as interleaved. So: walk forward from each possible start,
    # taking the next value when it appears and SKIPPING anything that is not it. A skipped
    # token is never removed from the page -- only chain members are.
    best = []
    for i in range(len(toks)):
        chain, nxt = [toks[i]], toks[i][2] + 1
        for t in toks[i + 1:]:
            if t[2] == nxt:
                chain.append(t)
                nxt += 1
        if len(chain) > len(best):
            best = chain
        if len(best) > len(toks) - i:      # nothing further can beat it
            break
    if len(best) < min_len:
        return []
    # spread: the median word distance between consecutive members must look like prose lines,
    # not like a column of figures sitting next to each other.
    gaps = sorted(len(raw[a[1]:b[0]].split()) for a, b in zip(best, best[1:]))
    med = gaps[len(gaps) // 2]
    # A line holds a handful of words, not forty: the upper bound keeps a coincidental ascending
    # sequence scattered across a long page from passing as line numbering.
    if med < min_gap or med > 40:
        return []
    return [(a, b) for a, b, _ in best]

_NEG = {"not", "no", "never", "none", "neither", "nor", "without", "cannot", "cant",
        "dont", "doesnt", "didnt", "isnt", "arent", "wasnt", "werent", "wont", "unable",
        "fails", "failed", "lack", "lacks", "lacking", "absent", "excluded", "except"}

ABSENT = {"not reported", "not applicable", "not stated", "explicitly absent"}
# `none` was in this set, which FORBIDS a quote on it. But 'none' is a real answer a
# paper can state -- "no validation was performed", "the indicator is not normalised" --
# so forbidding the sentence was as wrong as demanding one. It lives in SILENCE_DERIVED
# below, where the quote is optional. Found by the satisfiability suite, which requires
# every legal value to be writable in the form its meaning implies.


def strip_line_numbers(raw, mode=None):
    """Rule 9. `mode` comes from detect_line_numbering() on the PAGE; when it is None nothing
    is removed, so every figure in the text stays verifiable."""
    if not raw or mode is None:
        return raw
    if mode == "inline":
        spans = _inline_run(raw)
        if not spans:
            return raw
        out, prev = [], 0
        for a, b in spans:
            out.append(raw[prev:a])
            prev = b
        out.append(raw[prev:])
        return "".join(out)
    rx = _LEAD_NUM if mode == "leading" else _TRAIL_NUM
    out = []
    for l in raw.splitlines():
        m = rx.search(l)
        out.append((l[:m.start(1)] + l[m.end(1):]) if m else l)
    return "\n".join(out)


# Frozen rule 3 in output/grounding.py joins ANY hyphen followed by a line break, so a page
# reading '20-\n30 %' normalises to '2030 %' and a quote saying '2030 %' was accepted while the
# literally correct '20-30 %' was not. grounding.py cannot be touched (its behaviour is in the
# provenance of the v2.2.1 corpus-wide check), so the break is closed HERE, before rule 3 sees
# it: between two digits the hyphen is a range, never word hyphenation.
_NUM_HYPHEN_BREAK = re.compile(r"(\d)[ \t]*-[ \t]*\n[ \t]*(?=\d)")

# Defect 6 (found in production, 2026-09-13, rayyan-472536226). Frozen rule 2 deletes the soft
# hyphen U+00AD BEFORE rule 3 joins a hyphenated line break, so a page reading 'ma\xad\nchine'
# loses the hyphen, keeps the newline, and rule 7 collapses it to 'ma chine' - a token that
# exists in no quote a reader can write. The page itself became unquotable: neither the faithful
# copy 'ma\xadchine' nor the repaired 'machine' can match it. A soft hyphen at a line break IS
# discretionary hyphenation by definition, so it is joined here, before rule 2 sees it.
_SOFT_HYPHEN_BREAK = re.compile("\u00ad[ \t]*\n[ \t]*")

# Defect 7 (found in production, 2026-09-13, rayyan-472536410). The mirror image: frozen rule 3
# joins ANY hyphen at a line break, so a URL wrapped as '.../1FbJGmVs-FNY0JE-\n7fgT...' loses a
# hyphen that is part of the address, and the quote that copies the address correctly cannot
# match. Same reasoning as the digit rule above: inside a URL the hyphen is an address
# character, never word hyphenation.
_URL_HYPHEN_BREAK = re.compile(r"(?:https?://|www\.)[^\s]*(?:-[ \t]*\n[ \t]*[^\s]*)+")
_URL_BREAK_INNER = re.compile(r"-[ \t]*\n[ \t]*")


def normalize_stage_c(s, beta_variant="fi", numbering_mode=None):
    """numbering_mode strips the page's detected line numbering. It is applied to the PAGE, and
    to the quote only on the last, review-only attempt of check_quote: stripping the quote is
    what let '1995 was adopted' match a page saying '1990 was adopted' on a numbered page, and
    '2013 10.4' match a year column whose 2013 row reads 6.2."""
    if s:
        s = _SOFT_HYPHEN_BREAK.sub("", s)
        s = _NUM_HYPHEN_BREAK.sub(r"\1-", s)
        s = _URL_HYPHEN_BREAK.sub(lambda m: _URL_BREAK_INNER.sub("-", m.group(0)), s)
    return normalize_text(strip_line_numbers(s, numbering_mode), beta_variant=beta_variant)


# A locator may be corrected only for a quote long enough that a unique string match means
# something. 40 characters is about one clause; below that a phrase recurs in a running header
# or a repeated caption and the "unique page" is an artefact of the corpus, not a location.
LOCATOR_MIN_CHARS = 40

_PUNCT = re.compile(r"^[^\w]+|[^\w]+$", re.U)


def _words(s):
    """Tokens for word-level comparison, with edge punctuation removed: 'range.' and 'range'
    are the same word. Without this the negation guard and the interleaving router both fall
    through to 'not found', which looks like a safe answer and is not — it hides the reason."""
    return [w for w in (_PUNCT.sub("", t) for t in s.split()) if w]


def _negation_preserved(quote_words, span_words):
    """Every negation token in the matched page span must also be in the quote."""
    qn = [w for w in quote_words if w in _NEG]
    sn = [w for w in span_words if w in _NEG]
    from collections import Counter
    cq, cs = Counter(qn), Counter(sn)
    return all(cq[t] >= n for t, n in cs.items())


def _subsequence_span(needle, hay, budget):
    """Rule 10 candidate span: needle's words in order within hay, bounded insertions.
    Returns (inserted, start, end) or None. Tries every start position for the first word."""
    best = None
    first = needle[0]
    starts = [j for j, w in enumerate(hay) if w == first]
    for s0 in starts:
        i, inserted, j = 0, 0, s0
        while j < len(hay) and i < len(needle):
            if hay[j] == needle[i]:
                i += 1
            else:
                inserted += 1
                if inserted > budget:
                    break
            j += 1
        if i == len(needle) and inserted <= budget:
            if best is None or inserted < best[0]:
                best = (inserted, s0, j)
    return best


# Defect 13 (production, 2026-09-16, rayyan-472536532). A sentence that runs across a page break
# also runs across the page furniture printed between the two halves. Where that furniture is a
# bare folio — "...facilitates the general application to  30  different processes." — joining the
# two pages puts the page number inside the sentence, and the boundary check reports `interleaved`
# on a sentence that is contiguous in the paper and whole in the quote. Only a STANDALONE integer
# at the very edge being joined is dropped, and only while the joined text is built for this
# check: nothing is removed from either page for any other purpose, and a number that is part of
# a sentence has neighbours and therefore survives.
def _furniture(pages, edge_lines=3, min_share=0.5):
    """Lines that sit at the top or bottom of MOST pages are running furniture, by evidence
    rather than by guess: a header repeats, a sentence does not. Used only at the page boundary,
    where the furniture printed between two halves of a sentence lands inside it —
    'MANUSCRIPT / ACCEPTED / ACCEPTED MANUSCRIPT' between '...application to' and 'different
    processes.' (rayyan-472536532), or a conference strapline (rayyan-472536644)."""
    from collections import Counter
    cnt, n = Counter(), 0
    for p in pages:
        lines = [l.strip() for l in (p.get("text") or "").splitlines() if l.strip()]
        if not lines:
            continue
        n += 1
        for l in lines[:edge_lines] + lines[-edge_lines:]:
            if len(l.split()) <= 12:
                cnt[l.lower()] += 1
    if n < 4:
        return set()
    need = max(3, int(min_share * n))
    return {l for l, c in cnt.items() if c >= need}


def _strip_furniture(text, fur):
    if not text or not fur:
        return text
    return "\n".join(l for l in text.splitlines() if l.strip().lower() not in fur)


_FOLIO_TAIL = re.compile(r"(?:\s|\n)+\d{1,4}\s*$")
_FOLIO_HEAD = re.compile(r"^\s*\d{1,4}(?:\s|\n)+")


def _drop_folio(text, edge):
    if not text:
        return text
    return (_FOLIO_TAIL.sub("\n", text) if edge == "tail" else _FOLIO_HEAD.sub("\n", text))


def check_quote(quote, page, pages):
    """G1 + G2. Only 'exact' is a pass. Never asserts anything about G3."""
    if not quote:
        return {"G1_exists": False, "G2_page": False, "acceptance": "no quote supplied"}
    target = next((p.get("text") or "" for p in pages if p.get("page") == page), None)

    def attempt(text):
        """Returns 'exact' | 'interleaved' | 'line-number ambiguity' | 'negation mismatch'
        | None, for one page.

        Three stages, and the order is the whole point:

          1. quote as written against the page as written. A data table is verified here
             whatever the numbering detector thinks of the page, so a misdetection can only
             cost a routing, never buy a false accept.
          2. quote as written against the page with its detected line numbering removed. This
             is the legitimate case: a quote spanning a line break with a line number inside.
          3. quote AND page stripped. This is NOT a pass. Stripping the quote deletes its own
             leading or trailing figure, and that figure is usually content — a year, a sample
             size. It is kept only as a routing class so a model that copied the line number
             along with the sentence is sent to a human instead of being silently failed."""
        mode = detect_line_numbering(text)
        for bv in ("fi", "fl"):
            nq_raw = normalize_stage_c(quote, bv, None)
            for nt in (normalize_stage_c(text, bv, None),
                       normalize_stage_c(text, bv, mode) if mode else None):
                if nt is None:
                    continue
                if nq_raw and nq_raw in nt:
                    return "exact", bv
            nt = normalize_stage_c(text, bv, mode)
            qw, hw = _words(nq_raw), _words(nt)
            if qw and len(qw) <= len(hw):
                sp = _subsequence_span(qw, hw, int(len(qw) * 0.8) + 4)
                if sp is not None:
                    _, s0, e0 = sp
                    if not _negation_preserved(qw, hw[s0:e0]):
                        return "negation mismatch", bv
                    return "interleaved", bv
            if mode:
                nq_str = normalize_stage_c(quote, bv, mode)
                if nq_str and nq_str != nq_raw and nq_str in nt:
                    return "line-number ambiguity", bv
        return None, None

    if target is not None:
        a, bv = attempt(target)
        if a == "exact":
            return {"G1_exists": True, "G2_page": True, "acceptance": "exact",
                    "beta_variant": bv}
        if a == "negation mismatch":
            return {"G1_exists": False, "G2_page": False,
                    "acceptance": "negation mismatch",
                    "note": "the page span the quote aligns to carries a negation the quote "
                            "does not. Treated as a content change, not a near-miss."}
        if a == "line-number ambiguity":
            # ROUTING ONLY. Not a pass. The quote's own edge figure was removed to make it
            # match, so the figure is unverified — which is exactly the case that must reach
            # a human rather than be counted.
            return {"G1_exists": False, "G2_page": True,
                    "acceptance": "line-number ambiguity", "review_candidate": True,
                    "beta_variant": bv,
                    "note": "the quote matches this page only if a figure at its own edge is "
                            "deleted as line numbering. That figure may be content — a year, "
                            "a sample size, a row label. Read the page."}
        if a == "interleaved":
            # ROUTING ONLY. Not a pass.
            return {"G1_exists": False, "G2_page": True, "acceptance": "interleaved",
                    "review_candidate": True, "beta_variant": bv,
                    "note": "words present in order with insertions — consistent with "
                            "two-column extraction, but also with a word-deletion that "
                            "changes meaning. Requires human reading."}
    # A sentence can END on the next page. The pilot quarantined rayyan-472536612 for a quote
    # the paper really contains: it begins at the foot of page 4 -- the page the surface cited,
    # exactly as the prompt requires -- and finishes on page 5, with a figure caption dropped in
    # at the break by the PDF extraction. Checking page by page, that verbatim sentence looks
    # fabricated. So the boundary is checked explicitly, in reading order, before anything is
    # called not found.
    idx = {p.get("page"): i for i, p in enumerate(pages)}
    if target is not None and page in idx:
        i = idx[page]
        fur = _furniture(pages)
        nxt = (pages[i + 1].get("text") or "") if i + 1 < len(pages) else None
        prv = (pages[i - 1].get("text") or "") if i > 0 else None
        for other, where, begins in ((nxt, "next", page), (prv, "previous", None)):
            if not other:
                continue
            a_side = _strip_furniture(target if where == "next" else other, fur)
            b_side = _strip_furniture(other if where == "next" else target, fur)
            joined = _drop_folio(a_side, "tail") + "\n" + _drop_folio(b_side, "head")
            a, bv = attempt(joined)
            if a == "exact":
                out = {"G1_exists": True, "G2_page": True, "acceptance": "exact",
                       "beta_variant": bv, "spans_page_break": True,
                       "note": f"the sentence runs across the boundary with the {where} page; "
                               f"the cited page is where it begins, which is what the prompt "
                               f"asks for"}
                if begins is None:
                    # it begins on the PREVIOUS page, so the locator is one page late
                    out.update({"G2_page": False, "acceptance": "locator corrected",
                                "review_candidate": True, "page_as_recorded": page,
                                "found_on_page": pages[i - 1].get("page"),
                                "note": "the sentence runs across the boundary and begins on "
                                        "the previous page; cite the page where it begins"})
                return out
            if a == "negation mismatch":
                # the boundary must not become a way round the guard
                return {"G1_exists": False, "G2_page": False,
                        "acceptance": "negation mismatch", "spans_page_break": True,
                        "note": "across the page boundary the span the quote aligns to carries "
                                "a negation the quote does not. A content change, not a "
                                "near-miss."}
            if a == "interleaved":
                return {"G1_exists": False, "G2_page": True, "acceptance": "interleaved",
                        "review_candidate": True, "beta_variant": bv, "spans_page_break": True,
                        "note": f"the words appear in order across the boundary with the "
                                f"{where} page, with insertions -- consistent with a figure "
                                f"caption or a running header dropped in at the page break. "
                                f"Requires human reading."}

    # G1 and G2 are separate checks and a wrong locator is not a fabrication: the sentence
    # exists verbatim, only its address is off. Measured on the pilot, this was the DOMINANT
    # failure: two of four papers failed on nothing else, always by exactly one page, in both
    # directions, clustered on figure-heavy pages. Blocking it spent three attempts and an
    # extraction on a record whose evidence was entirely genuine.
    #
    # So: when the quote is found EXACTLY on one and only one other page, the locator is
    # corrected, the recorded page is kept as page_as_recorded, and the cell is routed for
    # review and counted. Reviewer decision, 2026-09-12. Guards, because a correction is a
    # machine touching provenance: a unique match only -- a quote found on two pages is left
    # as a failure -- and a minimum length, since a short phrase can recur.
    found = [p.get("page") for p in pages
             if p.get("page") != page and attempt(p.get("text") or "")[0] == "exact"]
    if len(found) == 1 and len((quote or "").strip()) >= LOCATOR_MIN_CHARS:
        return {"G1_exists": True, "G2_page": False, "found_on_page": found[0],
                "acceptance": "locator corrected", "review_candidate": True,
                "page_as_recorded": page,
                "note": "the sentence exists verbatim on exactly one page and it is not the "
                        "page cited. G1 passes, G2 does not. The locator is corrected in the "
                        "record, the cited page is kept, and the cell is counted as corrected "
                        "-- never as exact."}
    if found:
        return {"G1_exists": True, "G2_page": False, "found_on_page": found[0],
                "acceptance": "wrong page",
                "note": ("the quote is found on several pages, so no single locator can be "
                         "established" if len(found) > 1 else
                         f"the quote is shorter than {LOCATOR_MIN_CHARS} characters; too short "
                         f"to locate by string match alone")}
    return {"G1_exists": False, "G2_page": False, "acceptance": "not found",
            "fuzzy_score": _score(quote, target or ""),
            "page_line_numbered": detect_line_numbering(target or "") is not None,
            "review_candidate": False}


def _score(quote, text):
    try:
        from rapidfuzz import fuzz
        nq, nt = normalize_stage_c(quote), normalize_stage_c(text)
        return round(fuzz.partial_ratio(nq, nt), 1) if nq and nt else None
    except ImportError:
        return None


# Values that can ONLY be reached by silence: no sentence says them, so a quote is forbidden
# and absence_basis is mandatory. `null` belongs here -- the schema uses it as the absence for
# every free-string field (country_region, n_observations), and treating it as a substantive
# value demanded a quote that cannot exist.
#
# SILENCE_DERIVED is different and was the pilot's second unsatisfiable error: these values can
# be reached EITHER from a statement or from the paper's silence. 'fixed, not mentioned' is the
# clearest case -- it literally means the paper does not mention re-estimation -- and the
# validator was rejecting it as "a substantive value with NO quote", an error no surface can
# satisfy. So: a quote is OPTIONAL here, and when there is none, absence_basis must say that
# silence is the basis. Forbidding the quote would be just as wrong, because a paper may state
# 'all variables were retained' and that sentence is evidence.
SILENCE_DERIVED = {"fixed, not mentioned", "no selection", "none", "none (absolute)",
                   "none reported"}


def _is_absence(val):
    if val is None:
        return True
    if isinstance(val, str):
        return val in ABSENT
    if isinstance(val, list):
        return bool(val) and all(isinstance(x, str) and x in ABSENT for x in val)
    return False


def _silence_ok(val):
    if isinstance(val, str):
        return val in SILENCE_DERIVED
    if isinstance(val, list):
        return bool(val) and all(isinstance(x, str) and x in SILENCE_DERIVED for x in val)
    return False


def walk_values(obj, prefix=""):
    if isinstance(obj, dict):
        if ("evidence_quote" in obj or "support_class" in obj) and (
                "value" in obj or "page" in obj or "support_class" in obj
                or "evidence_quote" in obj):
            yield prefix, obj
            return
        for k, v in obj.items():
            yield from walk_values(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_values(v, f"{prefix}[{i}]")


def check_record(rec, pages):
    out = {"key": rec.get("paper_key"), "surface": rec.get("surface"),
           "G1_G2": {"exact": 0, "wrong_page": 0, "not_found": 0, "interleaved": 0,
                     "negation_mismatch": 0, "absent_no_quote": 0, "locator_corrected": 0},
           "locator_corrections": [], "locator_corrected_persisted": 0,
           "G3_support_class": {"direct statement": 0, "requires inference": 0,
                               "absence checked": 0, "missing": 0},
           "failures": [], "review_candidates": [], "absence_without_basis": [],
           "invented_absence_quote": [], "value_without_evidence": [],
           "stated_absence_without_quote": []}
    for path, env in walk_values(rec):
        # A correction made on an EARLIER pass is already in the record, so this pass finds the
        # quote on the page and counts it exact: the pass-level counter then reads 0 and hides
        # how much correcting the rule actually did. The persisted flags are the durable truth
        # and are counted separately. Reporting only the pass-level number understated 24
        # corrections as 0 on the pilot.
        if env.get("locator_corrected"):
            out["locator_corrected_persisted"] += 1
        q, pg = env.get("evidence_quote"), env.get("page")
        has_value_key = "value" in env
        val = env.get("value")
        if "support_class" in env:            # every object that can carry one is counted
            sc = env.get("support_class")
            out["G3_support_class"][sc if sc in out["G3_support_class"] else "missing"] += 1

        # Not every enveloped object has a `value`: a C5 entry carries its answer in
        # data_origin / boundary_correspondence, and a metric in metric/value pairs. For those
        # the absence is declared by support_class, and absence_basis is still mandatory.
        absent = (_is_absence(val) if has_value_key
                  else env.get("support_class") == "absence checked")
        if absent:
            if not env.get("absence_basis"):
                out["absence_without_basis"].append(path)
            # a quote is allowed ONLY when the paper explicitly states the absence
            if q and env.get("absence_basis") != "explicitly stated absent":
                out["invented_absence_quote"].append({"path": path, "quote": q[:120]})
            if not q:
                # 'explicitly stated absent' asserts that a sentence says so. Then quote it.
                if env.get("absence_basis") == "explicitly stated absent":
                    out["stated_absence_without_quote"].append(path)
                out["G1_G2"]["absent_no_quote"] += 1
                continue

        if not q:
            if _silence_ok(val):
                # reached from the paper's silence: no quote, but say so
                if not env.get("absence_basis"):
                    out["absence_without_basis"].append(path)
                out["G1_G2"]["absent_no_quote"] += 1
                continue
            # a substantive value with no evidence is a FAILURE, not an absence
            out["value_without_evidence"].append({"path": path, "value": str(val)[:80]})
            continue

        r = check_quote(q, pg, pages)
        a = r["acceptance"]
        if a == "exact":
            out["G1_G2"]["exact"] += 1
            continue
        if a == "locator corrected":
            out["G1_G2"]["locator_corrected"] += 1
            env["page_as_recorded"] = r["page_as_recorded"]
            env["page"] = r["found_on_page"]
            env["locator_corrected"] = True
            out["locator_corrections"].append(
                {"path": path, "page_as_recorded": r["page_as_recorded"],
                 "page_verified": r["found_on_page"], "quote": q[:160]})
            out["review_candidates"].append({"path": path, "page": r["found_on_page"],
                                             "quote": q[:160], "reason": r["note"]})
            continue
        if a == "interleaved":
            out["G1_G2"]["interleaved"] += 1
            out["review_candidates"].append({"path": path, "page": pg, "quote": q[:160],
                                             "reason": r["note"]})
            out["failures"].append({"path": path, "page_cited": pg, "quote": q[:160],
                                    "acceptance": "interleaved — human reading required"})
            continue
        if a == "negation mismatch":
            out["G1_G2"]["negation_mismatch"] += 1
            out["failures"].append({"path": path, "page_cited": pg, "quote": q[:160],
                                    "acceptance": "negation mismatch", "note": r["note"]})
            continue
        if a == "wrong page":
            out["G1_G2"]["wrong_page"] += 1
            out["failures"].append({"path": path, "page_cited": pg,
                                    "found_on_page": r.get("found_on_page"), "quote": q[:160]})
            continue
        out["G1_G2"]["not_found"] += 1
        out["failures"].append({"path": path, "page_cited": pg, "quote": q[:160],
                                "fuzzy_score": r.get("fuzzy_score")})
    out["hard_failures"] = (len(out["failures"]) + len(out["absence_without_basis"])
                            + len(out["invented_absence_quote"])
                            + len(out["value_without_evidence"]))
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("record"); ap.add_argument("--bundle")
    a = ap.parse_args()
    rec = json.load(open(a.record, encoding="utf-8"))
    b = a.bundle or f"output/stage0/{rec['paper_key']}.json"
    pages = json.load(open(b, encoding="utf-8"))["pdf"]["pages"]
    print(json.dumps(check_record(rec, pages), indent=2, ensure_ascii=False))
