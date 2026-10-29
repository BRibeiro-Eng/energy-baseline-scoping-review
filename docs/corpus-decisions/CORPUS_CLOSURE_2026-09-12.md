# Corpus closure — 2026-09-12

**Status:** Corpus A and Corpus B **locked**. §3-Step-4 candidate union exhausted on
the Claude surface; §3-Step-5 size branch selected from the locked |B|.

| | Locked value |
|---|---|
| **Corpus A** (eligible, all sectors) | **331** |
| **Corpus B** (continuous process, §5.3 registered sectors) | **42** |
| Declared exploratory cases (unlisted continuous-flow sectors) | **13** |
| Tier-2 branch | `25 < |B| ≤ 60` → **40 blind-first** + **2** AI-prefill + verification |
| Confirmed false negatives | **0** — §6a not triggered |

---

## 1. Provenance of these decisions — stated first, because it is a deviation

The seven verdicts below were adjudicated by the reviewer **in conversation**, on
verbatim source extracts — each detector quote plus the surrounding extracted
page text — rendered by the AI assistant. The quotes are the papers' own text
with physical page numbers, and every verdict turns on what those quotes say.

**The reviewer did not open the full PDFs**, and the dwell and evidence gates of
`output/fn_census_triage_c_serve.py` were therefore never exercised. This is
weaker than blind-first form adjudication and is reported as such wherever these
seven decisions are used. What it is not is unexamined: each verdict records the
quote, the page, and a reasoned justification naming the §5.3 clause it turns on.

## 2. Detector (c) — the pass

394/394 papers, Claude Code CLI surface, one clean session per paper, tools
disabled. One paper (`rayyan-472536601`) failed the grounding check on three
consecutive attempts — two-column extraction interleaves the columns, so verbatim
quotes score 66–79 — was quarantined, and produced a valid response on a later
attempt. No paper is missing a response. 144 run interruptions from session-limit
resets are recorded separately in `availability_interruptions.jsonl`; they are
availability events, not validation failures.

The pass fired on **186 of 394** papers, by design: the prompt instructs the model
to list any continuous-process signal even when confident the paper is out of
scope. Of those, 50 are outside Corpus A (Corpus B ⊂ Corpus A, so they cannot
enter without reopening eligibility — a Tier-1 action), leaving **136 eligible
and outside Corpus B**.

## 3. Partition and decisions

| Partition | Rule (all from §5.3) | N | Outcome |
|---|---|---|---|
| Stratum I | signal names a registered sector · strong application | 2 | both **out** |
| Exploratory | strong application, sector **not** on the §5.3 list | 12 (+1) | all **kept out** |
| Stratum II | `application_strength ∈ {mentioned_only, none}` | 122 | excluded by the registered criterion; at-risk subset read exhaustively |

### 3.1 Stratum I — both excluded

**`rayyan-472536698`** — *"Table 1. EPI calculation results in stainless steel
production"* (p.7). Steel by name, discrete by production mode: the table's
entities are Oven, Presser and Drop hammer, Turning machine, Boring and CNC
machine, Ring roller, grouped into lines L1–L3 — forging and machining of steel
parts. §5.3 lists *"Steel (and other primary-metals **continuous** production)"*
and excludes *"discrete manufacturing (parts, assembly, batch production)"*. Both
models charted A9 = discrete manufacturing, concordant. The glass and cement
signals are a literature-review sentence on Energy Star sector benchmarking.

**`rayyan-472535679`** — *"Figure 2. Application of the House of Quality diagram
on the data of the enterprise JSC KazanOrgSyntez"* (p.1). The sector test passes:
KazanOrgSyntez is an organic-synthesis producer and the method is demonstrated on
its own data. It fails the other half of §5.3 — what is applied is a QFD matrix
aligning energy-efficiency strategy goals with corporate strategy goals. No EnPI,
no energy baseline, not one measured energy quantity. Excluded on **what the model
is**, not on the sector.

### 3.2 Stratum II — an exhaustive at-risk census replaces the random sample

The registered design drawn on 2026-09-11 (`DETECTOR_C_TRIAGE_DESIGN_2026-09-11.md`)
specified a sub-stratified random sample: IIa n=25 seed 46, IIb n=8 seed 47. It was
replaced, **before any verdict was recorded**, by an exhaustive pass over a
deterministically defined at-risk subset: the Stratum-II papers whose **own charted
sector** (A8, not a cited sector) matches a §5.3 registered sector. That subset is
**5 papers**, all read.

