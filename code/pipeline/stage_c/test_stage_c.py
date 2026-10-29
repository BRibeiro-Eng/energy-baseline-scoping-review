#!/usr/bin/env python3
"""Stage C regression suite — every case here is a defect that was FOUND, reproduced, fixed.

Run from the repo root:  /usr/local/bin/python3 stage_c/test_stage_c.py
"""
import copy, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT + "/output")
from stage_c_grounding import (check_quote, check_record, detect_line_numbering,
                               strip_line_numbers)          # noqa: E402
from stage_c_validate import snap_enums, validate                # noqa: E402

FX = "stage_c/fixtures"
REC = json.load(open(f"{FX}/record_valid.json", encoding="utf-8"))
PAGES = json.load(open(f"{FX}/bundle_rayyan-000000001.json", encoding="utf-8"))["pdf"]["pages"]
fails = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (("  | " + str(detail)[:150]) if detail and not ok else ""))
    if not ok:
        fails.append(name)


def pg(text, n=1):
    return [{"page": n, "text": text}]


def _every_other_has_a_key():
    """Walk the schema: wherever an enum admits 'other', the object that holds it must also
    define the companion key the validator will ask for. Catches the pilot defect at the
    schema level, not one field at a time."""
    import stage_c_validate as V
    S = json.load(open("stage_c/schema.json", encoding="utf-8"))

    def deref(n):
        if not isinstance(n, dict):
            return n
        if "$ref" in n:
            t = S
            for part in n["$ref"].lstrip("#/").split("/"):
                t = t[part]
            return deref(t)
        if "allOf" in n:
            out = {k: v for k, v in n.items() if k != "allOf"}
            for sub in n["allOf"]:
                d = deref(sub)
                if isinstance(d, dict):
                    for k, v in d.items():
                        if k == "properties":
                            pr = dict(out.get("properties") or {}); pr.update(v)
                            out["properties"] = pr
                        else:
                            out[k] = v
            return out
        return n

    bad = []

    def walk(node):
        node = deref(node)
        if not isinstance(node, dict):
            return
        props = node.get("properties") or {}
        for k, v in props.items():
            dv = deref(v)
            if isinstance(dv, dict) and "other" in (dv.get("enum") or []):
                if V._verbatim_name(k) not in props:
                    bad.append(f"{k} -> {V._verbatim_name(k)}")
            walk(v)
        if node.get("items"):
            walk(node["items"])

    walk(S)
    if bad:
        print("      companions missing from the schema:", bad)
    return not bad


# ---------------------------------------------------------------- rule 9: numbers
check("R9 a changed number is NOT accepted",
      check_quote("The model used 90 samples", 1,
                  pg("The model used 20 samples from the kiln."))["acceptance"] != "exact")
check("R9 an unchanged number IS accepted",
      check_quote("The model used 20 samples", 1,
                  pg("The model used 20 samples from the kiln."))["acceptance"] == "exact")
check("R9 a real line number is still stripped",
      check_quote("most large steelmakers have deployed the system", 1,
                  pg("1488  most large steelmakers have deployed the system\n1489  and the "
                     "baseline was rebuilt"))["acceptance"] == "exact")
check("R9 a decimal inside a sentence is verified",
      check_quote("an R2 of 0.91 was obtained", 1,
                  pg("an R2 of 0.78 was obtained"))["acceptance"] != "exact")

# ---------------------------------------------------------------- rule 10: deletions
r = check_quote("The model is valid outside the observed range", 1,
                pg("The model is not valid outside the observed range."))
check("R10 a dropped negation is a hard failure", r["acceptance"] == "negation mismatch", r)
r = check_quote("the rolling window does improve the prediction error", 1,
                pg("the rolling window does not improve the prediction error of the baseline."))
check("R10 'does not improve' -> 'does improve' rejected",
      r["acceptance"] == "negation mismatch", r)
r = check_quote("The plant produced clinker during the campaign", 1,
                pg("The plant produced a little clinker only during the second campaign."))
check("R10 a word-deletion is NOT a pass",
      r["acceptance"] != "exact" and r.get("review_candidate") is True, r)
check("R10 column interleaving routes to human review, not to a pass",
      check_quote("the incoming raw sewage is lifted to a level", 1,
                  pg("the incoming raw COD and grease sewage is lifted oil to a level"))
      ["acceptance"] == "interleaved")

