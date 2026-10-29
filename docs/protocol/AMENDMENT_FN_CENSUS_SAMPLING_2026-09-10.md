> Translated from Portuguese for this release. Original: `AMENDMENT_FN_CENSUS_SAMPLING_2026-09-10.pt.md` (same folder), SHA-256 `a3d81f49a258756be2db79ce761c1216815f7715cbb62124a641b7c614ed32c8`. The original is the record; this translation is for reading.

---
date: 2026-09-10
type: protocol-amendment
status: NOT YET SUBMITTED (OSF) — needs a submission date before the report is produced
affects: VALIDATION_PROTOCOL_C.md §3-Step-4, §6a; PROTOCOL.md §12.5
---

# Amendment — the false-negative census becomes sampled triage

## What was registered

C-2.3 §3-Step-4 specifies a **census**: the union of the candidates produced by the detectors (a) model flags, (b) deterministic lexicon and (c) recall pass is **emptied** by the reviewer — each candidate gets a verdict with a justification, and the closure rule is a complete pass with no new candidates. The pre-registered cut order (C-2 §6) explicitly exempts censuses from any reduction.

## What happened

On 2026-09-10 the union had 177 candidates (125 Tier-hit-A, 52 Tier-hit-B), with detector (c) still running. 177 verdicts were recorded, all `not_fn`.

An audit of the files shows that **171 of those verdicts were issued without reading**:

- median of 2 seconds between consecutive decisions, including in Tier-hit-A, whose registered load is 10–12 minutes of full reading per paper;
- 166 of the 176 transitions under 10 seconds;
- 169 identical justifications (`"nao aplicável"`, "not applicable"), plus two equivalent empty variants.

The 171 were voided to `verdicts/_voided_20260910T1530/` (preserved, outside any calculation). Six verdicts with a substantive justification were kept.

Plain record of this finding: the result the instrument was producing — "complete census, zero confirmed false negatives" — would have been a false empirical statement in the report, the thesis and the OSF deposit. It is not a limitation to be declared; it is a fact that did not happen. Hence this amendment, and not a footnote.

## What changes

The exhaustive census is replaced by **triage by simple random sampling** over the same candidate frame:

| parameter | value |
|---|---|
| frame | 177 candidates (union of detectors a+b; (c) not yet integrated) |
| n | 40 |
| method | `random.Random(45).sample(sorted(frame), 40)` |
| seed | **45** (new; 42 form pilot, 43 validation, 44 SRS audit already in use) |
| drawn composition | 33 Tier-hit-A · 7 Tier-hit-B |
| coverage | 22.6 % of the frame |
| record | `output/fn_census/triage/SAMPLE.json` |

Effort estimate: ~6.2 h, against ~35 h for the census with the projected candidates of detector (c).

## How it is reported

The word "census" **may not** be attached to this result. The wording is:

> Triage by simple random sampling of the frame of false-negative candidates (n = 40, seed 45, 22.6 % of a frame of 177), with an observed false-negative rate of e/n and an exact 95 % Clopper–Pearson interval.

The denominator is that of the sample, never that of the frame. If the sample gives zero false negatives, the 95 % Clopper–Pearson upper bound for n = 40 is 8.8 % — that is what can be stated, not "there are no false negatives".

## What this costs, said explicitly

The closure rule of §3-Step-4 (zero new candidates in a complete pass) **can no longer be met**. The Corpus B roster is locked on an estimate of the false-negative rate instead of on its exclusion. The 137 candidates outside the sample remain unexamined, and that is the central limitation to declare for SQ2–4: any continuous-process paper among them remains unidentified.

## What remains mandatory

§6a is unchanged. Any false negative confirmed in the sample triggers expansion of the lexicon with that paper's sector vocabulary and a re-run of detector (b); three or more require a discussion with the supervisor about a sector re-screen before the roster is locked. With sampling, an FN in the sample also implies a rate that extrapolates to the frame, which makes the re-run more urgent, not less.

## Instrumentation added

`serve_triage.py` now records `dwell_seconds` per verdict — the interval between the paper being served and the decision being saved — and `progress.py` reports the median and the number of decisions under 30 seconds. The field is meant for the report: it is the verifiable evidence that the triage was executed, and it replaces trust in the statement that it was.

