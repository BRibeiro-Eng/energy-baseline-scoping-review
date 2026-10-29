#!/usr/bin/env python3
"""Corpus closure — §3-Step-4 (FN candidate union) and §3-Step-5 (size branch).

Records the reviewer's decisions of 2026-09-12, locks the Corpus-B roster, and
selects the pre-registered Tier-2 size branch from the locked |B|.

PROVENANCE, stated plainly because it is a deviation from the form-based
instrument: these seven verdicts were adjudicated by the reviewer IN
CONVERSATION, on verbatim source extracts — the detector's quote plus the
surrounding extracted page text — rendered by the AI assistant. The quotes are
the papers' own text with physical page numbers, and each verdict turns on what
those quotes say. The reviewer did NOT open the full PDFs, and the dwell and
evidence gates of `fn_census_triage_c_serve.py` were therefore not exercised.
This is weaker than blind-first form adjudication and is reported as such.
"""
import json, os, csv, glob, random, re, datetime, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus_profile import rosters, _get, SECTOR_RX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
D, T = "output/fn_census/detector_c", "output/fn_census/detector_c/triage"
V = f"{T}/verdicts"; os.makedirs(V, exist_ok=True)
NOW = datetime.datetime.now().isoformat(timespec="seconds")
DATE = "2026-09-12"
PROV = ("adjudicated in conversation on verbatim source extracts (detector quote + "
        "surrounding extracted page text) presented by the AI assistant; reviewer did "
        "not open the full PDF; form dwell/evidence gates not exercised")

