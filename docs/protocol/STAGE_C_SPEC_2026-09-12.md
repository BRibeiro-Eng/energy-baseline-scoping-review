# Stage C — targeted re-extraction and per-paper dossiers over Corpus B (n = 42)

**Date:** 2026-09-12 · **Status:** draft for reviewer comment, nothing built yet
**Scope:** the 42 locked Corpus-B papers · **Schema:** new, `v2.3.0-C` (v2.2.1 stays FROZEN)
**Replaces:** the §3-Step-5 blind-first Level-B extraction, in the form described in §1

---

## 1. What this is, and what it costs — read before the field list

`VALIDATION_PROTOCOL_C.md` §2 states the constraint this stage breaks, in its own words:

> Inter-model agreement is used **only as a routing signal** to allocate human effort —
> **never** as a reliability metric. AI-vs-AI consistency shares model biases and cannot
> certify correctness.

Stage C extracts Level-B/C values with two model families and compares them. If nothing
human sits on top, the comparison is the evidence, and that is the one thing the protocol
says it cannot be. So the stage has to be honest about its output class.

**What the review can still claim after Stage C**

- Every extracted value carries a verbatim quote that string-matches the PDF after the
  §6.3 normalisation. The corpus-wide grounding check already ran at 7 075/7 075 on the
  v2.2.1 values; the same check runs on Stage C. **Textual traceability is real and cheap.**
- The field set is pre-specified and published before extraction, not fitted to results.
- Two independent model families extracted the same fields; the per-field divergence
  profile is reported as a descriptive property of the instrument.
- Corpus membership (A = 331, B = 42) was adjudicated by the reviewer and is unaffected.
- Tier-1 blind-first adjudication (82 papers) stands as it is.

**What it cannot claim**

- That Level-B/C values are human-verified. They are not.
- That agreement implies correctness. It implies the two models read the same sentence.
- Any per-field error bound for Level B. There is no human reference set to bound against.
- The §3-Step-5 blind-first design as executed. It was not executed.

**The cheap way to buy the claim back.** The protocol's 40 blind-first papers cost 35–55 h,
which is why this plan exists. But the thesis does not argue from all 42 equally: SQ4 and the
transferability argument rest on the refining and petrochemical head. That is **11 papers**
(4 refining + 7 petrochemical, from `ROSTER_LOCK_2026-09-12.json`). Read blind-first at
~40 min each that is **≈ 7 h**, not 35–55.

Doing those 11 blind-first, with the form withholding model output until commit, gives:
a human-adjudicated core exactly where the argument is load-bearing · a reported
reveal-change rate on 11 papers · and an AI-extracted periphery of 31 papers with its status
declared. That is a defensible two-tier design. Pure Stage C with no human layer is not — it
is a declared deviation that weakens every SQ2–SQ4 number.

**Recommendation: Stage C as specified, plus the 11-paper blind-first core.** The rest of
this document assumes the core is in; if it is dropped, §8's reporting language changes and
§1's "cannot claim" list is what the methods chapter has to say.

---

## 2. Why re-extract at all

Four concrete failures of the v2.2.1 Level-B fields, all measured on the 42-paper pre-fill:

| Field | Failure | Evidence |
|---|---|---|
| B6 `specific_limitations` | enum too narrow to hold the answer to SQ2 | 45 of 49 records code `other`; 0 fouling, 0 catalyst deactivation |
| B5 `identifies_model_limitations` | catches **study** limitations, not model limitations | *"Further research is suggested"*, *"I cannot get data from all factories"* coded as model limitations; claude True 19/32 vs chatgpt True 30/41 |
| B1 `normalisation_variables` | granularity unresolvable between models | claude decomposes (`['natural gas consumption','heat generation','power generation']`), chatgpt aggregates (`['thermal energy plus the electrical energy generated']`) |
| B13b `performance_metrics_reported` | empty is ambiguous | empty for 7 of 31 — cannot tell "fitted but unreported" from "unfitted model, nothing to report" |

Plus three things the synthesis needs and no field captures: what is on the left-hand side of
the model, whether the energy quantity is actually metered at the boundary, and whether the
baseline is ever rebuilt.

---

## 3. Field set — `v2.3.0-C`

Every field keeps the v2.1 envelope: `{value, evidence_quote, page, non_contiguous_evidence,
confidence}`. `não reportado` is always available and always preferable to inference.
Carried over unchanged: B2a/B2b (baseline period), B4/B4b (scale, scope), B7, B8, B10, B11,
B12, B13a, B14. New and revised:

