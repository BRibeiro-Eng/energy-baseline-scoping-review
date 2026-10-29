"""grounding.py — Stage 4 evidence-grounding (PROTOCOL.md 12.2; Validation
Protocol C-2 corpus-wide grounding check).

Verifies an evidence_quote against the claimed PDF page via normalised fuzzy
substring match, with a length-sensitive threshold. Structural defence against
hallucinated quotes: match on claimed page -> confirmed; match elsewhere ->
page_unverified; no match anywhere -> not grounded (field invalidated upstream).

Implements the frozen v2.2.1 contract (PROTOCOL.md 6.3):

- the EIGHT ordered normalisation rules (control-character strip, soft-hyphen
  removal, line-break hyphenation join, ligature unification incl. the Greek
  beta symbol U+03D0, dash unification, quote unification, whitespace
  collapse, lowercase);
- the mandatory U+03D0 fi->fl fallback retry (rule 4: try 'fi'; if grounding
  fails, retry with 'fl'; whichever succeeds wins);
- non-contiguous evidence (6.3 v2.2): evidence_quote may be a LIST of
  substrings with `page` a positionally aligned LIST of ints; each substring
  is grounded against its own claimed page and the aggregate grounds only if
  every substring grounds;
- failure logging (6.3 future-proofing note): failures carry the normalised
  substring searched plus a bounded snippet of the normalised target-page
  text around the best fuzzy match, so systematic encoding artefacts surface
  as patterns (see collect_failure_patterns; >2 similar failures in a corpus
  warrant extending the normalisation spec).
"""
import re

from rapidfuzz import fuzz

GREEK_BETA = "ϐ"  # 'ϐ' — broken Symbol-font fallback for fi/fl ligatures

# Rule 1: U+0000-U+001F except LF (U+000A) and TAB (U+0009)
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f]")
# Rule 3: line-break hyphenation join ('vari-\n  ables' -> 'variables')
_HYPHEN_BREAK_RE = re.compile(r"-\s*\n\s*")
# Rule 7: whitespace collapse
_WS_RE = re.compile(r"\s+")

# Rules 4-6 are disjoint single-codepoint maps whose outputs are not inputs of
# one another, so a single str.translate pass is order-equivalent.
_BASE_MAP = {
    # rule 4: ligature unification (U+FB00-FB04)
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
    # rule 5: dash unification (U+2013 / U+2014 / U+2012 / U+2212)
    "–": "-", "—": "-", "‒": "-", "−": "-",
    # rule 6: quote unification — curly/typographic doubles
    "“": '"', "”": '"', "„": '"',
    # rule 6: curly/typographic singles + PDF artefacts ¶ (U+00B6), ¹ (U+00B9)
    "‘": "'", "’": "'", "‚": "'", "¶": "'", "¹": "'",
}
_TABLES = {
    "fi": str.maketrans({**_BASE_MAP, GREEK_BETA: "fi"}),
    "fl": str.maketrans({**_BASE_MAP, GREEK_BETA: "fl"}),
}

# 6.3 future-proofing note: artefact classes tracked for the >2-similar-
# failures extension trigger.
SUSPICIOUS_CLASSES = {
    "control_chars": _CONTROL_RE,
    "greek_beta_symbol": re.compile(GREEK_BETA),
    "ligatures": re.compile("[ﬀ-ﬄ]"),
    "pilcrow_superscript_one": re.compile("[¶¹]"),
    "curly_quotes": re.compile("[“”„‘’‚]"),
    "long_dashes": re.compile("[–—‒−]"),
}
EXTENSION_TRIGGER_THRESHOLD = 2  # >2 similar failures -> extend the 6.3 spec

_SNIPPET_WIDTH = 200


