#!/usr/bin/env python3
"""Comparator regression suite — the holes the review found, now asserted shut."""
import copy, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT + "/output")
from stage_c_compare import compare_paper  # noqa: E402

REC = json.load(open("stage_c/fixtures/record_valid.json", encoding="utf-8"))
fails = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + str(detail)[:170]) if not ok else ""))
    if not ok:
        fails.append(name)


a = copy.deepcopy(REC)
b = copy.deepcopy(REC)
r = compare_paper(a, b)
check("identical records: no divergence", r["summary"]["differ"] == 0, r["summary"])
check("C5 is actually compared", len(r["measurement"]) > 0, r.get("measurement"))
check("C8 metrics are actually compared", len(r["metrics"]) > 0, len(r["metrics"]))

# C5 divergence must be seen — it was invisible before
b = copy.deepcopy(REC)
b["applications"][0]["models"][0]["C5_measurement"][0]["boundary_correspondence"] = \
    "mismatch acknowledged"
r = compare_paper(a, b)
check("a C5 boundary disagreement is reported",
      any(m["boundary_correspondence"]["disagreements"] for m in r["measurement"]),
      r["measurement"][0] if r["measurement"] else None)

# metrics must pair by name, not by position
b = copy.deepcopy(REC)
blk = b["applications"][0]["models"][0]["C8_metrics"]["in_sample_fit"]["metrics"]
if len(blk) >= 2:
    blk.reverse()
    r = compare_paper(a, b)
    check("reordered metrics are NOT a divergence",
          all(not m["value_disagreements"] for m in r["metrics"]),
          [m["value_disagreements"] for m in r["metrics"] if m["value_disagreements"]])

# a multi-select array differing only in order is not a divergence
b = copy.deepcopy(REC)
ev = b["applications"][0]["models"][0]["C1_dependent_variable"]["energy_vector"]["value"]
if isinstance(ev, list) and len(ev) >= 2:
    ev.reverse()
    r = compare_paper(a, b)
    check("reordered multi-select is NOT a divergence",
          not any(c["path"].endswith("energy_vector") and c["verdict"] == "differ"
                  for c in r["cells"]),
          [c for c in r["cells"] if c["path"].endswith("energy_vector")])

# requires-inference mechanisms must not reach the SQ2 counting subset
b = copy.deepcopy(REC)
a2 = copy.deepcopy(REC)
a2["mechanisms"][0]["support_class"] = "requires inference"
r = compare_paper(a2, b)
sub = r["mechanisms_counting_subset"]
m0 = a2["mechanisms"][0]
k0 = f"{m0['mechanism_cause']} -> {m0['mechanism_effect_on_model']}"
check("an inference-based mechanism leaves the SQ2 counting subset",
      k0 not in sub["in_both"] and k0 in sub["only_chatgpt"], sub)
check("and it is reported as excluded, with the reason",
      any(x["why"] == "requires inference" for x in
          r["mechanisms_excluded_from_count"]["claude"]),
      r["mechanisms_excluded_from_count"])

# different decomposition: nothing below is compared
b = copy.deepcopy(REC)
b["applications"][0]["models"] = b["applications"][0]["models"][:1]
r = compare_paper(a, b)
check("different model count blocks field comparison",
      r["decomposition"]["verdict"].startswith("unresolved") and r["cells"] == []
      and r["measurement"] == [], r["decomposition"])

# a field present on one surface only must be reported, not dropped
b = copy.deepcopy(REC)
vd = b["applications"][0]["models"][0]["C8_metrics"]["out_of_sample_validation"]
vd.pop("validation_design", None)
r = compare_paper(a, b)
check("a field present on one surface only is reported",
      any(c.get("reason") == "field present on one surface only" for c in r["cells"]),
      [c for c in r["cells"] if c["verdict"] == "differ"][:2])

# ----------------------------------------- 2026-09-12 reproductions (reviewer)
# (2a) metrics were ALSO walked by the generic envelope pass, positionally. Swapping R2 and
#      RMSE produced two divergences in the summary while the C8 block declared agreement.
b = copy.deepcopy(REC)
b["applications"][0]["models"][0]["C8_metrics"]["in_sample_fit"]["metrics"].reverse()
r = compare_paper(a, b)
check("reordering metrics produces NO divergence anywhere in the summary",
      r["summary"]["differ"] == 0, r["summary"])
check("no metric envelope reaches the generic cell walk",
      not any(".metrics[" in c["path"] for c in r["cells"]),
      [c["path"] for c in r["cells"] if ".metrics[" in c["path"]][:3])

# (2b) keying by name+unit alone overwrote the same metric reported for different periods,
#      so a real discrepancy in one of them disappeared.
a3 = copy.deepcopy(REC)
b3 = copy.deepcopy(REC)
for rec_, v2 in ((a3, 0.88), (b3, 0.62)):
    blk = rec_["applications"][0]["models"][0]["C8_metrics"]["in_sample_fit"]["metrics"]
    blk[0]["period_or_context"] = "2019"
    blk.append({"metric": "R2", "value": v2, "unit": None, "period_or_context": "2020",
                "evidence_quote": blk[0]["evidence_quote"], "page": blk[0]["page"]})