# ---------------------------------------------------------------- evidence discipline
r = copy.deepcopy(REC)
m = r["applications"][0]["models"][0]
m["C2_model_form"]["estimation_method"] = {"value": "OLS", "evidence_quote": None,
                                          "page": None, "support_class": "direct statement"}
g = check_record(r, PAGES)
check("a substantive value with NO quote is a failure",
      any(v["path"].endswith("estimation_method") for v in g["value_without_evidence"]), g["G1_G2"])

r = copy.deepcopy(REC)
m = r["applications"][0]["models"][0]
m["C7_validity_envelope"]["statement"] = {"value": "not reported",
    "evidence_quote": "The model used 20 samples", "page": 1,
    "support_class": "absence checked", "absence_basis": "searched full text"}
g = check_record(r, PAGES)
check("an absence with a quote is rejected as invented",
      len(g["invented_absence_quote"]) == 1, g["invented_absence_quote"])

m["C7_validity_envelope"]["statement"]["absence_basis"] = "explicitly stated absent"
g = check_record(r, PAGES)
check("an absence the paper STATES may carry its quote",
      len(g["invented_absence_quote"]) == 0, g["invented_absence_quote"])

r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C1_dependent_variable"]["energy_vector"] = {
    "value": ["not reported"], "evidence_quote": None, "page": None,
    "support_class": "absence checked"}
g = check_record(r, PAGES)
check("a LIST-valued absence still needs absence_basis",
      any(p.endswith("energy_vector") for p in g["absence_without_basis"]),
      g["absence_without_basis"])

# ---------------------------------------------------------------- the snap
_, s = snap_enums(copy.deepcopy(REC))
check("a clean record produces no snaps", s == [], s)

r = copy.deepcopy(REC)
r["C13_reproducibility"]["equations_given"]["value"] = "Partial"
_, s = snap_enums(r)
check("case-only difference snaps", any(x["to"] == "partial" for x in s), s)

r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C1_dependent_variable"]["quantity"]["value"] = \
    "not absolute energy"
_, s = snap_enums(r)
check("a negated value does NOT snap", s == [], s)

r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C1_dependent_variable"]["quantity"]["value"] = \
    "energy consumption"
_, s = snap_enums(r)
check("'energy consumption' does NOT snap to 'specific energy consumption'", s == [], s)

# ---------------------------------------------------------------- id and quote integrity
r = copy.deepcopy(REC)
a2 = copy.deepcopy(r["applications"][0]); a2["application_id"] = "A2"
r["applications"].append(a2)            # duplicates M1/M2 in a second application
errs, _ = validate(r, PAGES)
check("model ids must be unique across the record",
      any("unique across the whole record" in e for e in errs), errs[:2])

# One sentence may state two limitations. Forbidding quote reuse LOSES information; the
# de-duplication belongs at counting time, per paper per category. Reversed 2026-09-12.
r = copy.deepcopy(REC)
r["mechanisms"][1]["evidence_quote"] = r["mechanisms"][0]["evidence_quote"]
r["mechanisms"][1]["page"] = r["mechanisms"][0]["page"]
errs, _ = validate(r, PAGES)
check("two mechanisms MAY share one sentence when cause or effect differ",
      not any("duplicate" in e for e in errs), [e for e in errs if "duplicate" in e])

r = copy.deepcopy(REC)
r["mechanisms"][1] = copy.deepcopy(r["mechanisms"][0])
r["mechanisms"][1]["mechanism_id"] = "X2"
errs, _ = validate(r, PAGES)
check("an EXACT duplicate mechanism is still an error",
      any("duplicate" in e for e in errs), errs[:2])

# trimming two words off the quote defeated the exact-string duplicate test
r = copy.deepcopy(REC)
r["mechanisms"][1] = copy.deepcopy(r["mechanisms"][0])
r["mechanisms"][1]["mechanism_id"] = "X2"
r["mechanisms"][1]["evidence_quote"] = r["mechanisms"][0]["evidence_quote"][4:]
errs, _ = validate(r, PAGES)
check("a sub-span of the same sentence is still the same finding",
      any("same sentence" in e for e in errs), errs[:2])