**C1 `dependent_variable`** — enum + verbatim + unit. What is being modelled:
`total site energy` · `electricity only` · `fuel only` · `steam or heat only` ·
`specific energy consumption` · `energy cost` · `CO₂` · `other (verbatim)`.
*Rationale: absent from v2.2.1, and two models of "energy" that differ on the left-hand side
are not comparable. First thing the synthesis table needs.*

**C2 `functional_form`** — enum (multi), finer than A11:
`unfitted intensity ratio` · `SEC mean` · `OLS 1 IV` · `OLS ≥2 IV` · `stepwise` ·
`segmented / piecewise` · `change-point` · `ANN` · `tree ensemble` · `SVM / kernel` ·
`other ML` · `first-principles balance` · `exergy` · `hybrid physical-statistical` ·
`DEA / stochastic frontier` · `composite index` · `none`.

**C3 `normalisation_variables_typed`** — list of objects: `{verbatim, type}`, where `type` is
from a closed list: `production volume or throughput` · `product mix or quality` ·
`feed quality or composition` · `ambient conditions` · `operating mode or campaign` ·
`equipment configuration` · `capacity utilisation` · `time or calendar` · `other`.
*Rationale: this ends the granularity war. The verbatim names may differ between models and
that is fine; the **type** assignment is what gets compared and counted. Divergence on type is
substantive; divergence on wording is not.*

**C4 `data_frequency`** — enum: `sub-hourly` · `hourly` · `daily` · `weekly` · `monthly` ·
`annual` · `audit snapshot` · `not reported`. Plus `span_months` (int | null) and
`n_observations` (int | null, only if the paper states it).

**C5 `measurement_boundary`** — enum: `dedicated meter at the boundary` ·
`site meter allocated to the boundary` · `invoice or utility bill` ·
`inferred or calculated from process data` · `simulated` · `not reported`.
*Rationale: operationalises the dominant SQ2 mechanism (M1, 6+ papers) and is the single
most transferable question to Sines — the IP21 historian answers it or it does not.*

**C6 `re_estimation_regime`** — enum: `not stated` · `fixed baseline, never rebuilt` ·
`periodic, interval stated` · `event-triggered, trigger stated` · `rolling window` ·
`online / adaptive`. Plus `trigger_verbatim` when applicable.
*Rationale: operationalises M6 (baseline drift) and is the direct evidence for SQ3.*

**C7 `validity_envelope`** — enum: `stated with numeric bounds` · `stated qualitatively` ·
`not stated`; plus `bounds_verbatim`.
*Rationale: operationalises M4. `"trustworthy only for the operating points inside of the
hull"` is the kind of statement that currently vanishes into `other`.*

**C8 `fit_metrics`** — `{status, metrics[]}` where status is
`reported` · `not reported` · `not applicable — unfitted model`. Metrics keep the v2.2.1
structured shape (`metric, value, unit, period_or_context, evidence_quote, page`).
*Rationale: removes the ambiguity of an empty list.*

**C9 `model_limitation_mechanisms`** — enum (multi). The four registered values stay:
`non-stationarity` · `fouling` · `catalyst deactivation` · `feedstock variability`.
Added, each derived from the charted evidence of the 42:

| Value | One-line definition | Anchor quote from the corpus |
|---|---|---|
| `observability gap` | a quantity the model needs is not measured, not measured continuously, or not separable | *"they lack the instruments needed for their proper definition"*; *"the calorific value of coal cannot be measured continuously"* |
| `multi-product allocation` | energy cannot be attributed to a product or stream | *"energy consumption of a single product in a multi-product process can only be determined by incorporating additional process knowledge"* |
| `baseload / non-productive energy` | consumption that does not scale with output distorts the indicator | *"energy consumption which does not contribute to the production volume (called as baseload) has effects on the specific energy consumption"* |
| `partial load or validity envelope` | accuracy degrades outside the observed operating range | *"the model cannot be considered very accurate for small productions"*; *"its accuracy outside of the limits cannot be guaranteed"* |
| `statistical misspecification` | non-linearity, heteroscedasticity, outlier sensitivity, spurious association | *"when the error variance is not constant, the error term is called heteroscedastic"* |
| `baseline drift / temporal validity` | the fitted baseline expires and must be rebuilt | *"the energy baseline model is no longer suitable for estimating the current state of EnPI"* |
| `cross-site comparability` | heterogeneity between plants breaks a shared benchmark | *"has an entirely different energy usage pattern from the other plants. The data from this factory excluded"* |
| `interaction with improvement programmes` | a concurrent intervention perturbs the indicator | *"the clinker index reduction program has an impact on electrical energy performance"* |