DECISIONS = [
 dict(key="rayyan-472536698", stratum="I", verdict="out", page=7,
      quote="Table 1. EPI calculation results in stainless steel production",
      justification=("Steel by name, discrete by production mode. Table 1's entities are "
                     "Oven, Presser and Drop hammer, Turning machine, Boring and CNC machine, "
                     "Ring roller, grouped into production lines L1-L3 — forging and machining "
                     "of steel parts. PROTOCOL.md §5.3 lists 'Steel (and other primary-metals "
                     "CONTINUOUS production)' and excludes 'discrete manufacturing (parts, "
                     "assembly, batch production)'. Both models charted A9=discrete "
                     "manufacturing, concordant. The glass and cement signals are a "
                     "literature-review sentence on Energy Star sector benchmarking, i.e. "
                     "citations, not application.")),
 dict(key="rayyan-472535679", stratum="I", verdict="out", page=1,
      quote=('Figure 2. Application of the House of Quality diagram on the data of the '
             'enterprise "JSC "KazanOrgSyntez"'),
      justification=("The enterprise is a registered-sector (organic synthesis / petrochemical) "
                     "producer and the method is demonstrated on its own data, so the sector "
                     "test passes. It fails the other half of §5.3: what is applied is a "
                     "QFD/House-of-Quality matrix aligning energy-efficiency strategy goals with "
                     "corporate strategy goals. No EnPI, no energy baseline, no measured energy "
                     "quantity — therefore no EnPI/EnB model is applied, validated or "
                     "empirically demonstrated. A1b=methodological/theoretical, A9='not "
                     "specified'. Excluded on what the model is, not on the sector.")),
 dict(key="rayyan-472536390", stratum="II_risk", verdict="citation", page=None, quote=None,
      justification=("Own A8 is 'aluminium parts in the automotive industry'; A9=discrete "
                     "manufacturing. Aluminium component manufacturing is discrete metal parts, "
                     "not primary-metals continuous production (§5.3 exclusion).")),
 dict(key="rayyan-472536468", stratum="II_risk", verdict="citation", page=None, quote=None,
      justification=("Power-transformer losses across four plants (automotive, textile, "
                     "aluminium profile, chemical products); A9=mixed. No continuous "
                     "primary-metals production context; the aluminium match is a profile "
                     "extrusion plant among four sites.")),
 dict(key="rayyan-472536481", stratum="II_risk", verdict="citation", page=None, quote=None,
      justification=("Energy Value Mapping in an aluminium alloy die-casting plant producing "
                     "automotive engine blocks; A9=discrete manufacturing. Die-casting of parts "
                     "is discrete/batch, not continuous primary-metals production.")),
 dict(key="rayyan-472535733", stratum="II_risk", verdict="citation", page=3,
      quote=("For US refineries, it was stated that the energy consumption in the plants could "
             "be reduced by 10-20% (Worrell and Galitsky 2005) by following a structured energy "
             "management system"),
      justification=("A8='petroleum industry' and A9=continuous process, so the sector is "
                     "registered — but every one of the five refining signals is a citation to "
                     "someone else's work (Worrell and Galitsky 2005; Zhang et al. 2013). The "
                     "paper's own contribution is a SWOT analysis and design recommendations for "
                     "EPC contracts. §5.3: 'Implicit, theoretical-only, or could be applied to "
                     "is not sufficient.' No own application.")),
 dict(key="rayyan-472536757", stratum="II_risk", verdict="exploratory_unlisted_sector", page=6,
      quote=("Typical plants in the US process at least 100,000 bushels per day (bu/day, or "
             "2,500 tonne/day) and operate continuously for nearly 365 days per year."),
      justification=("Genuinely continuous (365 days/year, 2500 t/day) and genuinely empirical "
                     "(stochastic frontier analysis building an ENERGY STAR EnPI tool) — but wet "
                     "corn milling is food and agricultural processing and is NOT one of the "
                     "eight §5.3 registered sectors. The 'refining' match was the word, not "
                     "petroleum refining. Reclassified as the 13th exploratory case under §5.3's "
                     "unlisted-sector rule; not a Corpus-B membership decision.")),
]
for d in DECISIONS:
    rec = dict(d, decided_at=NOW, source="chat_adjudication", provenance=PROV,
               protocol="C-2.3 §3-Step-4", dwell_seconds=None)
    json.dump(rec, open(f"{V}/{d['key']}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

S = json.load(open(f"{T}/SUMMARY.json", encoding="utf-8"))
explor = sorted(set(S["exploratory_unlisted_sector"]) | {"rayyan-472536757"})
json.dump({
    "decision": "keep_out", "sectors_added": [], "papers": explor, "n": len(explor),
    "rationale": ("The §5.3 main sector list was pre-specified to resolve the v2.1 circularity "
                  "(non-stationarity cannot both define membership and be the phenomenon "
                  "investigated). Expanding it after seeing which papers would enter is "
                  "selection on the outcome, and the same logic that barred deciding membership "
                  "by the phenomenon bars deciding it by the papers available. Operationally, "
                  "|B|=42 already commits 40 blind-first papers (35-55 h); adding these would "
                  "approach the |B|>60 cliff that forces a pause and supervisor decision. "
                  "Upstream oil & gas was considered on the merits — a gathering centre is "
                  "continuous-flow and nearer the Sines case than ceramics — and still declined, "
                  "because 'nearer' is not 'on the registered list'. All are reported as "
                  "declared exploratory cases outside the main Corpus B, available to the "
                  "narrative synthesis but absent from every Corpus-B count."),
    "decided_at": NOW, "protocol": "PROTOCOL.md §5.3 dated corpus decision",
    "source": "chat_adjudication",
}, open(f"{V}/_exploratory_decision.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---- roster lock + §3-Step-5 branch -----------------------------------------
R = rosters(); C, G = R["C"], R["G"]
B = sorted(R["corpus_b"])
assert len(B) == 42, len(B)
years = {}
with open("data/articles.csv", newline="", encoding="utf-8", errors="replace") as fh:
    for r in csv.DictReader(fh):
        try: years[r["key"]] = int(r["year"])
        except (TypeError, ValueError): pass

REFINING = r"refin(?!ed sugar)|petroleum industry|crude oil"
PETCHEM  = r"petrochem|propylene|olefin|polymer|organic synth|ethylene"
def group(k):
    a8 = f"{_get(C.get(k,{}),'stage2','sector_of_activity') or ''} {_get(G.get(k,{}),'stage2','sector_of_activity') or ''}"
    if re.search(REFINING, a8, re.I): return 0, "refining"
    if re.search(PETCHEM, a8, re.I):  return 1, "petrochemicals"
    return 2, "remaining"

rows = []
for k in B:
    g, name = group(k); y = years.get(k, 0)
    rows.append({"key": k, "priority_group": name, "year": y,
                 "a8": _get(C.get(k,{}),"stage2","sector_of_activity") or _get(G.get(k,{}),"stage2","sector_of_activity")})
rows.sort(key=lambda r: (group(r["key"])[0], 0 if r["year"] >= 2020 else 1, -r["year"], r["key"]))
head = [r["key"] for r in rows[:25]]
remainder = [r["key"] for r in rows[25:]]
n_sub = min(15, len(B) - 25)
sub = sorted(random.Random(44).sample(remainder, n_sub))
prefill = [k for k in remainder if k not in sub]

branch = {
    "locked_B": len(B), "branch": "25 < |B| <= 60", "K_head": 25, "n_sub": n_sub,
    "n_sub_seed": 44, "blind_first_total": 25 + n_sub,
    "edge_case_integral_applies": len(remainder) <= 15,
    "sector_priority_rule": "refining, then petrochemicals, then remaining; 2020+ first, then recency, then key",
    "sector_priority_head_25": head, "random_sub_sample_15": sub,
    "ai_prefill_plus_verification": prefill,
    "order": rows, "locked_at": NOW,
}
json.dump(branch, open(f"{T}/../ROSTER_LOCK_{DATE}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# Stage-3 supplements needed on the locked roster
supp = {k: [m for m, S_ in (("claude", C), ("chatgpt", G)) if not isinstance(S_[k].get("stage3"), dict)]
        for k in B}
supp = {k: v for k, v in supp.items() if v}
json.dump(supp, open(f"{T}/../STAGE3_SUPPLEMENTS_{DATE}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"|B| LOCKED = {len(B)}   branch = {branch['branch']}   blind-first = {branch['blind_first_total']}"
      f"   AI-prefill+verify = {len(prefill)}   edge-case integral = {branch['edge_case_integral_applies']}")
print(f"exploratory cases = {len(explor)}   verdicts written = {len(DECISIONS)}")
print(f"Stage-3 supplements needed = {len(supp)}")
print("\n-- sector-priority head (25) --")
for r in rows[:25]:
    print(f"  {r['key']} | {r['priority_group']:15s} | {r['year']} | {str(r['a8'])[:58]}")
print("\n-- remainder (17): sub-sample n=15 seed 44 blind-first, 2 on AI prefill + verification --")
for r in rows[25:]:
    tag = "BLIND" if r["key"] in sub else "PREFILL"
    print(f"  [{tag:7s}] {r['key']} | {r['priority_group']:15s} | {r['year']} | {str(r['a8'])[:48]}")