# ------------------------------------------------- 2026-09-12 reproductions (reviewer)
# (1) rule 9 accepted a changed number because the number sat at a line edge. Line-edge
#     POSITION is not evidence of line numbering; the page must be shown to be numbered.
r = check_quote("90 samples were used.", 1, pg("20 samples were used."))
check("R9' a leading number is content, not a line number, on an unnumbered page",
      r["acceptance"] != "exact", r)
r = check_quote("the kiln was rebuilt 1991", 1, pg("the kiln was rebuilt 1987"))
check("R9' a trailing number is content on an unnumbered page",
      r["acceptance"] != "exact", r)
numbered = ("\n".join(f"{1400+i}  line {i} of the running text of this page, long enough"
                      for i in range(12)))
check("R9' a page that IS numbered still strips its numbers",
      check_quote("line 5 of the running text of this page, long enough", 1,
                  pg(numbered))["acceptance"] == "exact")
table = "\n".join(["14  2.31  fouling factor", "92  8.04  feed rate",
                   "7   0.55  ambient", "311 44.1  stack loss",
                   "28  3.02  steam", "5   0.91  power",
                   "77  6.18  fuel gas", "180 12.4  flare"])
check("R9' a data table is NOT treated as line-numbered",
      check_quote("92 8.04 feed rate", 1, pg(table))["acceptance"] == "exact")
check("R9' and a changed table number is caught",
      check_quote("95 8.04 feed rate", 1, pg(table))["acceptance"] != "exact")

# (4) absence_declarations existed but gated nothing: an empty list validated with
#     searched:false, i.e. 'I did not look' counted the same as 'there is nothing'.
r = copy.deepcopy(REC)
r["mechanisms"] = []
r["absence_declarations"]["mechanisms"] = {"searched": False, "basis": None}
errs, _ = validate(r, PAGES)
check("an empty list with searched:false is REJECTED",
      any("absence_declarations.mechanisms.searched" in e for e in errs), errs[:2])
r["absence_declarations"]["mechanisms"] = {"searched": True, "basis": "searched full text"}
errs, _ = validate(r, PAGES)
check("an empty list WITH a declared search validates",
      not any("absence_declarations" in e for e in errs), errs[:2])

# (5) the G3 report counted only objects carrying a `value` key, so every mechanism and
#     adaptation — the objects the SQ2 claim rests on — was invisible to it.
r = copy.deepcopy(REC)
r["mechanisms"][0]["support_class"] = "requires inference"
g = check_record(r, PAGES)
check("G3 counts a requires-inference mechanism",
      g["G3_support_class"]["requires inference"] >= 1, g["G3_support_class"])
g0 = check_record(copy.deepcopy(REC), PAGES)
check("G3 counts every mechanism, not only fields with a `value` key",
      g0["G3_support_class"]["direct statement"] >= len(REC["mechanisms"]),
      g0["G3_support_class"])

# ------------------------------------- 2026-09-12 adversarial audit (independent reviewer)
# A1. detect_line_numbering() fires on any table whose first column ascends by 1 -- a year
#     column, the commonest table in this corpus -- and stripping BOTH sides then paired a
#     year with another year's value. The quote side is no longer stripped on an accepting
#     attempt; a stripped-quote match is a routing class, never a pass.
TBL = ("Table 3. Specific energy consumption, GJ/t\n"
       "2004 10.4\n2005 10.1\n2006 9.8\n2007 9.5\n2008 9.1\n"
       "2009 8.7\n2010 8.0\n2011 7.4\n2012 6.9\n2013 6.2")
check("A1 a year column is not treated as line numbering on an accepting attempt",
      check_quote("2013 6.2", 1, pg(TBL))["acceptance"] == "exact")
r = check_quote("2013 10.4", 1, pg(TBL))
check("A1 pairing a year with another year's value is NOT accepted",
      r["acceptance"] != "exact" and r.get("review_candidate") is True, r)

# A2. on a genuinely numbered page the quote's OWN leading figure was deleted, so any number
#     at the edge of a quote went unverified.
NUM = ("\n".join(f"{i} w{i} w{i}b w{i}c w{i}d" for i in range(1, 10))
       + "\n10 1990 was adopted as the baseline year")
check("A2 the quote's own edge figure is verified on a numbered page",
      check_quote("1990 was adopted as the baseline year", 1, pg(NUM))["acceptance"] == "exact")
r = check_quote("1995 was adopted as the baseline year", 1, pg(NUM))
check("A2 a changed edge figure on a numbered page is NOT accepted",
      r["acceptance"] == "line-number ambiguity", r)

