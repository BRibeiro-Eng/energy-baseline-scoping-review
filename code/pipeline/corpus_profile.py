#!/usr/bin/env python3
"""Corpus profile — the empirical basis for the synthesis-pillar taxonomy.

Rebuilds every figure quoted in PILLARS_PROPOSAL_2026-09-11.md from the
authoritative stores:

  roster  = concordant model values  UNION  reviewer-adjudicated Tier-1 forms
            (production/reviewer_workspace/reviews/membership/blind/<key>.json)

Level-A/B VALUES below are AI pre-fill (production/<model>/outputs/validated).
They are NOT adjudicated. Use them for scoping and design decisions only;
never as review results. Membership (Corpus A / Corpus B) IS adjudicated.

Usage:  python3 output/corpus_profile.py [--json out.json]
"""
import json, os, glob, csv, re, collections, argparse

ROOT = os.environ.get("L3_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load(model):
    return {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8"))
            for p in glob.glob(f"{ROOT}/production/{model}/outputs/validated/*.json")}

def _val(o):
    return o["value"] if isinstance(o, dict) and "value" in o else o

def _get(rec, stage, field):
    s = rec.get(stage)
    return _val(s.get(field)) if isinstance(s, dict) else None

def adjudicated():
    """Reviewer decisions from the Tier-1 membership forms (82 papers)."""
    bd = f"{ROOT}/production/reviewer_workspace/reviews/membership/blind"
    out = {}
    for p in glob.glob(bd + "/rayyan-*.json"):
        if any(p.endswith(s) for s in (".state.json", ".blind.json", ".ai.json")):
            continue
        d = json.load(open(p, encoding="utf-8"))
        out[d["key"]] = {"eligibility": d.get("eligibility") or {},
                         "reviewed": d.get("_review_fields") or [],
                         "done": bool(d.get("_done"))}
    return out

def rosters():
    C, G = _load("claude"), _load("chatgpt")
    adj = adjudicated()
    keys = sorted(set(C) & set(G))
    conc_a = {k for k in keys if _get(C[k], "stage1", "methodological_eligibility") is True
                             and _get(G[k], "stage1", "methodological_eligibility") is True}
    conc_b = {k for k in keys if _get(C[k], "stage1", "level_3b") is True
                             and _get(G[k], "stage1", "level_3b") is True}
    adj_a = {k for k, v in adj.items() if v["eligibility"].get("methodological_eligibility") is True}
    adj_b = {k for k, v in adj.items() if v["eligibility"].get("level_3b") is True}
    adj_a_f = {k for k, v in adj.items() if v["eligibility"].get("methodological_eligibility") is False}
    adj_b_f = {k for k, v in adj.items() if v["eligibility"].get("level_3b") is False}
    corpus_a = (conc_a | adj_a) - adj_a_f
    corpus_b_raw = (conc_b | adj_b) - adj_b_f
    corpus_b, resolved = enforce_b_subset_a(corpus_a, corpus_b_raw)
    return {"C": C, "G": G, "adj": adj, "keys": keys,
            "corpus_a": sorted(corpus_a),
            "corpus_b": sorted(corpus_b),
            "b_outside_a_resolved": sorted(resolved),
            "conc_a": sorted(conc_a), "conc_b": sorted(conc_b)}


# Corpus B is a charting partition INSIDE Corpus A (protocol §5.3): level_3b means nothing for a
# report that failed methodological eligibility. The Tier-1 form accepted the pair
# (level_3b=true, methodological_eligibility=false) for two reports; decision of 2026-09-17
# (stage_c/B_SUBSET_A_2026-09-17.md): the blind eligibility verdict stands and both leave B.
# Any OTHER report in B \ A is a new inconsistency and must stop the pipeline, not be dropped.
B_OUTSIDE_A_RESOLVED = {"rayyan-472535628", "rayyan-472535750"}


def enforce_b_subset_a(corpus_a, corpus_b, resolved=B_OUTSIDE_A_RESOLVED):
    outside = set(corpus_b) - set(corpus_a)
    unknown = outside - set(resolved)
    if unknown:
        raise AssertionError(f"Corpus B has reports outside Corpus A with no recorded decision: {sorted(unknown)}")
    return set(corpus_b) & set(corpus_a), outside

def dist(pool, src, stage, field, multi=False):
    c = collections.Counter()
    for k in pool:
        v = _get(src[k], stage, field)
        if v is None:
            c["<null>"] += 1
        elif multi and isinstance(v, list):
            if not v:
                c["<empty>"] += 1
            for x in v:
                c[str(x)] += 1
        else:
            c[str(v)] += 1
    return c

# §5.3 pre-specified main sector list, as surface strings
SECTOR_RX = {
    "refining":             r"refin|petroleum industry|crude",
    "petrochemicals":       r"petrochem|olefin|polymer|ethylene|propylene",
    "cement/lime":          r"cement|clinker|\blime\b",
    "pulp & paper":         r"pulp|paper mill|papermak",
    "steel/primary metals": r"\bsteel\b|smelt|alumini?um|primary metal|metallurg|foundr",
    "continuous chemicals": r"ammonia|sulfuric|methanol|fertili|chlor-alkali|nitric",
    "industrial gases":     r"industrial gas|air separation|hydrogen production|nitrogen production|\bLNG\b",
    "glass":                r"\bglass\b|float line",
}

def sector_string_candidates(R):
    """Detector (d), unregistered: A8 free text matches a §5.3 sector but the
    paper is outside Corpus B. Reported as a signal, not as a census detector."""
    C, G, B = R["C"], R["G"], set(R["corpus_b"])
    out = []
    for k in R["corpus_a"]:
        if k in B:
            continue
        txt = f"{_get(C[k],'stage2','sector_of_activity') or ''} | {_get(G[k],'stage2','sector_of_activity') or ''}"
        hit = [s for s, rx in SECTOR_RX.items() if re.search(rx, txt, re.I)]
        if hit:
            out.append({"key": k, "sectors": hit, "a8": txt.strip(),
                        "a9": _get(C[k], "stage2", "type_of_organisation")})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    R = rosters()
    C, A, B = R["C"], R["corpus_a"], R["corpus_b"]
    rep = {"corpus_a_n": len(A), "corpus_b_n": len(B),
           "concordant_a_n": len(R["conc_a"]), "concordant_b_n": len(R["conc_b"]),
           "size_branch": ("<=25" if len(B) <= 25 else "26-60" if len(B) <= 60 else ">60"),
           "blind_first_n": min(len(B), 40)}
    print(f"Corpus A = {len(A)}  (concordant {len(R['conc_a'])} + adjudicated)")
    print(f"Corpus B = {len(B)}  (concordant {len(R['conc_b'])} + adjudicated)")
    print(f"§3-Step-5 branch = {rep['size_branch']}   blind-first = {rep['blind_first_n']}"
          f"   AI-prefill+verify = {max(0, len(B)-40)}")

    for stage, field, multi in [("stage1", "paper_type", False),
                                ("stage2", "type_of_organisation", False),
                                ("stage2", "ems_standard", True),
                                ("stage2", "mv_protocol", True),
                                ("stage2", "regulatory_driver", True),
                                ("stage2", "enpi_enb_model_types", True),
                                ("stage2", "complementary_methodologies", True)]:
        d = dist(A, C, stage, field, multi)
        rep[field] = dict(d)
        print(f"\n## {field}  (Corpus A, n={len(A)}, AI pre-fill)")
        for k, v in d.most_common():
            print(f"   {v:4d}  {100*v/len(A):5.1f}%  {k}")

    for field, multi in [("scale_of_application", False), ("validation_types", True),
                         ("data_type", False), ("identifies_model_limitations", False),
                         ("specific_limitations", True), ("proposes_adaptations", False),
                         ("adaptation_types", True), ("normative_framing_of_adaptations", False),
                         ("empirical_refinery_application", False)]:
        d = dist(B, C, "stage3", field, multi)
        rep["B_" + field] = dict(d)
        print(f"\n## {field}  (Corpus B, n={len(B)}, AI pre-fill, claude surface)")
        for k, v in d.most_common():
            print(f"   {v:4d}  {k}")

    cands = sector_string_candidates(R)
    rep["sector_string_candidates"] = cands
    print(f"\n## detector (d) — §5.3 sector string outside Corpus B: {len(cands)}")
    for c in cands:
        print(f"   {c['key']}  [{','.join(c['sectors'])}]  {c['a8'][:70]}")

    if a.json:
        json.dump(rep, open(a.json, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print("\nwrote", a.json)

if __name__ == "__main__":
    main()