r = compare_paper(a3, b3)
dis = [d for m in r["metrics"] for d in m["value_disagreements"]]
check("the same metric in two periods is kept apart and the differing one is caught",
      len(dis) == 1 and dis[0]["period_or_context"] == "2020", dis)

# same metric, unit AND period twice on one surface: the pairing is ambiguous, not guessed
a4 = copy.deepcopy(REC)
blk = a4["applications"][0]["models"][0]["C8_metrics"]["in_sample_fit"]["metrics"]
blk.append(copy.deepcopy(blk[0]))
r = compare_paper(a4, copy.deepcopy(REC))
check("a duplicate metric key is reported unresolved, not resolved by position",
      any(m["ambiguous_pairings"] for m in r["metrics"]),
      [m["ambiguous_pairings"] for m in r["metrics"]])

# (4) two empty lists are not agreement unless BOTH surfaces declare they searched
a5 = copy.deepcopy(REC); b5 = copy.deepcopy(REC)
for rec_ in (a5, b5):
    rec_["mechanisms"] = []
a5["absence_declarations"]["mechanisms"] = {"searched": False, "basis": None}
r = compare_paper(a5, b5)
check("an unsearched empty list does NOT agree",
      r["mechanisms"]["verification_state"].startswith("unresolved"), r["mechanisms"])
a5["absence_declarations"]["mechanisms"] = {"searched": True, "basis": "searched full text"}
r = compare_paper(a5, b5)
check("two DECLARED empty lists agree provisionally",
      r["mechanisms"]["verification_state"].startswith("provisional"), r["mechanisms"])

# ------------------------- 2026-09-12 adversarial audit (independent reviewer)
# Nine substantive disagreements were reported as agreement. Each one alone, from the fixture.
def differs(mutate, name):
    b = copy.deepcopy(REC)
    mutate(b)
    r = compare_paper(copy.deepcopy(REC), b)
    # implementation_barriers is hardcoded unresolved (free text, never machine-paired), so it
    # carries no signal and must not be allowed to make these assertions pass trivially.
    blocks = {k: v for k, v in r.items()
              if isinstance(v, dict) and "verification_state" in v
              and k != "implementation_barriers"}
    seen = (r["summary"]["differ"] > 0
            or r["summary"]["cells_unresolved"] > 0
            or any(str(v["verification_state"]).startswith("unresolved")
                   for v in blocks.values())
            or any(str(x.get("verification_state", "")).startswith("unresolved")
                   for key in ("variables", "measurement", "metrics") for x in r[key]))
    check(name, seen, {"differ": r["summary"]["differ"],
                       "states": {k: v["verification_state"] for k, v in blocks.items()}})


def M(r):
    return r["applications"][0]["models"][0]


differs(lambda b: b["mechanisms"].extend(
            [dict(b["mechanisms"][0], mechanism_id=i, evidence_quote=q)
             for i, q in (("X8", "The regression coefficients drift over the four"),
                          ("X9", "coefficients drift over the four years of record"))]),
        "B1 three occurrences against one is a disagreement, not agreement")
differs(lambda b: b["adaptations"][0].update({"normative_framing": "absent"}),
        "B2 a flipped normative_framing is seen (R6)")
differs(lambda b: b["adaptations"][0].update({"addresses_mechanism": None}),
        "B3 a dropped addresses_mechanism is seen (R8)")
differs(lambda b: b["study_limitations"][0].update({"also_constrains_model": False}),
        "B4 a flipped also_constrains_model is seen")
differs(lambda b: M(b)["C3_variables"].append(
            dict(M(b)["C3_variables"][0], role="denominator")),
        "B5 the same variable listed twice under two roles is seen")
differs(lambda b: M(b)["C5_measurement"].append(
            dict(M(b)["C5_measurement"][0], data_origin="calculated from process data",
                 boundary_correspondence="mismatch acknowledged")),
        "B6 a second C5 entry for the same vector is seen (R10)")
differs(lambda b: M(b)["C1_dependent_variable"]["quantity"].update(
            {"support_class": "requires inference"}),
        "B7 a support_class flip on an envelope is seen")
differs(lambda b: M(b)["C1_dependent_variable"]["quantity"].update(
            {"evidence_quote": "a crude distillation unit at a European refinery.", "page": 1}),
        "B8 the same value grounded in a different sentence is seen")
differs(lambda b: b["absence_declarations"]["mechanisms"].update({"basis": "section absent"}),
        "B9 a different search basis is seen (R3)")
differs(lambda b: M(b)["C5_measurement"][0].update({"support_class": "requires inference"}),
        "B10 a support_class flip on a C5 entry is seen")

# and the identical record must still be clean after all of that
r = compare_paper(copy.deepcopy(REC), copy.deepcopy(REC))
check("identical records are still clean after the audit fixes",
      r["summary"]["differ"] == 0 and r["summary"]["cells_unresolved"] == 0
      and not any(str(v["verification_state"]).startswith("unresolved")
                  for k, v in r.items() if isinstance(v, dict)
                  and "verification_state" in v and k != "implementation_barriers"),
      {k: v.get("verification_state") for k, v in r.items()
       if isinstance(v, dict) and "verification_state" in v})

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILURES: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