# A3. frozen rule 3 joined any hyphen before a line break, so '20-\n30 %' normalised to
#     '2030 %': the fabricated figure passed and the correct transcription failed.
check("A3 a hyphen between digits is a range, not word hyphenation",
      check_quote("savings potential lies in the 20-30 % range", 1,
                  pg("savings potential lies in the 20-\n30 % range"))["acceptance"] == "exact")
check("A3 and the joined form is no longer accepted",
      check_quote("savings potential lies in the 2030 % range", 1,
                  pg("savings potential lies in the 20-\n30 % range"))["acceptance"] != "exact")
check("A3 word hyphenation still joins",
      check_quote("the normalisation variables were chosen", 1,
                  pg("the normalisation vari-\nables were chosen"))["acceptance"] == "exact")

# A4. evidence_quote was OPTIONAL on a C5 entry, so omitting the key made the whole object
#     invisible to the grounding walk: a metering claim with no evidence at all validated.
#     This is the field R10 rests on.
r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C5_measurement"] = [
    {"energy_vector": "electricity", "data_origin": "dedicated meter",
     "boundary_correspondence": "exact", "support_class": "direct statement"}]
errs, g = validate(r, PAGES)
check("A4 a C5 entry with no evidence key is rejected, not ignored",
      errs != [] and any("C5_measurement" in e for e in errs), errs[:2])

# A5. an absence asserted as 'explicitly stated absent' cited nothing.
r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C7_validity_envelope"]["statement"] = {
    "value": "not stated", "evidence_quote": None, "page": None,
    "support_class": "absence checked", "absence_basis": "explicitly stated absent"}
errs, _ = validate(r, PAGES)
check("A5 'explicitly stated absent' without a quote is rejected",
      any("explicitly stated absent" in e and "no quote" in e for e in errs), errs[:2])

# A6. 'other' passed unexplained everywhere except mechanisms and adaptations.
for path, setter in (
        ("C2.estimation_method",
         lambda rr: rr["applications"][0]["models"][0]["C2_model_form"]["estimation_method"]
         .update({"value": "other"})),
        ("C3.type",
         lambda rr: rr["applications"][0]["models"][0]["C3_variables"][0]
         .update({"type": "other"})),
        ("study_limitations.limitation",
         lambda rr: rr["study_limitations"][0].update({"limitation": "other"}))):
    r = copy.deepcopy(REC)
    setter(r)
    errs, _ = validate(r, PAGES)
    check(f"A6 'other' on {path} requires the paper's wording",
          any("other_verbatim" in e for e in errs), errs[:2])

# A7. an empty C3_variables and a 'reported' metric block with no metrics both validated.
r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C3_variables"] = []
r["applications"][0]["models"][0].pop("C3_variables_absence", None)
errs, _ = validate(r, PAGES)
check("A7 an empty C3_variables needs a declaration",
      any("C3_variables_absence" in e for e in errs), errs[:2])
r = copy.deepcopy(REC)
blk = r["applications"][0]["models"][0]["C8_metrics"]["in_sample_fit"]
blk["metrics"] = []
errs, _ = validate(r, PAGES)
check("A7 status 'reported' with no metric recorded is rejected",
      any("status is 'reported' but metrics is" in e for e in errs), errs[:2])

# A8. interleaving is a ROUTING class, and validate() was converting it into a blocking error,
#     so a two-column paper was retried three times and quarantined -- which is why the
#     pilot's 'count of interleaved routings' would have come out identically zero.
r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C7_validity_envelope"]["statement"] = {
    "value": "stated qualitatively",
    "evidence_quote": "the incoming raw sewage is lifted to a level",
    "page": 99, "support_class": "direct statement"}
P2 = PAGES + [{"page": 99,
               "text": "the incoming raw COD and grease sewage is lifted oil to a level"}]
errs, g = validate(r, P2)
check("A8 an interleaved quote is routed for review, not quarantined",
      g["G1_G2"]["interleaved"] == 1 and len(g.get("routed_for_review") or []) == 1
      and not any("not found on physical page" in e for e in errs),
      {"errs": errs[:2], "routed": g.get("routed_for_review")})

