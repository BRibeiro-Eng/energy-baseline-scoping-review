# Result → fields → human verification

**Status:** decided before the pilot, as required. Closes the open item carried from the
2026-09-12 review. Written against schema **v2.3.0-C** (`stage_c/SCHEMA_SHA256.txt`) and
Validation Protocol **C-2.3**.

**What this document is for.** Measuring minutes per paper in the pilot is meaningless until it
is fixed *what the reviewer actually does* to each field, and that depends on which claim the
field feeds. A claim of the form "*n* of 42 papers report X" cannot be verified by checking the
quotes the model produced, because a quote check cannot find what the model missed. A claim of
the form "the corpus contains papers that report X, here they are" can. The two cost different
amounts per paper, and they are different claims. The matrix below assigns every intended result
of Chapter 2 to one of them, before any of them is measured.

---

## 1. Verification vocabulary

| Level | What the reviewer does | What it can establish | What it cannot |
|---|---|---|---|
| **V0** | nothing; the AI value stands | nothing | everything |
| **V1 — grounding check** | open the cited page, read the quote, confirm it exists, is correctly located, and supports the recorded value (G1–G3) | that a recorded value is not fabricated and is not a mis-read | that nothing was missed; any denominator |
| **V2 — field verification** | read the paper's relevant sections for that field and confirm both the recorded value **and** that the field holds nothing else in those sections | a value, and an absence **within the sections read** | an absence elsewhere in the paper |
| **V3 — blind-first extraction** | extract the field from the full text without seeing any model output, commit, then reveal both | a value and a whole-paper absence; the only level that yields a defensible denominator | nothing further, within one reviewer's limits |

G3 — *does the quote support the value* — is not machine-checkable. Every V1 is therefore a human
act, not a script run. The script (`output/stage_c_grounding.py`) decides G1 and G2 and routes
the rest; it never certifies G3.

V1 presupposes that there is a cited page to open. As of 2026-09-12 the schema requires
`evidence_quote` and `page` on **every** object that carries a finding, `C5_measurement` entries
and individual metrics included: those keys were optional, and omitting them made the object
invisible to the grounding walk, so a metering claim could carry no evidence at all and still
validate. R10 had no V1 instrument until that was closed.

Three acceptance classes are **routings, not failures**: `interleaved` (words in order with
insertions, consistent with two-column extraction), `line-number ambiguity` (the quote matches
only if a figure at its own edge is deleted as line numbering) and `locator corrected` (the
sentence exists word for word on exactly one page, and it is not the page cited — see protocol
§9). All three produce a record with a review queue rather than a quarantine, because a human
reading is exactly what they need. `negation mismatch` and `not found` stay blocking.

A **corrected locator is not a verified cell.** It satisfies G1 and fails G2, so it enters V1's
queue with its work already half done: the reviewer opens the corrected page, finds the sentence
there, and judges G3. The corrected count is reported per paper beside the exact count; a result
whose evidence is mostly corrected locators is reported with that number visible.