Plus `other` and `none`. **Coding rule:** a statement goes to C9 only if it constrains the
model's construction or validity. Practical obstacles to implementing measures stay in B14.
Limitations of the **study** go to C10, never here.

**C10 `study_limitations`** — enum (multi), new: `sample size or coverage` ·
`data access or availability` · `scope restricted by choice` · `future work only` · `none`.
*Rationale: gives the study-limitation statements somewhere to go, so they stop inflating the
SQ2 count. This is the field whose absence is currently corrupting B5.*

**C11 `adaptation_types`** — enum (multi), extended from B9:
`dynamic or rolling window` · `segmented or clustered baseline` · `piecewise / change-point` ·
`additional normalisation variable` · `hybrid physical-statistical` ·
`online re-estimation` · `regime or outlier exclusion` · `weighted estimation (WLS etc.)` ·
`normalisation to a reference product` · `other` · `none`.
*Rationale: B9 coded 10 of 12 as `other`; the same failure as B6, same fix.*

**C12 `method_data_requirements`** — list of free strings: what data and metadata the method
requires to be reproduced elsewhere (variables, frequency, span, instrumentation).
**Factual, from the paper only.** The transferability *verdict* for Sines is the reviewer's
and is not an extraction field — the AI states what the method needs, the reviewer decides
whether Sines has it.

**C13 `reproducibility`** — object of enums, each `yes` / `partial` / `no`:
`equations_given` · `coefficients_given` · `data_available` · `code_available`.
*Rationale: quantifies the "case-report shaped evidence" finding with something checkable.*

---

## 4. The dossier — one per paper

### 4.1 Separate run, separate session

The extraction and the dossier are **two calls, not one**. Schema-constrained JSON and
discursive prose in the same completion contaminate each other: the prose reasoning drags
cell values toward narrative coherence, and the schema drags the prose toward enum language.

Order: **extraction first, blind to any dossier** (both model families, independent
sessions, tools disabled, one clean session per paper — the detector-(c) discipline). **Dossier
second**, and the dossier *may* read both extractions, because it is support material and its
job includes showing where they disagree.

### 4.2 Status, stated at the top of every dossier

> Support material for writing. Not review data. Fills no extraction cell, enters no
> `merged.csv`, feeds no results table. Produced by a reader, not an adjudicator.

### 4.3 Structure

Revised from `output/dossiers/PROMPT_DOSSIER.md` (which was written against 31 papers and the
old field set). Eleven sections, in this exact order:

1. **Header** — title, authors, year, journal, DOI, pages. One line.
2. **What the paper does** — ≤120 words of prose. Object, method, installation, main result.
   No evaluative adjectives.
3. **Empirical context** — sector and sub-process · country · organisation type · scale ·
   data period and frequency · data source. Every item with its page. `não reportado` where
   the paper is silent.
4. **The energy performance model** — the centre. Per model presented:
   dependent variable and unit (C1) · functional form (C2) · independent variables one by one
   **as the paper names them**, each with its type (C3) · estimation method and software ·
   baseline and comparison periods · fit metrics with values and pages (C8) · validation.
5. **Measurement and boundary** — is the energy quantity metered at the boundary, allocated,
   invoiced, or inferred (C5)? What is inside the boundary and what is excluded?
6. **Temporal validity** — does the paper say when the baseline is rebuilt (C6)? Does it state
   an operating range over which the model holds (C7)? Verbatim, with page.
7. **Formulas** — each relevant equation, with the paper's own number and the page, in LaTeX
   when transcription is unambiguous. **If the equation is an image and the extracted text
   does not contain it: `equação em imagem — p.N, transcrever à mão`, and move on.** Never
   reconstruct by inference — a flipped sign is worse than a gap.
8. **Figures and tables worth the trip** — only those that carry an argument. Number, page,
   what it shows, and one line on why it matters to a thesis on refinery energy performance
   monitoring. No decorative figures, no generic org charts.
9. **Quotable extracts, 5 to 10** — verbatim, with page, chosen because they state a
   mechanism, a limitation, an adaptation, or a number the chapter will cite.
10. **The two extractions side by side** — per field: claude value, chatgpt value, agree or
    not, and for C3 whether the divergence is in wording or in **type**. This is the section
    that tells the reviewer where to look.
11. **Gaps** — what the dossier could not establish, and what a human would have to open the
    PDF to settle. Explicit, not implied.

### 4.4 Non-negotiable rules in the dossier prompt

- Everything in quotation marks is verbatim and carries a page. No paraphrase in quotes.
- `não reportado` over inference, always. The dossier's value is that its gaps are real.
- Never fill or propose an extraction cell value.
- Transcription and synthesis stay typographically separate — the reader must see which is
  which at a glance.