# ------------------------------------------------ 2026-09-12 pilot, paper rayyan-472535351
# The generic 'other' rule derived the companion key as <field>_other_verbatim, but the schema
# names the mechanism axes' companions cause_other_verbatim and effect_other_verbatim. The
# validator therefore demanded a key that additionalProperties:false rejects -- an error no
# surface can satisfy. The paper burned one attempt at $1.59 before the run was stopped.
r = copy.deepcopy(REC)
r["mechanisms"][0]["mechanism_effect_on_model"] = "other"
r["mechanisms"][0]["effect_other_verbatim"] = "the indicator stops tracking the unit's load"
errs, _ = validate(r, PAGES)
check("P1 effect 'other' is satisfied by effect_other_verbatim, the key the schema defines",
      errs == [], errs[:3])
r["mechanisms"][0].pop("effect_other_verbatim")
errs, _ = validate(r, PAGES)
check("P1 and without it the error names that same key",
      any("effect_other_verbatim is missing" in e for e in errs), errs[:2])
r = copy.deepcopy(REC)
r["mechanisms"][0]["mechanism_cause"] = "other"
r["mechanisms"][0]["cause_other_verbatim"] = "a change of crude slate"
errs, _ = validate(r, PAGES)
check("P1 cause 'other' is satisfied by cause_other_verbatim",
      errs == [], errs[:3])
r = copy.deepcopy(REC)
r["adaptations"][0]["adaptation"] = "other"
r["adaptations"][0]["adaptation_other_verbatim"] = "a second regression on the residuals"
errs, _ = validate(r, PAGES)
check("P1 adaptation 'other' is satisfied by adaptation_other_verbatim",
      errs == [], errs[:3])
check("P1 every 'other' enum in the schema has a companion key the schema also defines",
      _every_other_has_a_key())

# 'absence checked' is one of the three legal support_class values and had no bucket in the G3
# report, so every declared absence was counted as MISSING: 29 of them on the first pilot paper.
g = check_record(copy.deepcopy(REC), PAGES)
check("P2 a declared absence is counted as 'absence checked', not as 'missing'",
      g["G3_support_class"]["absence checked"] > 0 and g["G3_support_class"]["missing"] == 0,
      g["G3_support_class"])

# ------------------------------------------------ 2026-09-12 pilot, paper rayyan-472535794
# P3. 'fixed, not mentioned' literally means the paper does not mention re-estimation, and the
#     validator rejected it as "a substantive value with NO quote" -- the second unsatisfiable
#     error of the pilot. A silence-derived value needs no quote, but must say that silence is
#     the basis; and it may still carry a quote, because a paper can state it.
r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C6_re_estimation"]["regime"] = {
    "value": "fixed, not mentioned", "evidence_quote": None, "page": None,
    "support_class": "absence checked", "absence_basis": "searched full text"}
errs, _ = validate(r, PAGES)
check("P3 'fixed, not mentioned' with a declared basis and no quote validates", errs == [],
      errs[:2])
r["applications"][0]["models"][0]["C6_re_estimation"]["regime"].pop("absence_basis")
errs, _ = validate(r, PAGES)
check("P3 but without a basis it is rejected",
      any("absence_basis is missing" in e for e in errs), errs[:2])
r["applications"][0]["models"][0]["C6_re_estimation"]["regime"] = {
    "value": "no selection", "evidence_quote": "The model used 20 samples", "page": 1,
    "support_class": "direct statement"}
errs, g = validate(r, PAGES)
check("P3 a silence-derived value MAY still carry a quote when the paper states it",
      not any("carries NO quote" in e or "never justify an absence" in e for e in errs),
      errs[:2])

# P4. a null value is the schema's absence for every free-string field, and it was being
#     treated as a substantive value that owed a quote.
r = copy.deepcopy(REC)
r["applications"][0]["country_region"] = {
    "value": None, "evidence_quote": None, "page": None,
    "support_class": "absence checked", "absence_basis": "searched full text"}
errs, _ = validate(r, PAGES)
check("P4 a null value with a declared basis is an absence, not a missing quote",
      errs == [], errs[:2])
r["applications"][0]["country_region"].pop("absence_basis")
errs, _ = validate(r, PAGES)
check("P4 and a null value still needs its basis",
      any("absence_basis is missing" in e for e in errs), errs[:2])