**The rule that governs the whole matrix.** A **denominator** claim ("*n* of 42", "two thirds
of", "absent from the corpus") requires **V3** on every paper in the denominator. An
**existential** claim ("the corpus contains *n* papers that state X; here they are") requires
**V1** on the papers claimed and nothing on the rest. A **distributional** claim over Corpus A
is a Tier-3 instrument and is governed by §4a of the protocol, not by this matrix.

---

## 2. B1–B14 → Stage C correspondence

The frozen v2.2.1 instrument (Protocol §6.2) still exists and still holds the pre-fill that the
re-extraction replaces. The correspondence is recorded so the chapter can say which figures come
from which instrument, and so no v2.2.1 number is silently re-labelled as a v2.3.0-C number.

| v2.2.1 | Stage C successor | Relationship | Note |
|---|---|---|---|
| B1 `normalisation_variables` | `C3_variables[]` (`verbatim` + `type` + `role`) | **split** | the 237 B1 divergences were granularity, not substance. `role` is what removes them: the same variable can be predictor in a regression and denominator in a ratio |
| B2a/B2b `baseline_period_*` | `baseline_period_start` / `_end` | direct | envelope added (quote, page, support_class) |
| B2c `baseline_construction_method` | `baseline_construction_method` + `C2_model_form` | **split** | the free text stays; the codeable part moves to `model_family` × `estimation_method` × `variable_selection` |
| B3 `validation_types` | `C8_metrics.out_of_sample_validation.validation_design` + the three metric blocks | **replaced** | B3 conflated *what was tested* with *how well*. A training R² is no longer a "validation type" |
| B4 `scale_of_application` | `applications[].scale_of_application` | direct | moved to application level: one paper may hold several |
| B4b `scope_description` | `applications[].scope_description` | direct | — |
| B5 `identifies_model_limitations` | derived: `len(mechanisms) > 0` | **replaced** | B5 was a boolean that caught study limitations as model limitations (claude 19/32 vs chatgpt 30/41). It is not re-extracted; it is computed, and only from occurrences that survive `claim_status` |
| B6 `specific_limitations` | `mechanisms[].mechanism_cause` × `mechanism_effect_on_model` | **split and extended** | 45 of 49 B6 records coded `other`. Cause and effect were competing for one slot; the enum is now two axes, 11 × 13 values |
| B7 `proposes_treatment_mechanism` | derived: any `adaptations[].status == "proposed"` | **replaced** | a boolean over a list the instrument now holds explicitly |
| B8 `proposes_adaptations` | derived: `len(adaptations) > 0` | **replaced** | same |
| B9 `adaptation_types` | `adaptations[].adaptation` (11 values) + `status` + `addresses_mechanism` | direct + extended | `status` separates proposed from implemented from evaluated; `addresses_mechanism` is recorded only when the paper states the link |
| B10 `normative_framing_of_adaptations` | `adaptations[].normative_framing` | direct | per adaptation, not per paper |
| B11 `empirical_refinery_application` | `applications[].refinery_or_petrochemical_case` | **replaced** | the boolean could not distinguish "applied at a refinery" from "refineries mentioned". Five values now; the empirical qualifier is explicit |
| B12 `data_type` | `C4_data.data_type` + `acquisition_frequency` + `modelling_frequency` | **split** | hourly data aggregated to monthly regression points is two answers |
| B13a `model_parameters_reported` | `model_parameters_reported` | direct | — |
| B13b `performance_metrics_reported` | `C8_metrics` three blocks, each `status` + `metrics[]` | **split** | empty was ambiguous for 7 of 31. `status` separates *not reported* from *not applicable*, so "fitted but unreported" is distinguishable from "nothing to report" — and the validator now requires the two to agree: `reported` with an empty array is rejected, as is a non-reported status with metrics recorded. Without that rule the third case ("reported, but no number written down") simply recreated the ambiguity |
| B14 `implementation_barriers` | `implementation_barriers[]` | direct | free text on both instruments; never machine-paired |
| — | `C5_measurement`, `C6_re_estimation`, `C7_validity_envelope`, `C10_study_limitations`, `C12_data_requirements`, `C13_reproducibility`, `sector_registered`, `absence_declarations` | **new** | the three things no v2.2.1 field captured: what is on the left-hand side, whether the energy quantity is metered at the studied boundary, and whether the baseline is ever rebuilt |

**No v2.2.1 field is deleted from the record.** The frozen instrument and its pre-fill stay on
disk; v2.3.0-C is a separate record type with its own `prompt_tag`. Where the chapter reports a
v2.2.1 figure (the four measured failures above, which are *about* the instrument) it is labelled
as such.

---

## 3. The matrix

Pillars are those of `PILLARS_PROPOSAL_2026-09-11.md` (Layer A over Corpus A, n = 331; Layer B
over Corpus B, n = 42, plus 13 declared exploratory cases held out).

### Layer B — Corpus B (n = 42), SQ2–SQ4

| # | Intended result | Claim type | Stage C fields | Minimum level | Tier | Why that level |
|---|---|---|---|---|---|---|
| **R1** | continuous-process papers do report model-breaking mechanisms; these are the mechanisms and this is their shape | existential | `mechanisms[]` (`cause`, `effect_on_model`, `claim_status`, `refers_to`, quote, page) | **V1** on every occurrence claimed | core 11 at V3, other 31 at V1 | each occurrence is its own evidence; a reader can check any one of them |
| **R2** | *n* of 42 papers report a mechanism of class X | denominator | same, counted per paper per category after de-duplication | **V3** on all 42 | not available under the proposed coverage | a missed occurrence changes *n*; quote-checking what was found cannot find it |
| **R3** | fouling and catalyst deactivation are **absent** from the corpus | denominator (absence) | `mechanisms[].mechanism_cause`, plus `absence_declarations.mechanisms` | **V3** on all 42 | not available; reportable as V2 over the sections read, declared as such | an absence claim is the strongest denominator claim there is |
| **R4** | the mechanisms reported are not the ones the thesis predicted; observability, allocation and baseline drift dominate | comparative, rank-only | `mechanism_effect_on_model` frequencies | **V1** on the occurrences of the classes compared, for a rank claim; **V3** for a proportion | core 11 at V3, other 31 at V1 | a rank order survives a few missed occurrences; a percentage does not |
| **R5** | a `general` claim is not a finding: *n* occurrences are textbook statements, not results of the study | existential | `mechanisms[].claim_status` | **V1** on every occurrence, both directions | all 42 | this is the heteroscedasticity defect; it is the reason the field exists |

On the pilot sample, `claim_status` excluded **8 of 30** mechanism occurrences (27 %) from the SQ2
counting subset; under the v2.2.1 instrument all 30 would have counted. That is the size of the
correction this field makes, measured, on five papers — not a claim about the corpus.
| **R6** | adaptations recur (segmentation, dynamic re-baselining) and are normatively unanchored | existential + rank | `adaptations[].adaptation`, `.normative_framing`, `.status` | **V1** | core 11 at V3, other 31 at V1 | `normative_framing` and `status` are required fields and both are part of the comparator's key; they were absent from it, so "ISO 50001/50006 explicit" against "absent" on the same adaptation was reported as agreement |
| **R7** | two thirds of papers propose nothing | denominator | derived `len(adaptations) == 0` + `absence_declarations.adaptations` | **V3** on all 42 | not available | "proposes nothing" is an absence per paper |
| **R8** | adaptations are rarely linked by the paper to the mechanism they treat | existential, with a declared denominator caveat | `adaptations[].addresses_mechanism` (recorded only when stated) | **V1** | all 42 | the claim is about what papers *state*, and a stated link is positive evidence. The field is in the comparator's key: a link present on one surface and absent on the other is now a divergence, which is what this result is made of |
| **R9** | implementation barriers are stable across sectors and are organisational and instrumental before methodological | existential, qualitative | `implementation_barriers[]`, `applications[].sector_registered` | **V1** + reviewer's own reading | core 11 at V3, other 31 at V1 | free text; never machine-paired, so the synthesis is interpretive by construction |
| **R10** | the energy quantity is frequently **not** metered at the studied boundary | denominator | `C5_measurement[].data_origin` × `boundary_correspondence`, each entry with its own quote, page and `support_class` | **V3** on all 42 | core 11 at V3; the 31 reportable at V2 with the sections read declared | this is the field the Sines case is read against — it carries the most weight per unit of evidence. `C5_measurement` now requires at least one entry per model, so "silent on metering" is recorded as `not reported` with an `absence_basis` instead of as an empty array indistinguishable from "not searched" |
| **R11** | baselines are seldom rebuilt, and silence is not a statement that they are not | existential + absence discipline | `C6_re_estimation.regime`, `.update_status` | **V1** for stated regimes; **V2** for the `not stated` share | all 42 | the whole point is that silence ≠ "never rebuilt" |
| **R12** | validity envelopes are rarely stated, and almost never numerically | denominator | `C7_validity_envelope.statement` (3 values) | **V3** on all 42 | core 11 at V3; the 31 at V2 | a three-valued field over a fixed denominator |
| **R13** | out-of-sample validation is rare; what is reported is in-sample fit | denominator | `C8_metrics` three blocks, `status` per block + `validation_design` | **V3** on all 42 | core 11 at V3; the 31 at V2 | `status: not reported` vs `not applicable` is exactly the B13b failure being repaired |
| **R14** | reproducibility elements are partially reported; no index is computed | existential, per element | `C13_reproducibility` (4 items, 4 values) | **V1** | all 42 | four small closed fields; cheap, and no composite is claimed |
| ~~**R15**~~ **CORTADO 2026-09-16** | ~~transferability conditions reported for refinery contexts (SQ4)~~ — withdrawn for hours; see protocol §9. The 11 are 11 ordinary records among 41 and the blind-first option was spent. |

### Layer A — Corpus A (n = 331), SQ1

| # | Intended result | Claim type | Fields | Level | Tier |
|---|---|---|---|---|---|
| **R16** | the dominant indicator is an unfitted ratio; fitted baselines are a minority | distributional | A11, A11b (v2.2.1 Level-A) | protocol §4a: divergences adjudicated + SRS n = 40 on the concordant set, exact per-field CIs | Tier 3, unchanged |
| **R17** | ISO 50001 is near-universal as a citation; ISO 50006 and the M&V protocols are not | distributional | A10a, A10b, A10c | as R16 | Tier 3, unchanged |
| **R18** | the evidence base is single-case, facility-scale, geographically concentrated; methodological work is a small share | distributional | A1b, A1c, A9, A7, A5, A3 | as R16 | Tier 3, unchanged |

Layer A is **not** re-extracted. Stage C does not touch it, and its claims rest on the Tier-3
instrument already registered. Nothing in this matrix changes what Chapter 2 may say about SQ1.

---

## 3b. One extraction surface, and what routes the reviewer

**Reviewer decision, 2026-09-12.** Stage C extracts on **one** surface. The second model family
reviews the instrument, the records and the documents; it does not extract. Tiers 1 and 3 already
ran dual and are unaffected.

No level in §1 changes, because none of them was ever satisfied by agreement: V1 is a human
opening a page, V2 a human reading sections, V3 a human extracting blind. `provisional — model
agreement only` simply stops occurring as a state — there is no second surface to agree with, so
an unverified cell is now plainly *unverified* rather than provisionally agreed. That is a
clarification of the record, not a loss.

What the second surface was actually doing for this tier was **triage**: the divergence set told
the reviewer which cells to open. Its replacement is the record's own declarations of weakness,
implemented in `output/stage_c_triage.py` and mapped cell-by-cell to the results below:

| Priority | Cell | Reviewer action |
|---|---|---|
| **P0** | the grounding check routed it — interleaved, line-number ambiguity, locator corrected | read it; the instrument asked for a human |
| **P1** | a result depends on it **and** it declares itself weak: `requires inference`, `claim_status: general`, an `other` enum with verbatim, a corrected locator | read it |
| **P2** | a result depends on it **and** it is an absence with a basis and no quote | read the sections; only reading confirms an absence |
| **P3** | a result depends on it, direct statement, exact quote | sample |
| **P4** | no registered result depends on it | no human time budgeted |

Measured on the five pilot papers: **171 of 723 cells to read (24 %), 130 to sample, 422 (58 %)
not result-bearing** — about 34 cells to read per paper. P1 reasons, in order: 32 `requires
inference`, 8 `claim_status general`, 18 `other` verbatims across three axes, 3 corrected
locators **that a result depends on** — the records carry 24 corrected locators in all, and 21 of
them sit on cells no registered result reads (see the decision owed in
`PILOT_RESULTS_2026-09-12.md`).

Stated plainly, because it cuts both ways: inter-model divergence would have flagged **fewer**
cells — two surfaces agree far more often than one surface hedges — but on a criterion that
shares model biases, so two models misreading a sentence identically is invisible to it. These
signals flag more, on a criterion about this extraction's own weakness, and each is declared in
the record rather than inferred. Neither is verification. The P3 sample is the only thing
standing between a confidently-wrong cell and an unexamined value, and its size is reported.

The field → result map in `stage_c_triage.py` is the executable form of §3 below. **Editing one
without the other is a defect**, and the script is what the worklist comes from.

---

## 4. Human coverage: registered vs proposed

| | Blind-first (V3) | AI pre-fill + verification | Source |
|---|---|---|---|
| **Registered** (§3-Step-5 size branch, `25 < \|B\| ≤ 60`) | **40** — priority head K = 25 + `n_sub = min(15, 42−25) = 15`, seed 44 | **2** | Protocol C-2.3 §3-Step-5, filed |
| **Proposed** (this design) | **11** — the refining/petrochemical head of `ROSTER_LOCK_2026-09-12.json` | **31** — verification of result-bearing fields, absences included | `STAGE_C_2026-09-12.md` §1 |

This is a **reduction in the registered human treatment of the thesis-central tier**, from 40
papers at V3 to 11. It is a protocol deviation and is filed as such in the OSF amendment, with
the reason (calendar) stated plainly rather than presented as a design improvement. Two
consequences follow and both are declared in §9 of the protocol and in the chapter:

1. **Every denominator claim over Corpus B loses its registered basis.** R2, R3, R7, R10, R12 and
   R13 are denominator claims. Under 11 + 31 they are reportable only as (a) V3 results over the
   11, with the 11 named and their sector composition given, or (b) V2 results over the 42 with
   the sections read declared. Neither is "*n* of 42".
2. **Roughly 70 % of the SQ2 mechanism evidence sits outside the 11.** The head is refining and
   petrochemicals; the mechanism evidence is concentrated in cement, glass, pulp & paper and
   steel. So the 11 do not rescue SQ2 — they are where SQ4 and the transferability argument are
   read properly, and nothing more. Any SQ2 figure drawn from the 11 alone is a figure about
   refining, not about the corpus.

If tier 2 does not fit before submission, the chapter reports the two tiers **separately** and
says so. The choice is not "11 papers or an indefensible design"; it is which conclusions are
claimed as verified.

---

## 5. What the pilot measured, and what is still yours to measure

The pilot ran on 2026-09-12: five papers, one surface, **5/5 valid**, results in
`PILOT_RESULTS_2026-09-12.md`. What it settled:

| Quantity | Measured |
|---|---|
| machine cost per paper | ~$1.5 and ~8 min per CLI attempt; a clean paper is one attempt. 42 papers ≈ $55, ≈ 6 h at two workers |
| cells per paper | 145 mean (723 over 5) |
| cells the reviewer must read | **34 per paper** (171 of 723), plus 26 to sample |
| cells no result depends on | 58 % — no human time budgeted for them |
| routing classes actually produced | 1 interleaved, 1 line-number ambiguity in 538 quotes. So the normalisation rules cost the reviewer almost nothing on real papers |
| grounding failures on the final records | 0 wrong page, 0 not found, 0 negation mismatch, 0 enum snaps |

What remains unmeasured, and **only you can measure it** — the minutes, per verification level,
not per paper:

| Measure on the five pilot records | Estimates |
|---|---|
| minutes to clear one **P0/P1** cell (open the cited page, judge whether the quote supports the value) | the 31-paper tier: 34 such cells per paper |
| minutes to run **V2** on one field family (C5, C7, C8, C6) for one paper | whether R10, R12, R13 are reportable at V2 over 42 |
| minutes to run **V3** on one paper, full text, form withheld before any model output is opened | the 11-paper core, and R15 |
| minutes to clear one **P2** absence | the absence discipline, which is the most expensive thing in the design |

A single "minutes per paper" figure still cannot be extrapolated to either tier, which is why the
worklist is priority-tagged rather than paper-tagged. `human_verification_times.tsv` in
`production/stage_c/pilot_support/` holds the blank slots; a blank duration is missing, not zero.

---

## 6. Instrument defects found by adversarial audit, 2026-09-12

The matrix above is written against the instrument **after** an independent adversarial audit of
the five fixes that preceded it. The audit reproduced, and the code now rejects:

- a quote pairing a year with another year's value, accepted as `exact` because the numbering
  detector read an ascending year column as line numbers and the stripping was applied to the
  quote as well as the page. The quote side is no longer stripped on an accepting attempt; a
  match that needs it is routed to a human;
- the same failure on a genuinely numbered page, where the quote's own leading figure — a year,
  a sample size — was deleted and therefore never verified;
- `20-\n30 %` normalising to `2030 %` through the frozen hyphenation rule, so a fabricated
  figure passed and the literally correct transcription failed. A hyphen between two digits is
  a range, closed before the frozen rule sees it;
- nine substantive disagreements reported as agreement by the comparator: occurrence
  multiplicity discarded, `normative_framing`, `addresses_mechanism` and `also_constrains_model`
  absent from the keys, a repeated C3 variable and a repeated C5 energy vector silently
  overwritten, a `support_class` flip invisible, and the same value grounded in two different
  sentences counted as agreement;
- five unevidenced assertions that validated: a C5 entry with no evidence keys at all, an
  unsearched empty C3 list, a `reported` metric block with no metrics, an `explicitly stated
  absent` with nothing quoted, and `other` with no verbatim on every enum except mechanisms and
  adaptations;
- five exception paths that aborted the whole 42-paper pass instead of quarantining one paper,
  including a schema-digest `SystemExit` escaping a worker thread past every handler.

Each is now an assertion in `stage_c/test_stage_c.py`, `stage_c/test_compare.py` or
`stage_c/test_runner.py` (109 assertions across the three, plus a 522-value satisfiability property in `stage_c/test_satisfiable.py` with its own self-test). The audit found no defect in the
enum-snapping path.

---

## 7. Cut order if the hours run out

> **Executed 2026-09-16, out of order.** R15 — registered here as the last to be cut — was cut
> first, and R5 was kept. Every earlier step removes a claim that the executed 11 + 31 coverage
> had already made unavailable, so none of them frees any hours; R15 was the only cut that did.
> Steps 1-4 below are still applied to what is claimed. The departure is recorded in §9 of the
> protocol rather than left to be inferred from what the chapter does not say.

Registered in advance, in this order. Each cut removes *claims*, never verification from a claim
that is still made.

1. Drop **R2, R7** (counts that need all 42 at V3). The underlying existential claims R1 and R6
   survive.
2. Report **R3** only as: "no occurrence of fouling or catalyst deactivation was found in the
   42 records extracted, in sections verified at V2; the corpus is not claimed to be free of
   them." An absence claim without V3 coverage is stated as a search result, not as a property
   of the literature.
3. Reduce **R10, R12, R13** from V3-over-42 to V2-over-42, declaring the sections read.
4. Reduce **R4** from proportions to rank order.
5. Last to be cut: **R5** (the `claim_status` separation) and **R15** (SQ4 over the 11). R5 is
   cheap and is the defect that motivated the re-extraction; R15 is the only result the core 11
   exist to support, and it is the one the refinery chapter depends on.

Nothing in this order trades honesty for coverage: each step narrows what is claimed and says so
in the chapter.
