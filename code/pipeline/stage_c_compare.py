#!/usr/bin/env python3
"""Stage C comparator — what a program can actually decide, and nothing more.

Deliberate limits, because the previous design overpromised:

  * NO semantic equivalence. The comparator never declares two differently-worded strings to
    be "the same referent". Free-text pairs that are not identical after normalisation are
    reported as `unresolved`, for a human.
  * NO "longest verbatim wins". Length does not establish correctness.
  * STRUCTURE FIRST. If the two surfaces decompose a paper into a different number of
    applications or models, nothing below that level is comparable and the paper is reported
    as `unresolved — different decomposition`. Comparing field by field across a mismatched
    decomposition is how a metric from one model ends up judged against another.
  * WHERE COUNTS MATCH, alignment is POSITIONAL and declared as such. It is an assumption,
    not a finding.
  * C3 IS THREE COMPARISONS, not one: which variables each surface found (presence), which
    ones pair up (correspondence), and whether the paired ones got the same type and role.
    Comparing only the type histogram would hide a variable one surface never saw.

Every output cell carries `provenance` and `verification_state`. Model agreement is
`provisional — model agreement only`; it is never `verified`.
"""
import json, os, glob, re, sys, argparse, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ABSENT = {"not reported", "not applicable", "explicitly absent"}


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def val(o):
    if isinstance(o, dict) and "value" in o:
        return o["value"]
    return o


def _sc(o):
    return o.get("support_class") if isinstance(o, dict) else None


def _ev(o):
    if not isinstance(o, dict):
        return (None, None)
    return (o.get("page"), norm(o.get("evidence_quote"))[:120] or None)


def cell(a, b, path):
    """Compare one envelope. Returns the verdict dict for the final dataset."""
    va, vb = val(a), val(b)
    if isinstance(va, list) and isinstance(vb, list):   # multi-select: order is not meaning
        va, vb = sorted(map(str, va)), sorted(map(str, vb))
    if va == vb:
        state = "provisional — model agreement only"
        if isinstance(va, str) and va in ABSENT:
            state = "provisional — both surfaces report an absence"
        out = {"path": path, "verdict": "agree", "value": va,
               "provenance": "both surfaces", "verification_state": state}
        # Same value, different support_class: one surface read it off the page and the other
        # inferred it. `requires inference` is what keeps a value out of a headline figure, so
        # a flip is substantive and was being reported as agreement.
        sa, sb = _sc(a), _sc(b)
        if sa != sb:
            out.update({"verdict": "differ", "reason": "support_class differs",
                        "claude": sa, "chatgpt": sb,
                        "provenance": "reviewer required",
                        "verification_state": "unresolved"})
            return out
        # Same value from different sentences on different pages: the coded value agrees, the
        # evidence does not, and V1 verification is defined on the evidence.
        ea, eb = _ev(a), _ev(b)
        if ea != eb and all(x != (None, None) for x in (ea, eb)):
            out["evidence_divergence"] = {"claude": {"page": ea[0], "quote": ea[1]},
                                          "chatgpt": {"page": eb[0], "quote": eb[1]}}
            out["verification_state"] = "unresolved — same value, different evidence"
        return out
    if isinstance(va, str) and isinstance(vb, str) and va in ABSENT and vb not in ABSENT:
        k = "presence/absence"
    elif isinstance(vb, str) and isinstance(va, str) and vb in ABSENT and va not in ABSENT:
        k = "presence/absence"
    elif isinstance(va, (str, int, float, bool)) and isinstance(vb, (str, int, float, bool)):
        k = "enum or scalar mismatch" if not (isinstance(va, str) and isinstance(vb, str)
                                             and len(va) > 60) else "free text — unresolved"
    else:
        k = "shape mismatch"
    return {"path": path, "verdict": "differ", "reason": k, "claude": va, "chatgpt": vb,
            "provenance": "reviewer required", "verification_state": "unresolved"}