def normalize_text(s, beta_variant="fi"):
    """v2.2.1 normalisation (6.3), applied in protocol order:

    1. control-character strip (U+0000-U+001F except LF/TAB)
    2. soft-hyphen (U+00AD) removal
    3. line-break hyphenation join (regex '-\\s*\\n\\s*' -> '')
    4. ligature unification (U+FB00-FB04 -> ff/fi/fl/ffi/ffl; Greek beta
       symbol U+03D0 -> `beta_variant`, 'fi' by default)
    5. dash unification (U+2013/2014/2012/2212 -> '-')
    6. quote unification (curly quotes; ¶ U+00B6 / ¹ U+00B9 as apostrophes)
    7. whitespace collapse
    8. lowercase (+ strip)

    The fi-vs-fl choice for U+03D0 cannot be resolved in a single pass;
    ground_quote implements the mandatory fallback retry ('fi' first, then
    'fl' — whichever succeeds wins).
    """
    if not s:
        return ""
    s = _CONTROL_RE.sub("", s)                # 1
    s = s.replace("­", "")               # 2
    s = _HYPHEN_BREAK_RE.sub("", s)           # 3
    s = s.translate(_TABLES[beta_variant])    # 4-6
    s = _WS_RE.sub(" ", s)                    # 7
    return s.strip().lower()                  # 8


def _threshold(qlen):
    if qlen < 30:
        return 95
    if qlen <= 100:
        return 90
    return 85