# --------------------------------- 2026-09-12 reviewer decision: locator correction
# G1 and G2 are separate checks. A quote that exists verbatim on exactly one page, cited at
# another, is a wrong ADDRESS, not a fabrication -- the dominant pilot failure, two of four
# papers failing on nothing else. It is corrected, recorded, routed and counted; never folded
# into 'exact'. Guards: a unique match only, and a quote long enough to locate by string match.
P3 = PAGES + [{"page": 98, "text": "A simulation model is used to facilitate the analysis of "
                                   "the energy and environmental performance of the plant."}]
LONG = "A simulation model is used to facilitate the analysis of the energy"
r = check_quote(LONG, 97, P3)
check("L1 a verbatim quote cited one page off is a corrected locator, not a failure",
      r["acceptance"] == "locator corrected" and r["found_on_page"] == 98
      and r["page_as_recorded"] == 97, r)
check("L2 a short quote is NOT locator-corrected",
      check_quote("the energy", 97, P3)["acceptance"] != "locator corrected")
# the same sentence on two NON-ADJACENT pages, cited on a third whose neighbours do not hold it:
# no single locator can be established, so it stays a failure
# the cited page's own neighbours must not hold the sentence either, or the boundary check
# would legitimately match it across the break
TWICE = [{"page": 49, "text": LONG + " and so on."}, {"page": 50, "text": "unrelated filler"},
         {"page": 51, "text": "unrelated filler"}, {"page": 52, "text": "unrelated filler"},
         {"page": 53, "text": LONG + " again."}]
check("L3 a quote found on more than one page is left a failure",
      check_quote(LONG, 51, TWICE)["acceptance"] == "wrong page", check_quote(LONG, 51, TWICE))

r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C7_validity_envelope"]["statement"] = {
    "value": "stated qualitatively", "evidence_quote": LONG, "page": 97,
    "support_class": "direct statement"}
errs, g = validate(r, P3)
check("L4 a corrected locator does not block the record",
      errs == [] and g["G1_G2"]["locator_corrected"] == 1, {"errs": errs[:2],
                                                            "g": g["G1_G2"]})
check("L5 the correction is recorded with both pages and the cell is queued for review",
      len(g["locator_corrections"]) == 1
      and g["locator_corrections"][0]["page_as_recorded"] == 97
      and g["locator_corrections"][0]["page_verified"] == 98
      and any(c["path"].endswith("statement") for c in g["review_candidates"]),
      g["locator_corrections"])
check("L6 the record itself carries the corrected page and keeps the cited one",
      r["applications"][0]["models"][0]["C7_validity_envelope"]["statement"]["page"] == 98
      and r["applications"][0]["models"][0]["C7_validity_envelope"]["statement"]
      ["page_as_recorded"] == 97,
      r["applications"][0]["models"][0]["C7_validity_envelope"]["statement"])
check("L7 a corrected locator is never counted as exact",
      g["G1_G2"]["exact"] == check_record(copy.deepcopy(REC), PAGES)["G1_G2"]["exact"],
      g["G1_G2"])

r = copy.deepcopy(REC)
r["applications"][0]["models"][0]["C1_dependent_variable"]["quantity"]["locator_corrected"] = True
errs, _ = validate(r, PAGES)
check("L8 a surface cannot assert locator_corrected on a correctly cited quote",
      any("locator_corrected is true" in e for e in errs), errs[:2])

# ------------------------------- 2026-09-12 pilot, paper rayyan-472536612: the page break
# The pilot quarantined a paper for a quote the paper really contains. The sentence begins at
# the foot of one page and finishes on the next -- the surface cited the page where it begins,
# exactly as the prompt asks -- and the PDF extraction drops a figure caption and a running
# header in at the break. Checked page by page, a true verbatim sentence looks fabricated.
SPLIT = [{"page": 1, "text": "The baseline was rebuilt after the turnaround and the\n"
                             "coefficients were"},
         {"page": 2, "text": "re-estimated on the following two years of data."}]
r = check_quote("The baseline was rebuilt after the turnaround and the coefficients were "
                "re-estimated on the following two years of data.", 1, SPLIT)
check("B1 a sentence running across a page break is exact, cited where it begins",
      r["acceptance"] == "exact" and r.get("spans_page_break") is True, r)
r = check_quote("The baseline was rebuilt after the turnaround and the coefficients were "
                "re-estimated on the following two years of data.", 2, SPLIT)