## Incomplete frame: the second stratum

The sample above was drawn with detector (c) still running (96/394 on 2026-09-10 15:30). When it finishes, it adds candidates to the frame — the projection from the first 96 is ~66 new ones, for a final frame of ~243.

The sample is **not** redrawn. The design becomes two strata with known weights:

| stratum | frame | n | how |
|---|--:|--:|---|
| I — candidates before detector (c) | 177 | 40 | already drawn, seed 45 |
| II — candidates added by detector (c) | to be determined | ⌈0.226 × N_II⌉ | seed 46, drawn after (c) closes |

The sampling fraction is the same in both strata (22.6 %), so the overall rate is the size-weighted mean of the strata and the interval is combined by the usual stratified-sampling methods. The rate is reported per stratum **and** overall; never the overall alone, because stratum II is what the lexicon had missed and its FN rate is, a priori, the higher of the two.

Practical consequence: triage of stratum I can start immediately and is not invalidated by what detector (c) brings.

## Status

Amendment **not submitted**. The submission date must be filled in and the deposit made before any report that uses these numbers.

---

# Design revision — risk stratification (2026-09-10, 16:00)

The simple random sampling described above (n = 40, seed 45) **is replaced** before any execution by a design that covers the same human effort better. The seed-45 draw is recorded in `SAMPLE_superseded_seed45.json`; no paper was triaged under it.

## Fourth detector (automatic classification of the frame)

A **classification pass over all 177 candidates** is added to the three registered detectors, run by six Claude Opus agents on 2026-09-10, each with access to the lexicon excerpts and the full Stage-0 text. Role: detector, never adjudicator — the output is a ranked recommendation, and none enters a verdict file without a human decision.

Output (`CLASSIFIER.json`), by category:

| category | n | meaning |
|---|--:|---|
| `A_aplica` | 5 | evidence of an application in a sector of the closed list — strong FN candidate |
| `B_contexto` | 43 | continuous-process industry without a clear application, or an unlisted continuous sector |
| `C_mencao` | 55 | mention, context, literature review or list of sectors |
| `D_homonimo` | 74 | homonymy (`refining` of parameters, `steel` as a material, `ammonia` as a refrigerant) or bibliography |

**Verification:** of the 48 classifications that cite evidence, all 48 quotations were checked against the paper's own Stage-0 text with `grounding.py` — **zero failures**. The classifier did not fabricate evidence in any case.

## Human review design

| stratum | frame | reviewed | criterion |
|---|--:|--:|---|
| high risk (`A` + `B`) | 48 | **48** | in full, no sampling |
| low risk (`C` + `D`) | 129 | **25** | random, seed 46, 19.4 % |
| **total** | **177** | **73** | |

Advantage over SRS: the stratum where false negatives plausibly are is covered **in full** instead of at 22.6 %, for the same human effort (~73 papers). The control sample of the low-risk stratum exists for what SRS gives for free and this design does not — an estimate of the false-negative rate **that the classifier let through**.

## How it is reported

> Triage of the frame of false-negative candidates (n = 177) assisted by automatic classification with evidence checked against the source text. The high-risk stratum (n = 48) was reviewed in full by the reviewer; the low-risk stratum (n = 129) was randomly sampled (n = 25, seed 46, 19.4 %). The false-negative rate is reported per stratum, with an exact Clopper–Pearson interval in the sampled stratum.

It is still **not** a census, and the word is not used. What changed from the previous design is the efficiency of the allocation, not the nature of the claim.

**Reading rule for the control:** any false negative found among the 25 controls is a classifier failure and requires a full review of the low-risk stratum — the claim of targeted coverage no longer holds. Zero false negatives in 25 gives a 95 % Clopper–Pearson upper bound of 13.7 % for that stratum: that is what is written, not "the classifier did not fail".

## Instrumentation

The form shows the classifier's recommendation next to the excerpts and the PDF, with the quotation and its verification status. `dwell_seconds` is still recorded per decision: the design assumes reading, and the evidence that there was reading is that field.