| Paper | A8 | Disposition |
|---|---|---|
| `rayyan-472536390` | aluminium parts, automotive | out — discrete metal parts |
| `rayyan-472536468` | transformers across 4 plants incl. aluminium profile | out — A9=mixed, no continuous primary metals |
| `rayyan-472536481` | aluminium alloy die-casting, engine blocks | out — die-casting of parts |
| `rayyan-472535733` | petroleum industry (A9 = continuous process) | out — all five refining signals are citations to Worrell & Galitsky 2005 and Zhang et al. 2013; the paper's own contribution is a SWOT and EPC design recommendations |
| `rayyan-472536757` | corn refining (wet corn milling) | **reclassified as the 13th exploratory case** — genuinely continuous (*"operate continuously for nearly 365 days per year"*, p.6) and genuinely empirical, but food/agricultural processing is not a §5.3 sector; the `refining` match was the word |

**Declared limitation of the substitution.** The random IIa sample would have
bounded the misclassification rate of `application_strength` across all 81 papers
carrying a registered-sector signal (one-sided 95% upper bound 11.3% at 0/25). The
census instead closes the highest-probability path with certainty rather than with
a sampling fraction, and leaves a residual blind spot: a paper whose own A8 does
not name a listed sector yet which applies in one. That requires **two independent
failures** — both models mis-charting A8 and the detector rating the paper
`mentioned_only` — and is reported as a residual risk, not as a bounded one. The
census is narrower and deeper than the sample, not stronger.

### 3.3 Exploratory cases — dated corpus decision, list not expanded

13 papers in continuous-flow sectors outside the §5.3 list: combined-cycle
thermal power · ceramics (tile, brick, sanitary ware) · municipal sewage treatment ·
sugar · upstream oil & gas (gathering centres, offshore platforms) · non-metallic
minerals (gypsum calcination) · continuous-production food · wet corn milling.

**Decision: none added to the main list.** The §5.3 main sector list was pre-specified to resolve the v2.1 circularity (non-stationarity cannot both define membership and be the phenomenon investigated). Expanding it after seeing which papers would enter is selection on the outcome, and the same logic that barred deciding membership by the phenomenon bars deciding it by the papers available. Operationally, |B|=42 already commits 40 blind-first papers (35-55 h); adding these would approach the |B|>60 cliff that forces a pause and supervisor decision. Upstream oil & gas was considered on the merits — a gathering centre is continuous-flow and nearer the Sines case than ceramics — and still declined, because 'nearer' is not 'on the registered list'. All are reported as declared exploratory cases outside the main Corpus B, available to the narrative synthesis but absent from every Corpus-B count.

Recorded in `triage/verdicts/_exploratory_decision.json`; to be carried into
`run_metadata.json` and the OSF amendment.

## 4. Closure statement (§3-Step-4)

Detector (a) model flags, (b) deterministic lexicon and (c) counter-anchored
recall have all run; the (c) pass is complete at 394/394. Of the candidates it
surfaced, **zero are confirmed false negatives** of Corpus-B membership.
Therefore **§6a does not trigger** — no lexicon expansion, no detector-(b)
re-run, no supervisor escalation — and the registered candidate union is
exhausted on this surface. What this does not claim: false negatives outside the
registered union, which no detector in this design can reach.

## 5. Size branch (§3-Step-5), selected from the locked |B| = 42

Remainder after the fixed head is 17 papers, so the C-2.3 edge case
(remainder ≤ 15 → integral blind-first) does **not** apply.
`n_sub = min(15, 42−25) = 15`, drawn seed 44 without replacement.
Total blind-first = `25 + 15 = 40`; the 2 papers beyond 40 receive AI pre-fill
plus field-by-field human verification. Protocol budget for this branch: **35–55 h**.

Sector-priority order: refining first, then petrochemicals, then the remaining
sectors; 2020+ first, then recency, then key as final tiebreaker.

### Head of 25 — blind-first

| Paper | Group | Year | A8 |
|---|---|---|---|
| `rayyan-472535351` | refining | 2025 | oil refinery |
| `rayyan-472535365` | refining | 2025 | gas refinery |
| `rayyan-472535625` | refining | 2017 | oil refinery |
| `rayyan-472536695` | refining | 2013 | refining |
| `rayyan-472535524` | petrochemicals | 2020 | petrochemical production site |
| `rayyan-472535550` | petrochemicals | 2019 | petrochemical |
| `rayyan-472536532` | petrochemicals | 2019 | Propylene oxide production |
| `rayyan-472535582` | petrochemicals | 2018 | petrochemical plant |
| `rayyan-472535649` | petrochemicals | 2017 | fertilizer company |
| `rayyan-472535680` | petrochemicals | 2016 | petrochemical enterprise |
| `rayyan-472536693` | petrochemicals | 2013 | pulp and paper, basic metals and petrochemicals industries |
| `rayyan-472535376` | remaining | 2025 | sulfuric acid production |
| `rayyan-472536358` | remaining | 2025 | industrial gases production |
| `rayyan-472535405` | remaining | 2024 | steel industry |
| `rayyan-472536226` | remaining | 2024 | ammonia production |
| `rayyan-472536379` | remaining | 2024 | steel industry |
| `rayyan-472536410` | remaining | 2023 | pulp and paper industry |
| `rayyan-472536425` | remaining | 2022 | oil companies |
| `rayyan-472536428` | remaining | 2022 | manufacturing industry |
| `rayyan-472535480` | remaining | 2021 | pulp and paper industry |
| `rayyan-472536455` | remaining | 2021 | cement industry |
| `rayyan-472536486` | remaining | 2021 | building material manufacturing (cement) industry end-user and metal processing (aluminium) industry end-user |
| `rayyan-472536487` | remaining | 2021 | container glass and tableware glass |
| `rayyan-472535522` | remaining | 2020 | dry paper production plant |
| `rayyan-472535532` | remaining | 2020 | cement industry |