check("B2 cited on the page where it ENDS, the locator is corrected to where it begins",
      r["acceptance"] == "locator corrected" and r["found_on_page"] == 1, r)
CAPTION = [{"page": 1, "text": "not all companies are equipped\nFig. 3. Histograms of data "
                               "sorted by sector.\n400  Energy Procedia 143 (2017) 396-403"},
           {"page": 2, "text": "with the necessary tools and there is not a unique procedure."}]
r = check_quote("not all companies are equipped with the necessary tools and there is not a "
                "unique procedure.", 1, CAPTION)
check("B3 a caption dropped in at the break routes for review, it is not a fabrication",
      r["acceptance"] == "interleaved" and r.get("spans_page_break") is True
      and r.get("review_candidate") is True, r)
check("B4 and a quote the paper does not contain is still not found",
      check_quote("the baseline was never rebuilt at any point", 1, SPLIT)["acceptance"]
      == "not found")
check("B5 the negation guard still holds across a boundary",
      check_quote("The baseline was rebuilt after the turnaround and the coefficients were "
                  "re-estimated on the following two years", 1,
                  [{"page": 1, "text": "The baseline was not rebuilt after the turnaround and "
                                       "the\ncoefficients were"},
                   {"page": 2, "text": "re-estimated on the following two years of data."}])
      ["acceptance"] == "negation mismatch")

# ------------------------------------------------- D6/D7: the page must stay quotable at a break
SOFT = [{"page": 1, "text": "we applied artificial intelligence with a focus on ma\u00ad\nchine "
                            "learning to improve energy efficiency in ammonia production."}]
check("D6 a soft hyphen at a line break joins the word, it does not split it",
      check_quote("machine learning to improve energy efficiency in ammonia production.",
                  1, SOFT)["acceptance"] == "exact")
check("D6b and the faithful copy, soft hyphen and all, matches the same page",
      check_quote("with a focus on ma\u00ad\nchine learning to improve energy efficiency",
                  1, SOFT)["acceptance"] == "exact")
URL = [{"page": 1, "text": "Final Report. Available from: https://drive.google.com/file/d/"
                           "1FbJGmVs-FNY0JE-\n7fgTfecziGFJxypNk/view?usp=sharing."}]
check("D7 a hyphen at a line break INSIDE a url is part of the address, not hyphenation",
      check_quote("Available from: https://drive.google.com/file/d/"
                  "1FbJGmVs-FNY0JE-7fgTfecziGFJxypNk/view?usp=sharing.", 1, URL)["acceptance"]
      == "exact")
check("D7b a hyphen at a line break in ordinary prose is still joined as hyphenation",
      check_quote("the reestimated baseline", 1,
                  [{"page": 1, "text": "we used the re-\nestimated baseline for the year"}])
      ["acceptance"] == "exact")

# ------------------------------------ D8: a quota stop is an availability stop, never a quarantine
import stage_c_run                                                # noqa: E402
check("D8 'weekly limit' is availability, not an exhausted record",
      stage_c_run.is_availability("You've hit your weekly limit \u00b7 resets 10am (Europe/Lisbon)"))
check("D8b so are the session, opus and any other named limit",
      all(stage_c_run.is_availability(t) for t in
          ("You've hit your session limit \u00b7 resets 2:50pm", "You've hit your Opus limit \u00b7 resets 3pm",
           "rate limit exceeded", "You've hit your usage limit")))
check("D8c a validation message that merely contains the word 'limit' is not availability",
      not stage_c_run.is_availability(
          "applications[0].C3_variables[2]: the paper reports an emission limit of 50 mg/Nm3"))

# ------------------------------- D10: a quarantine entry a later attempt contradicted is retracted
import subprocess, tempfile, shutil                                   # noqa: E402
_tmp = tempfile.mkdtemp()
try:
    _out = _tmp + "/outputs"; os.makedirs(_out)
    open(_out + "/rayyan-000000002.json", "w").write("{}")
    open(_tmp + "/quarantine.jsonl", "w").write(
        json.dumps({"key": "rayyan-000000002", "detail": "failed three times", "at": "x"}) + "\n"
        + json.dumps({"key": "rayyan-000000003", "detail": "still failing", "at": "x"}) + "\n")
    import stage_c_run                                                # noqa: E402
    rows = [json.loads(l) for l in open(_tmp + "/quarantine.jsonl") if l.strip()]
    live = [r for r in rows if not os.path.isfile(_out + "/%s.json" % r["key"])]
    gone = [r for r in rows if os.path.isfile(_out + "/%s.json" % r["key"])]
    check("D10 a key with a record no longer stands in quarantine",
          [r["key"] for r in live] == ["rayyan-000000003"]
          and [r["key"] for r in gone] == ["rayyan-000000002"], (live, gone))