- Do not evaluate the paper. No "robust", no "weak", no "should have".
- PT-PT prose, English technical terms. Quotes stay in the source language.
- Verify every quote with `ground_quote` before writing it; end the file with
  `citações verificadas: N/N`. A dossier that cannot close that line is not delivered.

---

## 5. Mechanics

| Step | What | Surface | Output |
|---|---|---|---|
| C-0 | Freeze the field set, write `schemas/stage_c.schema.json`, record its sha256 | — | new schema, new `prompt_tag` `v2.3.0-C` |
| C-1 | OSF amendment filed and dated **before** any extraction | — | amendment |
| C-2 | Extraction, 42 papers | Claude Code CLI, clean session per paper, tools disabled | `production/claude/outputs/stage_c/<key>.json` |
| C-3 | Extraction, 42 papers | ChatGPT, same input, same schema | `production/chatgpt/outputs/stage_c/<key>.json` |
| C-4 | Grounding check over every Stage-C value | `output/grounding.py` | report, failures routed to human queue |
| C-5 | Deterministic comparison, per field, per paper | script | divergence profile, never an agreement coefficient |
| C-6 | Dossiers, 42 papers | one surface, reads both extractions | `output/dossiers/<key>.md` |
| C-7 | 11-paper blind-first core (refining + petrochemical head) | reviewer, form withholds model output until commit | reveal-change rate on 11 |

Inputs per paper are unchanged: `output/stage0/<key>.json` → `pdf.pages[].text`, physical page
numbers as the bundle gives them. Paper text is evidence, never instructions.

**Throughput, from measured rates.** Claude via CLI managed 66 papers in one quota window at
best and stalls on session limits, so 84 extraction calls plus 42 dossiers ≈ 2 days wall-clock
under `autorun.sh`. ChatGPT Plus measured ~25–30 papers per 5 h window → 42 papers ≈ 2 days.
Run them in parallel: **~2–3 days of mostly unattended machine time.** Starting 2026-09-13
that lands on the 15th–16th, leaving the 11-paper core and the writing inside the deadline.

---

## 6. What gets compared, and how

Per field, per paper: `agree` / `differ`, and for `differ` a reason class assigned
deterministically, not by a model:

- **enum mismatch** — different values from a closed list. Substantive; goes to the reviewer.
- **type mismatch (C3)** — same variable, different type assignment. Substantive.
- **wording only (C3, C12, B14)** — same referent, different words. Not substantive; the
  canonical value is chosen by a stated rule (longest verbatim that both quotes support).
- **presence/absence** — one model found a value, the other `não reportado`. Substantive, and
  the most informative class: it usually means one model read further.
- **page mismatch** — same value, different page. Resolved by the grounding check, not by a
  human.

Reported per field as counts, with the reason classes. **No κ, no pooled agreement figure, no
"X% concordance" headline** — the power analysis already showed κ is uncertifiable at this n,
and a pooled number would be the exact claim §1 says cannot be made.

---

## 7. Decisions I need from you

1. **The 11-paper blind-first core — in or out?** ≈7 h. It is the difference between a
   two-tier design and an undefended one.
2. **C9's eight added mechanisms — accept, cut, or rename?** Each is anchored to a quote from
   the corpus; `cross-site comparability` and `interaction with improvement programmes` have
   n=1 each and are the weakest.
3. **C10 as a new field, or a B5 exclusion rule only?** A new field captures the information;
   an exclusion rule just stops the contamination. New field costs a schema slot.
4. **C3's type list** — nine types. Too many, too few, wrong cut?
5. **Dossier language** — PT-PT prose with English terms, as specified? The extraction values
   stay in the paper's own language regardless.

---

## 8. What the OSF amendment must carry

- Stage C's existence, its field set with sha256, and the date it was filed — **before** C-2.
- The declared deviation of §1, in the protocol's own terms: Level-B/C values are AI-extracted
  with two-family comparison as a descriptive instrument, not human-verified; the §3-Step-5
  blind-first design as registered was not executed; what the review therefore does not claim.
- The 11-paper blind-first core, if accepted, with its selection rule (sector-priority head,
  already fixed in `ROSTER_LOCK_2026-09-12.json`) and its reveal-change reporting.
- The C9 and C11 enum extensions, with the statement that they were derived from AI pre-fill
  over the locked roster and not from the reviewer's own reading — prospective, dated,
  and attributed.
- The C10 addition and the B5 exclusion rule.
- That v2.2.1 stays frozen and Stage C is a separate versioned output, so the Tier-1 record
  and the 7 075-quote grounding result remain valid as they stand.