### Random sub-sample n=15, seed 44 — blind-first

| Paper | Group | Year | A8 |
|---|---|---|---|
| `rayyan-472535585` | remaining | 2018 | cement manufacturing |
| `rayyan-472535748` | remaining | 2014 | metallurgical plants |
| `rayyan-472535750` | remaining | 2014 | manufacturing and distribution operations |
| `rayyan-472535762` | remaining | 2013 | cement industry |
| `rayyan-472535787` | remaining | 2012 | cement industry |
| `rayyan-472535794` | remaining | 2012 | Glass and cast iron melting processes |
| `rayyan-472536501` | remaining | 2020 | aluminum industry |
| `rayyan-472536518` | remaining | 2020 | manufacturing industry sectors |
| `rayyan-472536551` | remaining | 2019 | oil and gas |
| `rayyan-472536588` | remaining | 2018 | lime industry |
| `rayyan-472536606` | remaining | 2017 | manufacturing |
| `rayyan-472536612` | remaining | 2017 | nine industrial sectors |
| `rayyan-472536644` | remaining | 2016 | integrated steel |
| `rayyan-472536694` | remaining | 2013 | cement manufacturing |
| `rayyan-472536714` | remaining | 2012 | manufacturing |

### Beyond 40 — AI pre-fill + field-by-field verification

| Paper | Group | Year | A8 |
|---|---|---|---|
| `rayyan-472535628` | remaining | 2017 | cement plant |
| `rayyan-472535797` | remaining | 2011 | cement industry |

One rule-produced classification worth seeing: `rayyan-472536693`
("pulp and paper, basic metals and petrochemicals industries") entered the
petrochemical group because the priority regex matched one of the three sectors it
spans. Defensible, and visible here rather than buried.

## 6. Immediately downstream

1. **11 Stage-3 supplements** on the locked roster (`STAGE3_SUPPLEMENTS_2026-09-12.json`):
   papers a model classified `level_3b=false` and the reviewer adjudicated in.
   A Stage-3-only supplement receives the roster decision as a downstream routing
   fact and must not revisit Stage 1/2; the original negative stays immutable in
   the Tier-1 error record.
2. **51 Corpus-A papers have Level-A from one model surface only** (46 chatgpt,
   5 claude) — adjudicated eligible after one model short-circuited Level A, so
   they carry no inter-model divergence signal at all and bypass the
   reconciliation design. Separate problem from this closure, no queue yet.
3. **B6 enum.** The registered `specific_limitations` enum returns 0 fouling and
   0 catalyst deactivation across the Level-B pre-fill, with 15 of 18 limitation
   papers coded `other`. Extending it before blind-first extraction starts is a
   prospective refinement; doing it afterwards is post-hoc recoding.

## 7. What the OSF amendment must carry

- The dated corpus decision of §3.3 (list not expanded; 13 exploratory cases).
- The Stratum-II design substitution of §3.2 **and its declared residual risk**.
- The chat-adjudication provenance of §1 for the seven verdicts.
- The locked |B| = 42 and the branch selection, with the seed-44 draw.
- The detector-(c) limitations: single surface, mixed `models_returned`
  (`claude-haiku-4-5` alongside the pinned `claude-opus-4-8`), one quarantined
  and repaired paper.

Rebuild every number here with
`python3 output/fn_census_triage_c_build.py && python3 output/fn_census_close_corpus.py`.

---

## Adenda 2026-09-17 — B ⊂ A

O fecho de 2026-09-12 declarou |B| = 42, mas dois desses relatórios (`rayyan-472535628`,
`rayyan-472535750`) tinham elegibilidade metodológica adjudicada como falsa e não estavam em A.
Decisão do revisor: mantém-se o veredicto cego de elegibilidade e aplica-se B ⊂ A. **|B| = 40**
(39 cartografados + 1 em quarentena). A = 331 inalterado. O ramo `25 < |B| ≤ 60` não muda.
Os valores acima ficam como registo do que foi decidido em 12/09. Detalhe e alterações:
`stage_c/B_SUBSET_A_2026-09-17.md`.