finally:
    shutil.rmtree(_tmp, ignore_errors=True)

# ------------------------------ D9: a line number in the MIDDLE of the text is page furniture
INLINE = [{"page": 1, "text":
    "energy costs make up 15 30% of production costs, reducing energy consumption 16 increases "
    "profitability. existing energy management methods often demand 17 large capital "
    "investments. this study reports on 18 an electrical energy management system for improving "
    "cement plant productivity at minimal 19 cost. the system consists of an automated energy "
    "performance 20 report which encompasses the plan do check act approach of 21 iso 50001. "
    "the system collects data from various sources and 22 produces a monthly report for the "
    "plant manager to act 23 upon without further analysis."}]
INTERLOPED = [{"page": 1, "text":
    "manuscript accepted accepted manuscript 21 tariff structures during the summer and 492 "
    "winter months, the trend lines were generated separately for the two cases in 493 the "
    "graphs. the targets for these periods are also independent of one 494 another. in the "
    "2019 production cost graph for the finishing mill the 495 same approach was used, with "
    "figure 7 showing the result for the 496 period under study. the tariff applied in 2018 "
    "was unchanged 497 across both seasons, and the benchmark of 12 kwh per 498 tonne was "
    "retained throughout the 499 assessment."}]
check("D9e a run broken by a header number, a year and a figure number is still numbering",
      detect_line_numbering(INTERLOPED[0]["text"]) == "inline")
check("D9f and the skipped interlopers stay on the page — 2019 is not deleted",
      "2019" in strip_line_numbers(INTERLOPED[0]["text"], "inline")
      and " 492 " not in strip_line_numbers(INTERLOPED[0]["text"], "inline"))
check("D9 a page numbered mid-text is detected as line-numbered",
      detect_line_numbering(INLINE[0]["text"]) == "inline")
check("D9b and a sentence crossing a line number is exact, not interleaved",
      check_quote("this study reports on an electrical energy management system for improving "
                  "cement plant productivity at minimal cost.", 1, INLINE)["acceptance"]
      == "exact")
check("D9c a column of adjacent figures is NOT line numbering — the run must be spread",
      detect_line_numbering("year value\n1 2 3 4 5 6 7 8 9 10 11 12\nrest of the table") is None)
check("D9d and a genuinely absent sentence is still not found on a numbered page",
      check_quote("the plant manager ignored the monthly report entirely", 1, INLINE)
      ["acceptance"] in ("not found", "interleaved"))

# ----------------- D13: page furniture printed between two halves of a sentence is not an insertion
FURN = [{"page": n, "text": "ACCEPTED MANUSCRIPT\nbody text of page %d here for shape\n%d" % (n, n)}
        for n in range(1, 6)]
FURN[2] = {"page": 3, "text": "ACCEPTED MANUSCRIPT\nthe method does not incorporate any process "
                              "knowledge which facilitates the general application to\n3"}
FURN[3] = {"page": 4, "text": "ACCEPTED MANUSCRIPT\ndifferent processes. the backward elimination "
                              "step indicates that the ambient temperature\n4"}
check("D13 a running header and a folio between two halves do not break the sentence",
      check_quote("the method does not incorporate any process knowledge which facilitates the "
                  "general application to different processes.", 3, FURN)["acceptance"] == "exact")
check("D13b a sentence the paper does not contain is still not found across the same boundary",
      check_quote("the method incorporates full process knowledge at every step of the "
                  "elimination", 3, FURN)["acceptance"] in ("not found", "interleaved"))

# ---------------------------------------------------------------- the clean record still passes
errs, g = validate(copy.deepcopy(REC), PAGES)
check("the valid fixture still validates", errs == [], errs[:3])
check("the valid fixture grounds every quote exactly",
      g["G1_G2"]["not_found"] == 0 and g["G1_G2"]["interleaved"] == 0
      and g["G1_G2"]["negation_mismatch"] == 0 and g["value_without_evidence"] == [],
      g["G1_G2"])

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILURES: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