def _snippet(text, alignment):
    """Bounded window of the normalised target-page text centred on the best
    fuzzy-match position (6.3 future-proofing note)."""
    if not text:
        return ""
    if alignment is None:
        return text[:_SNIPPET_WIDTH]
    center = (alignment.dest_start + alignment.dest_end) // 2
    start = max(0, center - _SNIPPET_WIDTH // 2)
    return text[start:start + _SNIPPET_WIDTH]


def _ground_variant(quote, page, pages, beta_variant):
    """One grounding pass under a fixed U+03D0 mapping ('fi' or 'fl')."""
    nq = normalize_text(quote, beta_variant)
    page_text = {p["page"]: normalize_text(p["text"], beta_variant)
                 for p in pages}

    if nq:
        thr = _threshold(len(nq))

        # 1. claimed page
        if page in page_text:
            sc = fuzz.partial_ratio(nq, page_text[page])
            if sc >= thr:
                return {"grounded": True, "locator": page,
                        "page_unverified": False, "score": sc,
                        "beta_variant": beta_variant}

        # 2. any other page
        best_pg, best_score = None, 0.0
        for pg, txt in page_text.items():
            sc = fuzz.partial_ratio(nq, txt)
            if sc > best_score:
                best_score, best_pg = sc, pg
        if best_score >= thr:
            return {"grounded": True, "locator": best_pg,
                    "page_unverified": True, "score": best_score,
                    "beta_variant": beta_variant}
    else:
        best_pg, best_score = None, 0.0

    # Not grounded: log enough context to surface systematic encoding
    # patterns (6.3 future-proofing note).
    ctx_pg = best_pg if best_pg is not None else page
    ctx_txt = page_text.get(ctx_pg, "")
    alignment = None
    if nq and ctx_txt:
        try:
            alignment = fuzz.partial_ratio_alignment(nq, ctx_txt)
        except Exception:
            alignment = None
    return {"grounded": False, "locator": None, "page_unverified": False,
            "score": best_score, "beta_variant": beta_variant,
            "failure_context": {
                "quote": quote,
                "normalized_quote": nq,
                "snippet_page": ctx_pg,
                "snippet": _snippet(ctx_txt, alignment),
                "score": best_score,
            }}


def _ground_single(quote, page, pages):
    """Scalar grounding with the mandatory U+03D0 fi->fl fallback retry."""
    result = _ground_variant(quote, page, pages, "fi")
    if result["grounded"]:
        return result
    # 6.3 rule 4: retry with the 'fl' substitution if 'fi' fails to ground.
    # The artefact can sit in the quote or in the extracted page text, so
    # both sides trigger the retry.
    if GREEK_BETA in (quote or "") or any(
            GREEK_BETA in (p.get("text") or "") for p in pages):
        retry = _ground_variant(quote, page, pages, "fl")
        if retry["grounded"] or retry["score"] > result["score"]:
            return retry
    return result


def _list_failure(msg):
    return {"grounded": False, "locator": None, "page_unverified": False,
            "score": 0.0, "non_contiguous": True, "substring_results": [],
            "error": msg}


def _ground_non_contiguous(quote, page, pages):
    """6.3 v2.2 non-contiguous evidence: each substring must ground against
    its own claimed page; the aggregate grounds only if all do."""
    if not isinstance(quote, (list, tuple)) or not isinstance(page, (list, tuple)):
        return _list_failure(
            "non-contiguous evidence requires BOTH evidence_quote and page "
            "to be lists (got %s / %s)"
            % (type(quote).__name__, type(page).__name__))
    if len(quote) != len(page):
        return _list_failure(
            "evidence_quote/page length mismatch: %d substring(s) vs %d "
            "page(s)" % (len(quote), len(page)))
    if not quote:
        return _list_failure("empty evidence_quote list")

    results = [_ground_single(q, p, pages) for q, p in zip(quote, page)]
    return {
        "grounded": all(r["grounded"] for r in results),
        "locator": [r["locator"] for r in results],
        "page_unverified": any(r["page_unverified"] for r in results),
        "score": min(r["score"] for r in results),
        "non_contiguous": True,
        "substring_results": results,
    }


def ground_quote(quote, page, pages):
    """Ground `quote` (claimed on `page`) against `pages` (list of {page, text}).

    Scalar form (6.3 common case): `quote` is a string, `page` an int.
    Non-contiguous form (6.3 v2.2): `quote` is a list of 2-3 substrings and
    `page` a positionally aligned list of ints; `evidence_quote[i]` is
    verified against `page[i]`.

    Returns {grounded, locator, page_unverified, score, ...}. Failures carry
    `failure_context` (normalised substring + bounded snippet of the
    normalised target-page text + score); non-contiguous results carry
    per-substring dicts under `substring_results`. Malformed list envelopes
    (length mismatch, list/scalar mix, empty list) return a clean failure
    dict with an `error` key — never an exception.
    """
    if isinstance(quote, (list, tuple)) or isinstance(page, (list, tuple)):
        return _ground_non_contiguous(quote, page, pages)
    return _ground_single(quote, page, pages)


def _failure_contexts(failure):
    ctxs = []
    if failure.get("failure_context"):
        ctxs.append(failure["failure_context"])
    for sub in failure.get("substring_results") or []:
        if sub.get("failure_context"):
            ctxs.append(sub["failure_context"])
    return ctxs


def collect_failure_patterns(failures):
    """Group grounding failures by suspicious-character class (6.3
    future-proofing note): any encoding artefact responsible for >2 failures
    in a corpus warrants extending the normalisation spec.

    `failures`: list of ground_quote() result dicts (grounded=False), scalar
    or non-contiguous. Scans the RAW quote (where pre-normalisation artefacts
    survive) plus the normalised target-page snippet of every failure context.

    Returns {"patterns": {class_name: [failure, ...]},
             "extension_candidates": [class_name, ...]} where
    extension_candidates lists the classes with more than
    EXTENSION_TRIGGER_THRESHOLD failures, sorted alphabetically.
    """
    patterns = {}
    for failure in failures or []:
        hit_classes = set()
        for ctx in _failure_contexts(failure):
            text = "%s %s" % (ctx.get("quote") or "", ctx.get("snippet") or "")
            for name, rx in SUSPICIOUS_CLASSES.items():
                if rx.search(text):
                    hit_classes.add(name)
        for name in hit_classes:
            patterns.setdefault(name, []).append(failure)
    return {
        "patterns": patterns,
        "extension_candidates": sorted(
            name for name, hits in patterns.items()
            if len(hits) > EXTENSION_TRIGGER_THRESHOLD),
    }