# C8 metrics and C3/C5 items have their own comparisons; the generic walker must not visit
# them as well. Two passes over the same data produced a positional verdict beside the
# name-paired one, and the summary counted the positional one.
_OWN_COMPARISON = ("C8_metrics", "C3_variables", "C5_measurement")


def envelopes(obj, prefix=""):
    if isinstance(obj, dict):
        if "value" in obj and ("evidence_quote" in obj or "support_class" in obj):
            yield prefix, obj
            return
        for k, v in obj.items():
            if k in _OWN_COMPARISON:
                continue
            yield from envelopes(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from envelopes(v, f"{prefix}[{i}]")


def compare_measurement(ma, mb, path):
    """C5: the field the Sines case is read against. Previously never compared at all,
    because its items carry no `value` key and the envelope walker skipped them."""
    # A dict keyed by energy_vector silently discarded a second entry for the same vector --
    # precisely the case that matters here, where one surface records the site meter and the
    # other a calculated value for the same vector.
    key = lambda x: x["energy_vector"]
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for x in ma:
        ga[key(x)].append(x)
    for x in mb:
        gb[key(x)].append(x)
    dup = [{"energy_vector": k, "n_claude": len(ga[k]), "n_chatgpt": len(gb[k])}
           for k in sorted(set(ga) | set(gb)) if len(ga[k]) > 1 or len(gb[k]) > 1]
    ka = {k: v[0] for k, v in ga.items()}
    kb = {k: v[0] for k, v in gb.items()}
    paired = sorted(set(ka) & set(kb))
    origin_diff, boundary_diff = [], []
    for k in paired:
        if ka[k]["data_origin"] != kb[k]["data_origin"]:
            origin_diff.append({"energy_vector": k, "claude": ka[k]["data_origin"],
                                "chatgpt": kb[k]["data_origin"]})
        if ka[k]["boundary_correspondence"] != kb[k]["boundary_correspondence"]:
            boundary_diff.append({"energy_vector": k,
                                  "claude": ka[k]["boundary_correspondence"],
                                  "chatgpt": kb[k]["boundary_correspondence"]})
    only_a, only_b = sorted(set(ka)-set(kb)), sorted(set(kb)-set(ka))
    return {"path": path,
            "presence": {"only_claude": only_a, "only_chatgpt": only_b,
                         "paired": paired},
            "data_origin": {"disagreements": origin_diff},
            "boundary_correspondence": {"disagreements": boundary_diff},
            "repeated_vectors": dup,
            "support_class": {"disagreements":
                              [{"energy_vector": k, "claude": _sc(ka[k]), "chatgpt": _sc(kb[k])}
                               for k in paired if _sc(ka[k]) != _sc(kb[k])]},
            "verification_state": ("provisional — model agreement only"
                                  if not (only_a or only_b or origin_diff or boundary_diff
                                          or dup
                                          or any(_sc(ka[k]) != _sc(kb[k]) for k in paired))
                                  else "unresolved")}


def compare_metrics(block_a, block_b, path):
    """Metrics were aligned POSITIONALLY and compared on `value` alone, so R2=0.91 from one
    surface was judged against RMSE=2.4 from the other. Pair by metric name and unit."""
    # A paper may report R2 for three periods. Keying by (metric, unit) alone overwrote them
    # and a real discrepancy disappeared, so period_or_context is part of the key and repeated
    # occurrences are kept as lists. Where one key holds more than one occurrence on either
    # side, the pairing is ambiguous and is reported unresolved rather than guessed.
    def key(m):
        return (norm(m.get("metric")), norm(m.get("unit")), norm(m.get("period_or_context")))
    ka, kb = {}, {}
    for m in (block_a.get("metrics") or []):
        ka.setdefault(key(m), []).append(m)
    for m in (block_b.get("metrics") or []):
        kb.setdefault(key(m), []).append(m)
    paired = sorted(set(ka) & set(kb))
    vdiff, ambiguous = [], []
    for k in paired:
        if len(ka[k]) != 1 or len(kb[k]) != 1:
            ambiguous.append({"metric": ka[k][0].get("metric"),
                              "period_or_context": ka[k][0].get("period_or_context"),
                              "n_claude": len(ka[k]), "n_chatgpt": len(kb[k]),
                              "note": "same metric, unit and period reported more than once — "
                                      "pairing is ambiguous, not resolved here"})
            continue
        if str(ka[k][0].get("value")) != str(kb[k][0].get("value")):
            vdiff.append({"metric": ka[k][0].get("metric"), "unit": ka[k][0].get("unit"),
                          "period_or_context": ka[k][0].get("period_or_context"),
                          "claude": ka[k][0].get("value"), "chatgpt": kb[k][0].get("value")})
    only_a = [ka[k][0].get("metric") for k in sorted(set(ka)-set(kb))]
    only_b = [kb[k][0].get("metric") for k in sorted(set(kb)-set(ka))]
    st = cell(block_a.get("status"), block_b.get("status"), path + ".status")
    # Excluding C8 from the generic envelope walk also removed the asymmetric-presence check
    # for the block's OWN non-metric envelopes (validation_design). They are compared here, so
    # a field present on one surface only is still reported rather than silently dropped.
    others = []
    for k in sorted((set(block_a) | set(block_b)) - {"metrics", "status"}):
        ea, eb = block_a.get(k), block_b.get(k)
        if not (isinstance(ea, dict) or isinstance(eb, dict)):
            continue
        if isinstance(ea, dict) and isinstance(eb, dict):
            others.append(cell(ea, eb, f"{path}.{k}"))
        else:
            others.append({"path": f"{path}.{k}", "verdict": "differ",
                           "reason": "field present on one surface only",
                           "present_on": "claude" if isinstance(ea, dict) else "chatgpt",
                           "value": val(ea if isinstance(ea, dict) else eb),
                           "provenance": "reviewer required",
                           "verification_state": "unresolved"})
    return {"path": path, "status": st, "other_fields": others,
            "presence": {"only_claude": only_a, "only_chatgpt": only_b},
            "value_disagreements": vdiff, "ambiguous_pairings": ambiguous,
            "verification_state": ("provisional — model agreement only"
                                  if not (only_a or only_b or vdiff or ambiguous)
                                     and st["verdict"] == "agree"
                                     and all(c["verdict"] == "agree" for c in others)
                                  else "unresolved")}


def compare_variables(va, vb, path):
    """C3: presence, correspondence, then type and role on the pairs."""
    # Same defect as C5: a dict keyed by verbatim dropped a variable listed twice under two
    # roles (predictor and denominator), and then reported a count that was not the length of
    # the list it came from.
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for v in va:
        ga[norm(v["verbatim"])].append(v)
    for v in vb:
        gb[norm(v["verbatim"])].append(v)
    dup = [{"verbatim": k, "n_claude": len(ga[k]), "n_chatgpt": len(gb[k])}
           for k in sorted(set(ga) | set(gb)) if len(ga[k]) > 1 or len(gb[k]) > 1]
    ka = {k: v[0] for k, v in ga.items()}
    kb = {k: v[0] for k, v in gb.items()}
    paired = sorted(set(ka) & set(kb))
    only_a, only_b = sorted(set(ka) - set(kb)), sorted(set(kb) - set(ka))
    type_diff, role_diff = [], []
    for k in paired:
        if ka[k]["type"] != kb[k]["type"]:
            type_diff.append({"verbatim": ka[k]["verbatim"],
                              "claude": ka[k]["type"], "chatgpt": kb[k]["type"]})
        if ka[k]["role"] != kb[k]["role"]:
            role_diff.append({"verbatim": ka[k]["verbatim"],
                              "claude": ka[k]["role"], "chatgpt": kb[k]["role"]})
    return {"path": path, "repeated_verbatim": dup,
            "presence": {"n_claude": len(va), "n_chatgpt": len(vb),
                         "n_distinct_claude": len(ka), "n_distinct_chatgpt": len(kb),
                         "only_claude": [ka[k]["verbatim"] for k in only_a],
                         "only_chatgpt": [kb[k]["verbatim"] for k in only_b]},
            "correspondence": {"paired_exact": len(paired),
                               "unpaired": len(only_a) + len(only_b),
                               "note": "pairing is exact-after-normalisation only; unpaired "
                                       "variables are NOT assumed absent, they are unresolved"},
            "type_assignment": {"disagreements": type_diff},
            "role_assignment": {"disagreements": role_diff},
            "verification_state": ("provisional — model agreement only"
                                   if not (only_a or only_b or type_diff or role_diff or dup)
                                   else "unresolved")}


def _declared(rec, field):
    d = (rec.get("absence_declarations") or {}).get(field) or {}
    return d.get("searched") is True


def compare_set_declared(ra, rb, field, keyfn, label):
    """Two empty lists agree on nothing unless BOTH surfaces declare they searched."""
    r = compare_set(ra.get(field) or [], rb.get(field) or [], keyfn, label)
    da = (ra.get("absence_declarations") or {}).get(field) or {}
    db = (rb.get("absence_declarations") or {}).get(field) or {}
    if da.get("basis") != db.get("basis"):
        r["declaration_disagreement"] = {"claude": da.get("basis"), "chatgpt": db.get("basis")}
        r["verification_state"] = "unresolved — the two surfaces searched differently"
    if not (ra.get(field) or []) and not (rb.get(field) or []):
        if not (_declared(ra, field) and _declared(rb, field)):
            r["verification_state"] = "unresolved — absence not searched on both surfaces"
            r["note"] = ("both lists are empty but at least one surface did not declare a "
                         "search. An unsearched field is not a finding.")
    return r


def compare_set(a, b, keyfn, label):
    sa = collections.Counter(keyfn(x) for x in a)
    sb = collections.Counter(keyfn(x) for x in b)
    # Multiplicity is the finding, not noise: three occurrences of one cause->effect against
    # one occurrence is a disagreement about how many times the paper states it. The previous
    # version built these Counters and then compared set(sa) == set(sb), discarding them.
    mult = [{"key": k, "n_claude": sa[k], "n_chatgpt": sb[k]}
            for k in sorted(set(sa) | set(sb)) if sa[k] != sb[k] and sa[k] and sb[k]]
    return {"label": label, "only_claude": sorted(k for k in sa if k not in sb),
            "only_chatgpt": sorted(k for k in sb if k not in sa),
            "in_both": sorted(k for k in sa if k in sb),
            "count_disagreements": mult,
            "n_claude": sum(sa.values()), "n_chatgpt": sum(sb.values()),
            "verification_state": ("provisional — model agreement only"
                                   if sa == sb else "unresolved")}


def compare_paper(ca, cg):
    out = {"key": ca["paper_key"], "decomposition": {}, "cells": [], "variables": [],
           "measurement": [], "metrics": [],
           "mechanisms": None, "mechanisms_counting_subset": None, "adaptations": None,
           "study_limitations": None, "implementation_barriers": None, "reproducibility": []}
    aa, ab = ca["applications"], cg["applications"]
    out["decomposition"] = {"n_applications": {"claude": len(aa), "chatgpt": len(ab)},
                            "n_models": {"claude": sum(len(x["models"]) for x in aa),
                                         "chatgpt": sum(len(x["models"]) for x in ab)}}
    if len(aa) != len(ab):
        out["decomposition"]["verdict"] = "unresolved — different application decomposition"
    else:
        mism = [i for i, (x, y) in enumerate(zip(aa, ab)) if len(x["models"]) != len(y["models"])]
        out["decomposition"]["verdict"] = (
            "aligned positionally" if not mism
            else f"unresolved — different model count in application index {mism}")
        if not mism:
            out["decomposition"]["alignment"] = ("POSITIONAL, by order of appearance. This is an "
                                                 "assumption, not a finding.")
            for i, (x, y) in enumerate(zip(aa, ab)):
                ea_all = dict(envelopes(x, f"A{i+1}"))
                eb_all = dict(envelopes(y, f"A{i+1}"))
                for p in sorted(set(ea_all) | set(eb_all)):
                    if p in ea_all and p in eb_all:
                        out["cells"].append(cell(ea_all[p], eb_all[p], p))
                    else:
                        which = "claude" if p in ea_all else "chatgpt"
                        out["cells"].append({
                            "path": p, "verdict": "differ", "reason": "field present on one "
                            "surface only", "present_on": which,
                            "value": val(ea_all.get(p) or eb_all.get(p)),
                            "provenance": "reviewer required",
                            "verification_state": "unresolved"})
                for j, (mx, my) in enumerate(zip(x["models"], y["models"])):
                    out["variables"].append(
                        compare_variables(mx["C3_variables"], my["C3_variables"],
                                          f"A{i+1}.M{j+1}.C3_variables"))
                    out["measurement"].append(
                        compare_measurement(mx["C5_measurement"], my["C5_measurement"],
                                            f"A{i+1}.M{j+1}.C5_measurement"))
                    for blk in ("in_sample_fit", "out_of_sample_validation", "energy_result"):
                        mb = compare_metrics(mx["C8_metrics"][blk], my["C8_metrics"][blk],
                                             f"A{i+1}.M{j+1}.C8_metrics.{blk}")
                        out["metrics"].append(mb)
                        # C8 is out of the generic envelope walk, so its own envelope cells
                        # (status, validation_design) are registered here instead — otherwise
                        # they would leave the record-level cell list and the summary counts.
                        out["cells"].append(mb["status"])
                        out["cells"].extend(mb["other_fields"])
    mkey = lambda m: (f"{m['mechanism_cause']} -> {m['mechanism_effect_on_model']} "
                      f"| {m['claim_status']}")
    out["mechanisms"] = compare_set_declared(ca, cg, "mechanisms", mkey,
                                             "cause -> effect + claim_status")
    # the two axes compared separately: a paper may agree on the effect and differ on whether
    # a cause was named at all, which is itself the SQ2 finding
    out["mechanism_axes"] = {
        "cause": compare_set(ca["mechanisms"], cg["mechanisms"],
                             lambda m: m["mechanism_cause"], "cause axis"),
        "effect": compare_set(ca["mechanisms"], cg["mechanisms"],
                              lambda m: m["mechanism_effect_on_model"], "effect axis")}
    # A mechanism counts toward SQ2 only if it is NOT 'general' AND NOT inference-based.
    # The prompt, the design doc and the schema all say requires-inference values never enter
    # a headline figure; the previous filter dropped only 'general'.
    keep = lambda ms: [m for m in ms
                       if not m["claim_status"].startswith("general")
                       and m.get("support_class") != "requires inference"]
    out["mechanisms_counting_subset"] = compare_set(
        keep(ca["mechanisms"]), keep(cg["mechanisms"]),
        lambda m: f"{m['mechanism_cause']} -> {m['mechanism_effect_on_model']}",
        "mechanisms counting toward SQ2: claim_status not 'general' AND "
        "support_class not 'requires inference'")
    out["mechanisms_excluded_from_count"] = {
        "claude": [{"mechanism": mkey(m), "why": ("general" if
                    m["claim_status"].startswith("general") else "requires inference")}
                   for m in ca["mechanisms"] if m not in keep(ca["mechanisms"])],
        "chatgpt": [{"mechanism": mkey(m), "why": ("general" if
                     m["claim_status"].startswith("general") else "requires inference")}
                    for m in cg["mechanisms"] if m not in keep(cg["mechanisms"])]}
    # R6 rests on normative_framing and R8 on addresses_mechanism; neither was in the key, so
    # 'ISO 50001/50006 explicit' vs 'absent' on the same adaptation was reported as agreement.
    out["adaptations"] = compare_set_declared(
        ca, cg, "adaptations",
        lambda d: (f"{d['adaptation']} | {d['status']} | "
                   f"{d.get('normative_framing')} | links={d.get('addresses_mechanism')}"),
        "adaptation + status + normative_framing + addresses_mechanism")
    # also_constrains_model is the B5 defect in its new home: a study limitation the paper says
    # also constrains the model is a different finding from one that does not.
    out["study_limitations"] = compare_set_declared(
        ca, cg, "study_limitations",
        lambda s: f"{s['limitation']} | constrains_model={s.get('also_constrains_model')}",
        "study limitation + also_constrains_model")
    out["implementation_barriers"] = {
        "n_claude": len(ca["implementation_barriers"]),
        "n_chatgpt": len(cg["implementation_barriers"]),
        "verification_state": "unresolved — free text, never machine-paired"}
    for k in ("equations_given", "coefficients_given", "data_available", "code_available"):
        out["reproducibility"].append(cell(ca["C13_reproducibility"][k],
                                           cg["C13_reproducibility"][k], f"C13.{k}"))
    cells = out["cells"] + out["reproducibility"]
    out["unresolved_blocks"] = {
        "C3_variables": sum(1 for v in out["variables"]
                            if v["verification_state"] == "unresolved"),
        "C5_measurement": sum(1 for v in out["measurement"]
                              if v["verification_state"] == "unresolved"),
        "C8_metrics": sum(1 for v in out["metrics"]
                          if v["verification_state"] == "unresolved")}
    out["summary"] = {
        "cells_compared": len(cells),
        "agree": sum(1 for c in cells if c["verdict"] == "agree"),
        "differ": sum(1 for c in cells if c["verdict"] == "differ"),
        # A cell can agree on the value and still need a human: both surfaces recorded
        # 'specific energy consumption' from different sentences on different pages, and V1
        # verification is defined on the evidence, not on the label.
        "cells_unresolved": sum(1 for c in cells
                                if str(c.get("verification_state", "")).startswith("unresolved")),
        "by_reason": dict(collections.Counter(c.get("reason") for c in cells
                                              if c["verdict"] == "differ")),
        "unresolved_blocks": out["unresolved_blocks"],
        "note": "Counts describe the instrument, not correctness. No agreement coefficient is "
                "computed: AI-vs-AI consistency shares model biases and cannot certify a value.",
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="production/stage_c/compare")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ca_d, cg_d = "production/stage_c/claude/outputs", "production/stage_c/chatgpt/outputs"
    keys = sorted(set(os.path.basename(p)[:-5] for p in glob.glob(ca_d + "/rayyan-*.json")) &
                  set(os.path.basename(p)[:-5] for p in glob.glob(cg_d + "/rayyan-*.json")))
    if not keys:
        sys.exit("no paper has both surfaces yet")
    agg = collections.Counter()
    for k in keys:
        r = compare_paper(json.load(open(f"{ca_d}/{k}.json", encoding="utf-8")),
                          json.load(open(f"{cg_d}/{k}.json", encoding="utf-8")))
        json.dump(r, open(f"{a.out}/{k}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        agg["papers"] += 1
        agg["decomposition_unresolved"] += r["decomposition"]["verdict"].startswith("unresolved")
        agg["cells"] += r["summary"]["cells_compared"]
        agg["agree"] += r["summary"]["agree"]
        agg["differ"] += r["summary"]["differ"]
        agg["mech_unresolved"] += r["mechanisms"]["verification_state"] == "unresolved"
        print(f"{k}  {r['decomposition']['verdict'][:46]:46s} cells {r['summary']['agree']}/"
              f"{r['summary']['cells_compared']} agree  mech {r['mechanisms']['verification_state'][:12]}")
    print("\n" + json.dumps(dict(agg), indent=1))
    print("\nPer-field counts are in the per-paper files. Reported per field, never pooled.")


if __name__ == "__main__":
    main()
