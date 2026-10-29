"""fn_hunt.py — Validation Protocol C-2 step 4: false-negative candidate-union
CENSUS for Corpus B (supersedes the C-1.0 'detector 2 of capture-recapture' role;
capture-recapture is deleted in C-2 — REVIEW_ROUND2_C2.md).

Three detectors with different failure modes build a candidate list the human
EMPTIES (every candidate gets an accept/reject with quote + page):
  (a) model flags   — either model says level_3b=true / borderline / continuous-
                      process organisation (caller supplies these);
  (b) lexicon       — deterministic full-text scan below (canonical term list);
  (c) recall pass   — counter-anchored model pass (caller supplies flags).

Closure rule: any confirmed FN adds that paper's sector vocabulary to the lexicon
and re-runs detector (b); the census closes only when a full pass yields zero new
candidates. Over-inclusive by design; the goal is to never silently drop a genuine
continuous-process paper (the costliest SQ2-4 error).
"""
import re

# Canonical continuous-process lexicon (VALIDATION_PROTOCOL_C.md sec 3 step 4;
# PROTOCOL.md sec 12.5 mirrors this list). Multi-word for ambiguous sectors —
# never the bare word "paper".
CONTINUOUS_PROCESS_TERMS = [
    "refinery", "refining", "petrochemical", "petroleum",
    "cement", "clinker", "kiln",
    "pulp and paper", "paper mill",
    "steel", "blast furnace", "steelmaking",
    "ammonia", "ethylene", "olefin", "sulfuric acid", "sulphuric acid",
    "chlor-alkali", "industrial gases", "air separation",
    "glass furnace", "glass melting",
    "continuous process", "steady-state", "steady state",
]


def _compile(terms):
    # Longest-first so multiword terms win; word-boundary, case-insensitive.
    return [
        (t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE))
        for t in sorted(terms, key=len, reverse=True)
    ]


_PATTERNS = _compile(CONTINUOUS_PROCESS_TERMS)


def scan_text(text, patterns=None):
    """Return continuous-process terms present in `text` (canonical lower form,
    de-duplicated, in declaration order)."""
    if not text:
        return []
    found = []
    for term, pat in (patterns or _PATTERNS):
        if pat.search(text) and term not in found:
            found.append(term)
    return found


def hunt(items, extra_terms=None):
    """Detector (b). items: iterable of {key, level_3b, text}. Returns
    [{key, terms}] for records outside Corpus B (level_3b falsey) whose text hits
    >=1 term. extra_terms extends the lexicon (closure-loop expansions)."""
    patterns = _compile(CONTINUOUS_PROCESS_TERMS + list(extra_terms or []))
    out = []
    for it in items:
        if it.get("level_3b"):
            continue  # already Corpus B; not a false-negative candidate
        terms = scan_text(it.get("text", ""), patterns)
        if terms:
            out.append({"key": it["key"], "terms": terms})
    return out


def candidate_union(model_flagged, lexicon_hits, recall_flagged):
    """C-2 sec 3 step 4: union of the three detectors, per-key provenance.

    Each arg: iterable of keys (model_flagged/recall_flagged) or of {key, terms}
    dicts (lexicon_hits). Returns sorted [{key, detectors, terms}] — the census
    work-list the human must empty."""
    detectors = {}
    for k in model_flagged:
        detectors.setdefault(k, {"detectors": set(), "terms": []})["detectors"].add("model_flags")
    for hit in lexicon_hits:
        d = detectors.setdefault(hit["key"], {"detectors": set(), "terms": []})
        d["detectors"].add("lexicon")
        d["terms"] = hit["terms"]
    for k in recall_flagged:
        detectors.setdefault(k, {"detectors": set(), "terms": []})["detectors"].add("recall_pass")
    return [
        {"key": k, "detectors": sorted(v["detectors"]), "terms": v["terms"]}
        for k, v in sorted(detectors.items())
    ]


def closure_pass(items, reviewed_keys, extra_terms):
    """One closure iteration (C-2 sec 3 step 4): re-run detector (b) with the
    expanded lexicon; return only NEW candidates (not yet human-reviewed).
    The census closes when this returns []."""
    return [h for h in hunt(items, extra_terms) if h["key"] not in set(reviewed_keys)]
