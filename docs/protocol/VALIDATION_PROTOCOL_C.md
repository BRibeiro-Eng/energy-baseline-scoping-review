# Validation Protocol C-2.3 — AI-Assisted Charting Quality Control

**Version:** C-2.3 (issued 2026-07-14; pre-sign-off operational clarification
2026-07-20 and contingency-rule correction 2026-07-21; supersedes
reviewer-approved C-2.2; **C-2.3 reviewer-approved and filed 2026-07-23**)
**What changed C-2.2 → C-2.3 (external review, all claims verified):** (1)
**execution order corrected** — membership-critical Tier-1 adjudication
(`methodological_eligibility`, `level_3b`) now PRECEDES the Corpus-B roster
lock (§7); the roster is named **initial-wave/provisional** until §16 closure;
(2) Tier-2 branch edge case closed: sub-sample = min(15, |B|−25); remainder
≤ 15 → integral blind-first (§3-Step-5); (3) overclaims removed ("validated
design"→pre-registered; "sole source of truth"→sole adjudicator of record;
Tier-1 row now names the provisional-accept class; FN-invisible-paper risk
probability → Unknown); (4) volumes updated everywhere to 220/459 and
~220–280; (5) upstream sample reports x/n_u; canary drawn from the end-of-run
proceeding corpus; (6) OSF draft: R/M set notation, clean trigger disjunction,
"procedure to be used", observable retrieval-differential phrasing, JBI
selection-vs-charting wording corrected.
(7) Operational execution aligned with the approved interactive design: one
clean Claude Code session and one clean Codex/ChatGPT session, article-level
subagents, deterministic file-backed batch state, default batch size 5, and no
model-invocation runner.
(8) Pre-production re-pilot clarifications (2026-07-20): authoritative storage
must be local and outside iCloud-managed roots; reviewer forms use atomic
autosave plus browser-local draft recovery; human evidence has separate quoted
and full-text-absence modes; Stage 4 resolves eligibility before dependent
fields and applies a narrow structural-not-applicable rule to ineligible
papers, while all eligible-paper divergences remain fail-closed.
(9) Pre-sign-off contingency-rule correction (2026-07-21): the earlier
overrun rules allowing scripted precedence for Tier-3 divergences and selective
`paper_type` adjudication were removed because they contradicted the registered
blind-first treatment of eligible-paper consequential disagreements. Beyond a
reduction of the Level-A audit from n=40 to n=30, further workload reduction
requires a dated deviation that omits named non-core descriptive outputs; it
does not silently replace human adjudication with model precedence.
(10) Reviewer sign-off and OSF filing (2026-07-23): the final C-2.3 text was
approved by Bernardo Ribeiro and its prospective amendment was deposited before
full-corpus production extraction in OSF project `wh62r` (file ID
`6a61e15518c36790cda322f4`; deposited PDF SHA-256
`15c140cdcc18f1f9d9c1dd7520d9ad96741cccafd654ad8b39fac64412ec2650`).
**Supersedes:** C-2.1 (2026-07-10), C-2.0 (2026-07-03) and C-1.0 (2026-06-25;
summarised in `REVIEW_ROUND2_C2.md`), which superseded the §13.2 pilot (hybrid
10+20) and the §12.5 audit design in `PROTOCOL.md`.
**What changed C-2.1 → C-2.2 (external methodological review, verified 2026-07-13):**
(1) **execution surfaces corrected** — extraction runs on consumer subscriptions
(Claude Code under a Claude Max plan; Codex CLI under a ChatGPT Plus plan), which
expose no sampling parameters, no dated model snapshots and no request IDs; all
"temperature 0" and "pin API snapshot IDs" requirements replaced by honest
surface-level provenance (§3-Step-1, §10, §12) — note the Opus 4.8 API itself no
longer accepts temperature/top_p/top_k either; (2) **two-stage corpus freeze** —
the 2026-07-10 freeze is the *initial database-retrieval freeze*; the *final
review corpus freeze* comes only after snowballing/supplementation closure
(PROTOCOL.md §16); (3) **audit frame corrected to cell-level semantics** — SRS
samples papers from the FULL concordant-eligible frame; census exclusions apply
per-cell, not per-paper (§4a; `audit_sampler.py` aligned); (4) all e_v/40
phrasings → e_v/n_v; the §6a trigger is an absolute e_v ≥ 3 with n_v reported;
(5) global "all Corpus-B blind-first" and "never cut" claims qualified by the
§3-Step-5 size branch; (6) "Acceptance thresholds" wording removed (control
rules only); (7) upstream audit fixed at n=50/seed 44 with explicit
small-frame rule and its ~5.8% zero-error bound stated (spot-check, not
closure); (8) test–retest/canary ranges fixed at n=30 with borderline-shortfall
fallback and exact flip denominators; (9) coverage taxonomy added (§4c): what
is adjudicated vs censused vs provisionally accepted vs sample-covered vs
residual; (10) census volume re-based on the post-rerun corpus (lexicon fires
on 220/459); (11) **open decisions moved to §13 and marked BLOCKING** — this
protocol is NOT ready for production until §13 closes.
**What changed C-2.0 → C-2.1 (external-audit corrections, 2026-07-10, all
claims verified against the repo before adoption):** (1) "Corpus-B membership
closed" language corrected everywhere — the census closes the *candidate
union*, not membership (residual risk stated in §9); (2) Corpus-B size
assumption corrected: the "4–15 papers" premise traced to a denominator
misread in the Round-1 red-team (3–4 per *10-paper pilot*, not per ~430);
observed probe prevalence is 1–2/10, PROTOCOL.md §15 estimated 25–30% — the
true size is UNKNOWN, so Tier-2 now carries a **pre-registered size-branch
rule** (§3-Step-5); (3) FN census workload re-based on the measured lexicon
firing rate (214/445 papers, verified) with a **tiered triage** inside the
census (§3-Step-4); (4) §4a audit re-specified with per-field denominators
e_v/n_v; (5) §6a triggers reframed as cost-based escalation rules, not
acceptance tests; (6) test–retest and canary given fixed n; (7) an upstream
**Level-1/2 exclusion audit** added (§3-Step-4b).
**Status:** C-2.3 was reviewer-approved and its prospective amendment was filed
on 2026-07-23, before full-corpus production extraction. Public record:
`https://osf.io/wh62r/files/osfstorage/6a61e15518c36790cda322f4`. The
deterministic implementation and seven-paper stored-fixture mini-repilot closed
green on 2026-07-14. The real interactive seven-paper re-pilot completed on
2026-07-20: both application workspaces and deterministic Stage 4 completed
green (7 records; locked Corpus B = 2; 0 unresolved fields; 0 cross-check
flags; 227 tests). A browser refresh had erased two completed but not durably
saved blind Level-B forms. Those blind values were not reconstructed from
memory; their final pilot values were recorded as explicitly **post-reveal,
non-blind adjudications** and are excluded from blind/reveal-change claims. The
incident led to atomic autosave, browser-local recovery and fail-closed
navigation/commit controls before production. The operational gate is therefore
closed **with this declared pilot deviation**; the affected episodes are not
presented as blind validation evidence. The §13 decisions are closed or
explicitly deferred.
Note the corpus state: the **initial database-retrieval freeze** (2026-07-10: 459 retrieved /
137 non-retrieved of 596) is done; the **final review corpus freeze** happens
only after snowballing/supplementation closure (PROTOCOL.md §16) — validation
of the initial corpus proceeds meanwhile, and snowballed/supplemented papers
enter the same pipeline afterwards.

---

## 0. Framing (read first — it changes how everything is reported)

This is a **pre-registered error-estimation / quality-control design for an AI-assisted
charting pipeline**. It is **not** a classical inter-rater reliability study and
**does not report Cohen's κ as its headline statistic.** That reframing is
deliberate and load-bearing: a power analysis (`power_analysis/POWER_ANALYSIS.md`)
proved that per-variable κ cannot be certified at any sample size a single reviewer
can sustain, especially for the rare, thesis-central variables (`level_3b`,
Level-B).

**The C-2 design principle: census where it counts, estimate only where it doesn't.**
The thesis-critical objects are enumerable — the false-negative candidate union
(measured lexicon firing rate: 220 of 459 available papers hit ≥1 term, so plan
for ~220–280 candidates after adding the other two detectors, handled by tiered
triage, §3-Step-4) and the consequential-field divergences (~100–150 units).
Those are covered by **exhaustible human censuses** — lists an examiner can
inspect row by row — not by estimators. **Corpus B's size is genuinely unknown**
(probe: 1–2 of 10 papers; PROTOCOL.md §15 once estimated 25–30% of eligible;
the earlier "4–15" figure traced to a denominator misread — see
`REVIEW_ROUND2_C2.md` addendum): Tier-2 treatment therefore branches on the
observed roster size (§3-Step-5). Statistical estimation is reserved for the
only non-enumerable population (the concordant Level-A bibliometric tail),
using the simplest design whose interval is valid by construction (simple
random sample + exact binomial CI, per-field denominators).

**Single-reviewer integrity (OSF) is preserved.** The AI does not act as a second
reviewer. Inter-model agreement is used **only as a routing signal** to direct human
attention; it is **never** treated as evidence of correctness. The human remains the
sole adjudicator of record (not an infallible ground truth — §9), and on the
consequential fields establishes the adjudicated values **blind-first**
(deciding from the source before seeing any model output).

**One-line defense:** *"Model agreement is routing, not reliability. Every paper
in a three-detector false-negative candidate union was human-verified with the
list emptied under a closure rule (residual risk outside the union is declared,
not claimed away); the branch-prescribed analytical head/subsample was
human-extracted blind-first, while any remainder beyond 40 papers received
AI pre-fill plus field-by-field human verification, under the corpus-size
branch declared before the roster was known; disagreements were adjudicated
blind-first; and the bibliometric tail carries a per-field error bound from a
simple random audit with exact intervals — with pre-registered escalation rules
that say in advance what error rate triggers what action."*

---

## 1. Principles

1. **Agreement = routing, not truth.** Concordance only decides where the human
   looks; it never certifies a value.
2. **Census where it counts.** Enumerable thesis-critical sets — the
   registered false-negative candidate union, membership-critical divergences,
   and consequential-field divergences — are exhausted by the human, not
   sampled. Residual membership risk outside the candidate union remains
   declared rather than claimed closed.
3. **Blind-first where it matters — including Tier 2.** Consequential-field
   disagreements are always adjudicated from the PDF *before* seeing model
   outputs; Corpus-B analytical extraction is blind-first for the whole roster
   through |B|=40 and for the pre-registered head/subsample above 40. Any
   AI-prefilled verification remainder is explicitly non-blind and reported
   separately, with the size branch declared before the roster is known.
4. **Estimate only the un-enumerable, with valid intervals.** SRS + exact CI on the
   bibliometric tail; per-field raw counts, never pooled, no agreement coefficients.
5. **Thresholds before data.** Escalation triggers (cost-based control rules —
   never acceptance tests) and the overrun cut order are pre-registered in the
   OSF amendment — QC with control limits, not monitoring.
6. **Everything is deposited.** Raw model outputs + all census/adjudication logs are
   the reproducible object, not the live (non-deterministic) pipeline.

---

## 2. Field tiering (concentrates human effort by consequence)

| Tier | Fields | Validation regime (C-2) |
|---|---|---|
| **Tier 1 — Consequential** | `methodological_eligibility`, `level_3b`, `paper_type`, `borderline_review_synthesis_eligibility` | All divergences **blind-first** adjudicated (census, §3-Step-3); concordant **3B/borderline** cells censused exhaustively (§4b); concordant eligible-non-3B Tier-1 cells are **provisionally accepted** (§4c class 3 — no individual human eyes); Corpus-B false-negative risk attacked by the **FN candidate-union census** (§3-Step-4 — union emptied; residual risk outside the union declared in §9) |
| **Tier 2 — Analytical (Corpus B)** | all Level-B fields | **Pre-registered §3-Step-5 size branch:** all papers blind-first if \|B\| ≤ 25; if 25 < \|B\| ≤ 60, a priority head of 25 plus a random blind-first sub-sample `n_sub = min(15, \|B\|−25)`, giving `25+n_sub = min(\|B\|,40)` blind-first papers. Thus the whole roster is blind-first through \|B\|=40; only papers beyond 40 receive AI pre-fill + human field-by-field verification. On blind-first papers the form withholds model outputs until commit, then reveals both as post-hoc discrepancy checkers; reveal-changes are logged. This *is* the SQ2–4 extraction, not overhead. |
| **Tier 3 — Bibliometric (Corpus A)** | Level-A descriptive fields | Divergences adjudicated (anchored OK, §3-Step-3b); concordant set → **SRS n=40 audit** with exact per-field CIs (§4a) |

> C-1.0 had Tier 2 as AI-pre-fill + human confirmation (anchored verification of the
> most important tier) — inverted in C-2 (confirmed defect 3): the strongest
> treatment now sits on the thesis-central data. In the small-\|B\| branch the
> inversion costs almost nothing net (integral human verification was already
> budgeted); in the larger branches the blind-first treatment covers the
> priority head + a measured sub-sample, and the pre-fill remainder carries a
> reported discrepancy rate instead of an unmeasured anchoring assumption.

> **Amendment note, 2026-09-12 — Tier 2 instrument replaced; coverage reduced.**
> Tier 2 above reads "all Level-B fields", meaning the frozen v2.2.1 fields B1–B14 of
> Protocol §6.2. Those fields are **no longer the Tier-2 instrument**. Four of them failed
> measurably on the 42-paper pre-fill (B6: 45 of 49 records coded `other`; B5 caught study
> limitations as model limitations; B1's granularity was unresolvable across surfaces, 237
> divergences; B13b could not distinguish "fitted but unreported" from "nothing to report"),
> and three things the synthesis needs were captured by no field at all. Tier 2 is now the
> Stage C instrument, schema **v2.3.0-C** (`stage_c/schema.json`, digest in
> `stage_c/SCHEMA_SHA256.txt`), described in `STAGE_C_2026-09-12.md`. The B1–B14 → Stage C
> correspondence, field by field, is in `RESULT_FIELD_VERIFICATION_MATRIX_2026-09-12.md` §2.
> B1–B14 and their pre-fill remain on disk and are not deleted; v2.3.0-C records carry their
> own `prompt_tag`, so no v2.2.1 figure is re-labelled as a v2.3.0-C figure.
>
> The **human coverage registered in §3-Step-5** for this branch — 40 blind-first + 2 pre-fill
> — is **not** what will be executed. The executed design is **11 blind-first** (the
> refining/petrochemical head of `ROSTER_LOCK_2026-09-12.json`) **+ 31 AI pre-fill with human
> verification of result-bearing fields, absences included**. This is a reduction of the
> registered treatment on the thesis-central tier, for calendar reasons, and is filed as a
> deviation in the OSF amendment. Its consequence is specific and is declared in §9: every
> **denominator** claim over Corpus B ("*n* of 42", "absent from the corpus", "two thirds
> propose nothing") loses its registered basis and is reported either over the 11, or over the
> 42 at the weaker verification level with the sections read declared. Roughly 70 % of the SQ2
> mechanism evidence sits outside the 11, so the head does not substitute for the roster.
> Which result may be claimed at which level is settled in advance, per result, in
> `RESULT_FIELD_VERIFICATION_MATRIX_2026-09-12.md` §3–§6, including the cut order if the hours
> run out.

> **Amendment note, 2026-09-12 (second) — Stage C extracts on ONE surface.**
> Reviewer decision. The second model family is no longer an extractor for Tier 2; it reviews
> the instrument, the records and the documents instead. **Tiers 1 and 3 already ran dual and
> are untouched** — the 82 Tier-1 membership adjudications, the §3-Step-3b Level-A divergence
> adjudications and the §4a SRS frame all stand as executed. The change is confined to Stage C.
>
> What this removes is **§3-Step-1/Step-2 for Stage C**: there is no second extraction to
> reconcile, so no (paper, field) cell can be called concordant or divergent, and no reveal
> against a second surface exists. No CLAIM is weakened by that, because §0 and the verification
> matrix never treated inter-model agreement as verification — only as `provisional — model
> agreement only`. What is lost is the **triage**: the divergence set was what told the reviewer
> which cells to read.
>
> The replacement is registered here and is implemented in `output/stage_c_triage.py`: the
> reviewer's worklist is built from the record's **own declarations of weakness** —
> `support_class: requires inference`, `claim_status: general`, an `other` enum with its
> verbatim, an absence with a basis and no quote, and any cell the grounding check routed
> (interleaved, line-number ambiguity, locator corrected). Each cell is mapped to the registered
> results it feeds (matrix §3) and assigned P0–P4; cells no result depends on get no human time.
> Measured on the five pilot papers: **171 of 723 cells to read (24 %), 130 to sample, 422
> (58 %) not result-bearing** — about 34 cells to read per paper.
>
> The honest comparison, stated rather than glossed: inter-model divergence would flag **fewer**
> cells, because two surfaces agree far more often than one surface hedges — but on a criterion
> that shares model biases, so two models reading a sentence the same wrong way is invisible to
> it. These signals flag more cells, on a criterion about this extraction's own weakness, and
> every one of them is declared in the record rather than inferred by the pipeline. Neither is
> verification; both are routing. The consequence for what may be claimed is in §9.
>
> `output/stage_c_compare.py` and its suite are **retained and not deleted** — they encode
> nine measured comparator defects and are ready if a second extraction surface is ever added —
> but they are out of the executed pipeline and produce nothing for this review.

---

## 3. Operational pipeline

**Step 1 — Dual extraction.** Two independent model families chart all available
papers against the frozen v2.2.1 schema with versioned prompts, running on
**consumer-subscription application surfaces** (reviewer decision, updated
2026-07-14): one clean Claude Code session and one clean Codex/ChatGPT session.
Each session acts as a thin orchestrator and dispatches one paper end-to-end per
article agent; the deterministic batch controller owns selection and state. No
model-invocation API/CLI runner is used. These surfaces provide no guaranteed
sampling controls, dated model snapshots or request IDs; run-to-run stability is
therefore measured empirically by the §3-Step-6 canary. Provenance recorded per
run: application version, model label exactly as displayed by the surface,
runtime configuration, run dates and per-paper timestamps. **Archive every raw
output** — the deposited outputs + logs are the reproducible object. *(No third-model arbiter: a third
correlated vendor adds census noise, not independence — red-team A5.
Irresolvable cases go to the human with a quote requirement, full stop.)*

**Operational storage invariant.** The authoritative project tree and both
execution packs live on a local filesystem outside the Desktop, Documents and
Mobile Documents roots, which are conservatively treated as potentially
iCloud-managed. Pack initialization and every controller entry point fail
closed on a prohibited path, an unreadable or dataless file, a
path escaping the canonical root, a content-hash mismatch or an invalid lock.
The two model workspaces contain the same frozen inputs, schemas and prompts;
their executor identity, run metadata, state and outputs remain separate.

**Step 2 — Field-level reconciliation.** Automatic comparison per field →
partition each (paper, field) into **concordant** or **divergent** (after
normalising format/enum-label differences, per the cross-model probe lessons).

**Step 2a — Structural applicability in Stage 4.** Consolidation resolves
`methodological_eligibility` first, using finalised human adjudication before
model concordance. If the resolved value is `false`, every Level-A field is
forced to `null` with provenance `structural_not_applicable`, because the
registered schema forbids Level-A charting for ineligible papers. A difference
between the two ancillary, non-analytical free-text `ineligibility_reason` narratives is not a
standalone blocker once ineligibility itself is resolved: Stage 4 selects the
first non-empty narrative in a fixed family order (ChatGPT, then Claude), marks
the source `model_narrative_precedence`, and retains both raw model envelopes in
provenance. No other mismatch is automatically collapsed. In particular, any
Tier-3 difference on an eligible paper remains unresolved until anchored human
adjudication.

**Human evidence contract.** Every targeted human decision records a rule or
rationale. Present/positive values use `quoted` evidence: a literal supporting
quote and positive physical page, verified against the PDF. Absence-like values
(`false`, `null`, empty lists or a registered absence label) may instead use
`not_reported_after_full_text_review`: no invented quote or page is permitted,
and the reviewer records the explicit full-text absence/applicability rationale.

**Step 3 — Blind-first adjudication of ALL Tier-1 divergences (census).** For each
Tier-1 field where the models differ, the reviewer extracts the value **from the
PDF with model outputs hidden**, records it, *then* reveals both models and
reconciles. Log per unit: blind decision, both model values, final value, evidence
under the human evidence contract, decision rule, borderline tag, and whether
the reveal changed the decision (→ the reveal-change rate is reported raw as
the anchoring-exposure figure).

**Step 3b — Anchored adjudication of Tier-3 divergences.** Bibliometric divergences
are resolved seeing model outputs (fast, batched in the Flask form; expect
~500–1,200 field conflicts at the probe's ~81% Level-A agreement — budget ~7 h, not
less). Anchoring is accepted on this tier because its end product is independently
measured by the §4a audit. Each anchored cell retains both model values, the
human final value, evidence under the human evidence contract, rule and
timestamp. *(C-1.0's 15% blind sub-sample here is deleted — it
measured anchoring where it is not load-bearing.)*

**Step 4 — False-negative candidate-union census (replaces capture–recapture).**
Build the candidate set as the **union of three detectors** with different failure
modes, over all papers outside Corpus B:
- **(a) Model flags:** either model says `level_3b=true`, or flags
  `borderline_review_synthesis_eligibility`, or types the organisation as a
  continuous-process sector;
- **(b) Deterministic lexicon:** full-text word-boundary match against the
  continuous-process term list (the canonical list lives in `output/fn_hunt.py`:
  refinery, refining, petrochemical, petroleum, cement, clinker, kiln, **pulp and
  paper, paper mill** (never the bare word "paper"), steel, blast furnace,
  steelmaking, ammonia, ethylene, olefin, sulfuric/sulphuric acid, chlor-alkali,
  industrial gases, air separation, glass furnace, glass melting, continuous
  process, steady-state);
- **(c) Counter-anchored recall pass:** one extra machine pass over the
  concordant-excluded set with a recall-tuned prompt ("assume NOT Corpus B unless
  explicit evidence; list any continuous-process signal").

Detector (c) fires on **any listed continuous-process signal** (the recall
direction), not on the model's final classification — the conservative framing
only disciplines the classification, the signal list is deliberately
over-inclusive.

The reviewer **empties the candidate list** — every candidate gets a human
accept/reject with evidence under the human evidence contract. **Measured volume (re-based
2026-07-13, post Stage-0 rerun):** the lexicon alone fires on **220 of 459**
available papers (219 proceeding; top terms by document count: steel 101,
cement 87, petroleum 49, pulp-and-paper 43, petrochemical 38), so the union
will plausibly hold **~220–280 candidates**, not the ~50–100 C-2.0 assumed.
The census therefore runs in **two triage tiers** (both logged, both part of
the census — nothing is dropped): **Tier-hit-A** (multi-word sector term,
sector metadata match, or any model/recall-pass flag) → full triage read
(~10–12 min); **Tier-hit-B** (only generic single terms: steel, steady-state,
continuous process, refining, petroleum) → 2-minute title/abstract/context
skim with a one-line logged justification; any doubt promotes to Tier-hit-A.
**Closure rule:** any confirmed FN adds that paper's sector vocabulary to the
lexicon and re-runs detector (b); the census closes only when a full pass
yields **zero new candidates**. Instead of estimating what the detectors
missed, the union is made broad and cheap enough for the human to exhaust it —
and what lies outside the union is a declared residual risk (§9), not a closed
question.

**Step 4b — Upstream Level-1/2 exclusion audit (added C-2.1; rule fixed C-2.2).**
The census above cannot recover papers wrongly excluded at title/abstract
screening (Levels 1–2), which C-2 otherwise never revisits. Fixed, reproducible
rule: (i) run the deterministic lexicon over the **titles + abstracts of all
326 records excluded in Rayyan**; every hit gets a 2-minute human re-check;
(ii) draw a **simple random sample of n = 50, seed 44, without replacement**,
from the 326 **minus** the lexicon hits; if that remainder holds fewer than 50
records, take all of it. Report **x/n_u** (n_u = 50, or the full remainder
size when it holds fewer) with a one-sided 95% upper bound — note
that even 0/50 leaves an upper bound of **~5.8%** on the sampled-frame miss
rate, so this instrument is a **spot-check of the upstream screen, not a
closure of upstream false negatives** (declared in §9). Cheap (metadata only,
~3–4 h). *(Considered alternative — reviewing all 326 integrally at ~2
min/record ≈ 11 h — buys frame-wide coverage at ~3× the cost; kept as an
escalation option if the sample or the lexicon hits surface any confirmed
upstream miss.)*

**Step 5 — Select the pre-registered size branch, complete model coverage,
then perform human Level-B extraction.** After the reviewer locks or
version-expands the Corpus-B roster, the branch is selected immediately from
the human-locked |B|. If |B| > 60, the pause/amendment/supervisor rule below
applies **before any Stage-3 supplement or human Level-B extraction**. In the
other branches, each model workspace deterministically identifies roster papers for
which its own frozen initial output lacks Stage 3. This occurs when that model
originally classified the paper `level_3b=false` but the human adjudicated it
into Corpus B. A Stage-3-only supplement is run for that model: it receives the
human roster decision only as a downstream routing fact, must not reconsider or
alter Stage 1/2, and is stored as a separate versioned output. The original
negative classification remains immutable in the Tier-1 error record. If the
supplement remains invalid after one repair, the paper is processed blind-first
without AI prefill and the missing model comparison is reported explicitly.

**Reviewer-form durability and blinding failure rule.** Every edit is copied
immediately to browser-local recovery storage and atomically autosaved to disk
after a short debounce; manual save, paper navigation, blind commit and
finalisation all flush the current state first. A newer local draft is restored
automatically after a refresh or application interruption. Navigation, reveal
and finalisation fail closed if the durable save fails, and the interface shows
whether the state is unsaved, saving, durably saved, recovered or failed. If a
blind form is nevertheless lost or exposed before durable commit, work stops
for that unit: the reviewer does not reconstruct a blind decision from memory.
Any later value is explicitly logged as post-reveal/non-blind, with the incident
reason and timestamp, and is excluded from blind discrepancy and reveal-change
denominators.

Once the applicable supplements terminate, the reviewer performs the Level-B
treatment prescribed by the selected branch. Corpus-B prevalence is unknown (probe: 1–2 of 10; PROTOCOL.md §15
once estimated 25–30%), so the treatment branches on the human-locked roster
size observed at census closure — **registered before the outcome is known**:

**Branch thresholds and rules CONFIRMED by the reviewer 2026-07-10:**

- **|B| ≤ 25:** integral blind-first extraction of every paper (the C-2.0
  design): all Level-B fields completed from the PDF with model outputs
  **withheld** by the form; reveal after commit; disagreements re-checked
  against the source (human value stands unless the re-check shows a clear
  miss); reveal-changes logged. (~20–25 h.)
- **25 < |B| ≤ 60:** blind-first extraction in **sector-priority order —
  refining first, then petrochemicals, then the remaining sectors, recency
  (2020+) as tiebreaker within each** — for a **fixed head of K = 25 papers**
  (D1 closed 2026-07-13), **plus a random blind-first sub-sample of
  n_sub = min(15, |B| − 25)** of the remainder (drawn seed 44, without
  replacement). **Edge case (C-2.3):** when the remainder holds 15 or fewer
  papers (26 ≤ |B| ≤ 40), it is reviewed blind-first **integrally** — the
  branch degenerates to integral blind-first for |B| ≤ 40. Total blind-first
  work in this branch is **25 + n_sub = min(|B|, 40)**. The sub-sample
  discrepancy rate is reported as **x/n_sub**. When `n_sub = 15`, 0/15 leaves
  a one-sided 95% upper bound of **~18.1%**; for a smaller `n_sub`, the exact
  bound for that observed denominator is reported instead. The sub-sample is
  interpreted descriptively and is **never used to certify the AI-prefilled,
  human-verified remainder**. Only papers beyond the first 40 receive AI
  pre-fill + human field-by-field verification. (~35–55 h across the branch.)
- **|B| > 60:** extraction **pauses before Level-B work begins**. A dated
  amendment note is filed and supervisor scope is recorded; only then does
  extraction resume. The SQ2–4 **deep narrative synthesis is
  restricted to the sector-priority head of the roster** (refining +
  petrochemicals + as far down the priority order as the budget reaches),
  with the remaining papers reported descriptively (counts, sectors, model
  families).

In every branch this is the analytical extraction the thesis needs anyway; the
AI serves only as a post-hoc discrepancy checker on blind-first papers.

**Step 6 — Measurement instruments.**
- **Corpus-wide grounding check** (replaces the contamination probe): every
  AI-extracted value in the production dataset must carry a verbatim supporting
  quote that string-matches the PDF text after the full §6.3 8-rule
  normalisation (`output/grounding.py`, Stage-4 §12.2). Failures are auto-routed
  to the human queue and logged with enough context to surface systematic
  encoding patterns (§6.3 extension trigger). A quote verified against the
  actual PDF defeats fabrication regardless of whether the model "remembered"
  the paper. **Declared limit:** the string match proves textual traceability,
  not that the quote semantically supports the extracted value — semantic
  support is covered by the human instruments (blind-first Tiers 1–2, §4a
  audit on Tier 3).
- **Determinism canary (fixed n = 30):** re-run 30 papers (SRS, seed 44, drawn
  from the proceeding corpus **as it stands at end-of-run** — 448 at the
  initial-retrieval freeze, grown by any §16 additions) through
  both surfaces at end-of-run, attempting to hold **application version,
  displayed model label, runtime configuration, and prompts** fixed.
  **Flip** = any field whose normalised value (reconcile.py rules) differs
  between the two runs of the same model. **Denominator** = fields evaluable
  in both runs of that model; fields non-evaluable in either run are excluded
  from the denominator and their count reported. Report the field-level flip
  rate per model; **any Tier-1 flip triggers human review of that paper
  regardless of the overall rate**. The canary measures **run-to-run
  instability under a fixed configuration only**. If the application version
  or displayed model label changes, retain and report the rerun but mark it
  **configuration-non-comparable** rather than presenting it as a fixed-
  configuration canary. Silent provider-side changes remain a declared risk.
- **Test–retest (human self-consistency, fixed n = 30):** ≥2 weeks after
  adjudication, re-decide 30 of the reviewer's own consequential-field
  decisions from the PDF alone (originals and model outputs hidden): 20 drawn
  from borderline-tagged decisions and 10 from the remainder (seed 44, without
  replacement); **if fewer than 20 borderline-tagged decisions exist, take all
  of them and fill to 30 from the remainder**. Report the raw flip count with
  dates. This replaces C-1.0's hard-coded "residual error ≈ 0 on
  human-adjudicated units" with a measurement (interpret descriptively — it
  measures self-consistency, not accuracy; the single-reviewer ceiling is
  declared, not solved).

---

## 4. Audit design (one binding rule; censuses and sample kept separate)

### 4a. SRS audit of the concordant Level-A tail — the ONLY sampled instrument
- **Population target:** concordant, evaluable Level-A **cells** (paper × field)
  not covered by a census instrument.
- **Sampling unit = paper; error unit = cell.** **Simple random sample, n = 40
  papers** (seed 44) drawn from **ALL eligible papers with reconciled Level-A
  data — including papers whose consequential cells are censused** (a 3B or
  borderline paper's *other* Level-A fields still need audit coverage; C-2.1
  wrongly excluded whole papers from the frame — corrected here and in
  `audit_sampler.py`). All Level-A fields of each sampled paper are blind
  re-extracted by the reviewer, then diffed. No strata, no weights — SRS makes
  the plain per-field binomial interval valid by construction.
- **Per-field denominators:** for field *v*, **n_v** counts the sampled cells
  that are (i) concordant between the models, (ii) evaluable (field applicable
  to that paper), and (iii) not individually covered by a census instrument;
  divergent cells are excluded from n_v (they are adjudicated via §3-Step-3/3b,
  not audited). Report **e_v/n_v with n_v stated, never e_v/40**.
- **Error definitions (pre-specified per field type):** enum/bool — normalised
  values differ (reconcile.py rules); multi-select — set difference after
  normalisation (any element added/missing = 1 field error); free text —
  substantive-content disagreement as judged blind (logged with justification);
  null vs value — error unless the PDF genuinely lacks the datum;
  `not applicable` vs null — error (they are schema-distinct).
- **Metric:** per field, the raw error count with an **exact Clopper–Pearson
  95% CI** on e_v/n_v. Zero errors on a field with n_v = 40 still reports a
  **one-sided** 95% upper bound of ~7.2% (rule of three; the two-sided CP upper
  is ~8.8% — both stated so no reader mistakes one for the other). The binomial
  CP interval is **conservative for the finite frame** (sampling without
  replacement); it is reported as a probabilistic bound, not a deterministic
  cap on unobserved errors. All per-field 95% intervals are **marginal per
  field** — they do not provide simultaneous coverage across the field set.
  **Never pooled across fields, no agreement coefficients.**
- *(C-1.0's stratified design + pooled Wilson CI + Gwet AC1 + the three coexisting
  sizing rules are deleted — confirmed defects 1 and 4. The strata existed to catch
  rare cells; those are now censused exhaustively instead.)*

### 4b. Exhaustive censuses of the rare consequential cells (not sampled, not pooled)
- **Concordant `level_3b=true`:** all papers, every one human-verified.
- **Concordant-excluded keyword/detector hits:** all — this is the §3-Step-4 census.
- **Concordant `borderline_review_synthesis_eligibility=true`:** all.
Census results are reported as complete enumerations (counts + per-paper verdicts
with quotes), separately from the §4a sample — never merged into a rate.

### 4c. Coverage taxonomy — what is and is not covered (do not overstate)

Every (paper, field) decision in the pipeline falls into exactly one class;
reports must use these terms and never blur them:

1. **Individually human-adjudicated:** all Tier-1 inter-model divergences
   (blind-first, §3-Step-3); Tier-3 divergences (anchored, §3-Step-3b);
   FN-census candidate verdicts (§3-Step-4); blind-first Tier-2 cells per the
   active branch (§3-Step-5).
2. **Censused (exhaustively enumerated):** concordant `level_3b=true` papers'
   consequential cells; concordant `borderline=true` papers' consequential
   cells; the FN candidate union; the upstream lexicon hits (§3-Step-4b·i).
3. **Provisionally accepted (no individual human eyes):** concordant, eligible,
   non-3B papers' Tier-1 cells — accepted under PROTOCOL.md §9 routing and
   covered only by the instruments below. **It is therefore FALSE to claim
   that "all full-text decisions are human-adjudicated"; do not claim it.**
4. **Sample-covered:** the concordant Level-A tail (§4a SRS, marginal
   per-field bounds); the upstream non-hit exclusions (§3-Step-4b·ii, n=50
   spot-check); the pre-fill Tier-2 remainder's discrepancy rate (n=15
   sub-sample, larger branches).
5. **Declared residual (uncovered):** papers invisible to all three FN
   detectors; upstream misses outside the lexicon hits and the n=50 sample;
   un-audited concordant Level-A cells beyond their probabilistic bounds;
   whatever the ~137 non-retrieved and any not-yet-snowballed literature
   contain (§9).

---

## 5. Metrics (what gets computed and reported — separately, never composited)

Report **per field / per instrument**, never a single summed number:

1. **Divergence rate** D_v/N_v per field (routing volume; descriptive).
2. **Reveal-change rate** on blind-first units (anchoring-exposure figure, raw count).
3. **Concordant Level-A error rate per field:** e_v/n_v with exact
   Clopper–Pearson 95% CI (§4a; n_v stated per field), plus the count of
   un-audited concordant cells per field so the reader sees what the bound
   covers. The un-audited tail carries a **probabilistic, marginal per-field
   bound** (the CI upper limit under the binomial model) — not a deterministic
   cap — and no composite "residual error" multiplication is performed.
4. **Census outcomes:** FN-census candidate count, confirmed FNs (papers pulled
   INTO Corpus B), closure-pass count; papers that entered/left Corpus B after
   validation (the SQ2–4-critical figure).
5. **Tier-2 discrepancy table:** human-vs-AI disagreement count per Level-B field
   (descriptive; human value is the datum).
6. **Grounding-check pass rate** (corpus-wide) + enumerated failures and their
   resolutions.
7. **Determinism-canary flip rate**; **test–retest flip count** (x/n, dates).

*(C-1.0's composite R̂_v = p̂·(C−a)/N with propagated CI, the capture–recapture
estimator, and Gwet's AC1 are deleted: the composite summed a bias-dominated and a
noise-dominated term into a number that communicates neither (red-team A6); the
capture–recapture detectors had mismatched error universes and n₁₂=0 was the likely
outcome, making N̂ decorative (confirmed defect 2); agreement coefficients answer
"do raters agree", not "is the datum correct". `output/capture_recapture.py` is
retained in the repo as historical record, marked superseded.)*

---

## 6. Pre-registered thresholds and cut order (filed in the OSF amendment)

### 6a. Escalation triggers (cost-based control rules — NOT acceptance tests)
These thresholds are chosen on cost-of-error grounds and pre-registered so that
escalation cannot be improvised post hoc. They are **not** statistical
acceptance tests and are not evidence that a field "passed". The Level-A
trigger is an **absolute count — e_v ≥ 3 on any field, with the observed n_v
reported alongside**; its sensitivity varies with the denominator (at n_v = 40
and a true error rate of 5% it fires with only ~32% probability, ~78% at 10%;
at n_v = 30 the same absolute rule is a stricter 10% rate; 2 errors in 40
without a trigger still leaves a one-sided 95% upper bound of ~14.9%). The
per-field CIs of §4a are the evidence; the triggers are action rules.

| Trigger (pre-registered) | Action (costed) |
|---|---|
| e_v ≥ 3 errors on any Level-A field in the §4a audit (absolute count; n_v reported) | Scripted corpus-wide recheck of that field + root-cause note (~2–4 h/field) |
| Any confirmed FN in the §3-Step-4 census | Lexicon expansion with the paper's sector vocabulary + detector-(b) re-run; census the new candidates (closure loop, ~2 h/iteration) |
| ≥3 confirmed FNs total | Supervisor discussion of corpus-wide sector re-screen before locking the roster |
| >1 flip in the test–retest (out of 30) | Re-adjudicate every borderline-tagged decision in the logs (~2–4 h) |
| Canary flip rate >2% of fields | Report as partition-instability limitation; >5% → re-reconcile flipped fields |
| Grounding-check failure | Automatic: field routed to human queue (already in pipeline) |

### 6b. Overrun cut order (if human-hours run out — registered, not improvised)
1. SRS audit n=40 → n=30 (zero-error bound degrades 7.2% → 9.5%, stated openly;
   the e_v ≥ 3 trigger becomes a stricter rate at the smaller n_v — declared);
2. If a further reduction is necessary, pause and file a dated deviation that
   identifies any non-core descriptive Level-A outputs omitted from the
   synthesis. The corresponding fields remain unresolved/not reported; model
   values do not acquire scripted precedence.

**Never cut:** the FN census, blind-first Tier-1 adjudication, and **the
blind-first Tier-2 work prescribed by the active §3-Step-5 branch** (integral
through |B|=40; the priority head + `n_sub=min(15, |B|−25)` in the larger
branches — the branch rule itself already scales Tier-2 to the roster size, so
the cut order never reduces it further). Any omitted Level-A output is declared
as out of synthesis scope and is not silently imputed from either model.

---

## 7. Execution order (B-first: the thesis core lands earliest — C-2.3 corrected sequence)

> **C-2.3 correction:** earlier revisions locked the Corpus-B roster BEFORE
> Tier-1 adjudication — wrong, because `methodological_eligibility` and
> `level_3b` divergences determine membership. Membership-critical
> adjudication now precedes the roster lock.

1. **Week 1:** file the dated OSF amendment → dual extraction runs (machine) →
   field-level reconciliation.
2. **Weeks 1–2:** **blind-first adjudication of the membership-critical Tier-1
   divergences** (`methodological_eligibility`, `level_3b`) — the FN
   candidate-union census (incl. §3-Step-4b upstream audit) runs **in parallel
   on the concordant-excluded set**, since its inputs do not depend on those
   adjudications; census closure follows the closure rule.
3. **End of week 2:** **initial-wave Corpus-B roster locked** (= membership
   divergences adjudicated + candidate union emptied; §9 states what this does
   not close). The roster is **provisional until §16
   snowballing/supplementation closure** — snowballed/supplemented papers
   enter the same pipeline and can extend it. → **Tier-2 branch selected by
   |B|** (§3-Step-5); if |B| > 60, pause before Level-B work; otherwise each
   model workspace runs any required **Stage-3-only supplements** without
   changing its original membership decision.
4. **Weeks 3–4:** Tier-2 treatment per the branch → **the SQ2–4
   analytical data of the initial wave in hand**; analysis chapters can start.
5. **Weeks 5–6:** remaining Tier-1 divergences (`paper_type`, borderline
   leftovers) blind-first + Tier-3 anchored cleanup → Corpus A denominators
   final for the initial wave.
6. **Week 7:** §4a SRS audit + canary + test–retest scheduling + deposit packaging.

If everything after week 4 collapses, SQ2–4 still has its initial-wave data.
This ordering is part of the registered design.

---

## 8. Risk matrix (updated for C-2)

| Risk | Prob | Impact | Severity | Mitigation (in this protocol) | Evidence reported |
|---|---|---|---|---|---|
| Concordant false-negative in Corpus B | Med | Very high | **Critical** | §3-Step-4 three-detector union census + closure rule + exhaustive concordant-3B census | candidate list, per-paper verdicts, closure passes |
| FN invisible to all three detectors | Unknown (not estimable) | Very high | Serious | Named residual risk: requires a continuous-process paper that names no sector term, fools both models AND the recall pass — argued implausible, admitted not quantified (§9) | detector-coverage description |
| Anchoring in adjudication | Med | High | Serious | **Blind-first** on all Tier-1 divergences and the branch-prescribed Tier-2 head/subsample; any AI-prefill remainder is explicitly non-blind and field-by-field human-verified | Tier-1/Tier-2 reveal-change rates; verification-remainder discrepancies reported separately |
| Human (single-reviewer) error | Med | High | Serious | Test–retest flip count; per-decision evidence quotes; declared ceiling | x/n flips; quote-anchored logs |
| Protocol dies half-executed at deadline | Med→High | High | **Serious** | B-first ordering (§7) + pre-registered cut order (§6b) | executed-vs-registered checklist |
| Correlated concordant error (Level-A tail) | Med | Med | Moderate | §4a SRS audit per-field bounds; consequential cells censused | per-field counts + exact CIs |
| Robustness mistaken for correctness | Med | High | Serious | §0 framing; agreement = routing only | explicit "what this does not claim" |
| Fabricated values / contamination | Med | Med→High | Serious | Corpus-wide grounding check (every value quote-verified against the PDF) | pass rate + failure list |
| Run-to-run instability (sampling not configurable on subscription surfaces) | Med | Med | Moderate | Determinism canary (n=30, fixed config) | canary flip rate per model |
| Silent surface/model updates mid-run (no snapshot pinning available) | Med | Med | Moderate | Record surface versions + model labels per run; B-first ordering shortens the exposure window; declared residual risk | version/label log per run |
| OSF single-reviewer deviation undeclared | High if ignored | High | Serious | **Dated amendment before run** (describes C-2 incl. thresholds + cut order) | timestamped OSF amendment |
| PDF non-retrieval skewed to Corpus B | Med | High | Serious | Coverage limitation + sensitivity table (retrieved vs missing by sector/year); manual-download pass on high-value tiers before corpus freeze | `non_retrieved_records.json` + sector/year table |
| `source_string` null (all records) | High | Low→Med | Minor | Declared Rayyan-export traceability limit | — |

---

## 9. What this design explicitly does NOT claim
- That inter-model agreement proves correctness.
- That it is equivalent to dual independent **human** extraction. With no second
  human, "AI unreliable" cannot be distinguished from "variable intrinsically
  ambiguous", and test–retest measures self-consistency, not accuracy.
- A certified per-variable κ (impossible at sustainable n — see power analysis).
- Zero error on the un-audited concordant Level-A tail (bounded per field by the
  §4a exact CI — a probabilistic bound, not a deterministic cap).
- **"Corpus-B membership closed."** The census empties the three-detector
  candidate UNION; a paper invisible to all three detectors (no lexicon term,
  both models negative, no recall-pass signal) escapes it. That residual is
  argued implausible — a continuous-process paper that names no sector
  vocabulary — but it is declared, not quantified. The same applies to the
  Level-1/2 exclusion audit (§3-Step-4b): it re-checks lexicon hits + a sample,
  not every excluded record.
- Coverage of the ~137 non-retrieved reports (23% of the deduplicated
  universe; separate declared limitation with a per-decision/DOI/sector/year
  missingness table — retrieval is measurably biased: 85% of Rayyan-Included
  retrieved vs 65% of Maybe; 92% with-DOI vs 30% no-DOI).
- That the reveal-change rate is a causal estimate of anchoring (a post-reveal
  change can be a legitimate correction; the rate is reported descriptively).
- That a grounded quote semantically supports the extracted value (the string
  match proves traceability; semantic support rests on the human instruments).
- That every page locator in a Stage C record is as the extracting surface
  wrote it. **Locator correction, reviewer decision 2026-09-12:** where a quote
  exists word for word on exactly one page and the surface cited another, the
  grounding check replaces the page, keeps the cited one in
  `page_as_recorded`, sets `locator_corrected: true`, and queues the cell for
  human review. G1 (the sentence exists) passes; G2 (where it is) does not, and
  the record says so. The correction is mechanical and independently
  re-checkable — the string match IS its evidence — and is never counted as an
  exact match. Guards: a unique match only (a quote found on two pages stays a
  failure) and a minimum quote length of 40 characters, below which a phrase can
  recur in a running header. The count of corrections per paper is reported
  beside the exact count, never folded into it. Measured reason for the rule: on
  the pilot this was the dominant failure mode, two of four papers failing on
  nothing else, always by one page, in both directions, clustered on
  figure-heavy pages; blocking it spent three CLI attempts and an extraction on
  records whose evidence was entirely genuine.
- That the frozen v2.2.1 text normalisation reproduces the page faithfully at a
  line break. **Two production defects, found 2026-09-13 on the first 24
  records and repaired in the Stage C wrapper (`normalize_stage_c`), not in the
  frozen `normalize_text`:** (6) frozen rule 2 deletes a soft hyphen U+00AD
  before rule 3 joins a hyphenated line break, so a page reading `ma<U+00AD>\nchine`
  normalises to `ma chine` — a token no reader can write, making the page
  itself unquotable in both directions: neither the faithful copy nor the
  repaired word matches it (`rayyan-472536226`, which spent 5 CLI attempts and
  ~EUR 6 of subscription budget failing on nothing else). (7) The mirror image:
  frozen rule 3 joins ANY hyphen at a line break, so a URL wrapped as
  `.../1FbJGmVs-FNY0JE-\n7fgT...` loses a hyphen that is part of the address,
  and the quote that copies the address correctly cannot match
  (`rayyan-472536410`). Both are repaired before `normalize_text` sees the
  string, by the same reasoning already applied to the digit-range rule: a soft
  hyphen at a line break IS discretionary hyphenation, and inside a URL a
  hyphen is an address character, never word hyphenation. Both repairs are
  strictly more permissive and were verified to be inert on what had already
  passed: all 2 004 quotes in the 24 records accepted before the change were
  re-checked under both versions with identical acceptance classes (1 999
  `exact`, 5 `interleaved`). The frozen schema digest
  `d855254b73a8640b4e13255876a3021ae9da699e1bf04bb4db3d5b2444e883ff` is
  unaffected: neither the instrument nor the prompt changed. `normalize_text`
  itself is NOT touched — its behaviour remains in the provenance of the
  corpus-wide v2.2.1 check.
- **Any denominator claim over Corpus B, under the executed 11 + 31 coverage**
  (amendment note, §2). "*n* of 42 papers report X", "X is absent from the
  corpus", "two thirds propose nothing" require blind-first coverage of the
  whole roster, which the executed design does not have. Such results are
  reported either over the 11 blind-first papers — named, with their sector
  composition — or over the 42 at field-verification level with the sections
  read declared. They are never reported as properties of the literature.
  Per-result levels and the cut order:
  `RESULT_FIELD_VERIFICATION_MATRIX_2026-09-12.md`.
- **SQ4 and R15 at all. Withdrawn 2026-09-16, by the reviewer, for hours.** The transferability
  result over the refining/petrochemical core was the only result the 11 blind-first papers were
  selected to support, and §7 registers it as the LAST claim to be cut. It is cut first, and the
  order matters enough to say why: every earlier step of that order removes a claim that was
  already unavailable under the executed 11 + 31 coverage and therefore frees no hours at all,
  while R15 alone carried a real cost — roughly 22 hours of blind-first reading against a
  2026-09-30 deposit. The cut is a departure from the registered cut order, taken knowingly, and
  is recorded as such rather than executed silently. Consequences, all of them declared:
  (a) no result in the chapter rests on the 11 as a privileged subset; they are 11 ordinary
  records among 41. (b) The blind-first option was spent deliberately: their dossiers were
  released with `--include-core-without-blind-first`, which cannot be undone, so no later session
  can restore V3 on those papers. (c) The thesis makes its bridge from the literature to the
  Sines case through Chapter 1 and the case itself, not through a literature-based
  transferability argument. `C5` and `implementation_barriers` are unaffected and keep serving
  R10 and R9.
- **Any verification level above "extracted and grounded" on the results that ARE claimed.**
  Executed: single-surface extraction under the frozen instrument, every record validating, and
  every evidence quote checked against the physical page it cites by the protocol's own checker
  (41 records, 3 111 quotes, 3 101 exact, 10 routed for reading as line-number ambiguity; 30 → 41
  dossiers, 642 quotes, all exact). NOT executed: V1, V2 or V3 — no human independently re-read
  a cell against the paper and confirmed the coding. The triage worklist (1 364 cells) was built
  and is deposited, and was not worked. The chapter therefore reports what the extraction found,
  with the quote and page as the evidence a reader can check, and says so; it does not report
  verified properties of the literature. Claims the reviewer chooses to assert on his own
  authority are verified individually before they are written, and the rule for which ones is
  registered here: **every quotation reproduced in the chapter, and every claim of absence.**
- That the refining/petrochemical head substitutes for the roster on SQ2.
  Roughly 70 % of the mechanism evidence sits in cement, glass, pulp & paper
  and steel; a figure drawn from the 11 is a figure about refining.
- **Any inter-model agreement statistic for Stage C.** There is one extraction
  surface (amendment note, §2), so no Tier-2 cell is concordant or divergent and
  no reveal-change rate against a second surface exists. Stage C figures are
  reported as single-surface extraction plus the human verification actually
  performed, and nothing else. Tier-1 and Tier-3 dual-extraction figures are
  unaffected and keep their own provenance.
- That the triage replacing divergence routing measures correctness. It ranks
  cells by what the extraction DECLARES about itself; a cell that declares
  itself a direct statement with an exact quote can still be wrong, and the
  sampled P3 tier is the only thing standing between that and an unexamined
  value. The sampled share is reported.

---

## 10. Reproducibility & provenance
- **Execution-surface provenance (consumer subscriptions — no model-invocation
  API/CLI runner):** record in `run_metadata.json`, per run: application
  version, model label exactly as displayed by each surface, runtime
  configuration, run dates and per-paper timestamps. Subscription surfaces
  expose **no guaranteed dated model
  snapshots, no sampling parameters, and no request IDs** — state this
  plainly rather than implying API-grade pinning.
- Deposit **all raw model outputs (both models × all papers) + the full census and
  adjudication logs** (per field: both model values, blind decision, final value,
  evidence mode and evidence, rule, timestamp, reveal state and any deviation)
  on OSF — this frozen artefact is the reproducible object. Stage-4 lineage
  additionally records the content hash of every consumed input and the selected
  source for every field.
- Prompts: git tags v2.0→v2.3.1-operational; record the exact tag +
  commit hash used (schema unchanged at v2.2.1; eligibility prompt at v2.3).
- The pre-registered thresholds (§6a) and workload-contingency rule (§6b) are
  substantively recorded in the filed OSF amendment, so any later degradation
  must be dated and declared rather than improvised.
- State plainly: re-execution against future surface/model versions is not
  expected to reproduce; the deposited outputs + logs are the reproducible
  record.

---

## 11. Methods text for the thesis (EN, QC-framed — drop-in for the annex)

> **AI-assisted charting validation.** The charting process was validated with a
> risk-stratified, AI-assisted quality-control design rather than a conventional
> inter-rater reliability study, reflecting the registered single-reviewer nature of
> the review and a power analysis showing that per-variable Cohen's κ cannot be
> stably estimated for rare, analytically central variables. AI systems were used as
> charting tools, not as independent reviewers; inter-model agreement was used solely
> as a routing signal to allocate human effort, never as evidence of correctness.
> The design principle was to take a census wherever the population was small enough
> for the reviewer to enumerate, and to sample only where it was not.
>
> All available full texts were charted independently by two large language model
> families (one clean Claude Code application session and one clean Codex/ChatGPT
> application session, running on consumer subscriptions whose sampling
> configuration is provider-managed and not
> user-controllable, against the frozen v2.2.1 schema with versioned
> prompts; raw outputs archived) and reconciled field by field. For the consequential
> fields determining analytical-corpus membership, every inter-model disagreement was
> adjudicated by the reviewer **blind-first** — extracting from the source before
> viewing model outputs — with the reveal-induced change rate reported as a
> descriptive anchoring-exposure figure. Continuous-process-corpus membership was
> additionally defended by an exhaustive false-negative candidate census: the union
> of model flags, a deterministic sector-terminology search over all full texts, and
> a recall-oriented counter-anchored model pass generated a candidate list that the
> reviewer emptied, with a pre-registered closure rule (any confirmed false negative
> expanded the search lexicon and re-ran the detectors until a full pass produced no
> new candidates); the residual risk of papers invisible to all three detectors is
> reported as a declared limitation. The same terminology search was applied
> retrospectively to the title/abstract-excluded records as an upstream screening
> audit. Analytical fields of continuous-process papers received the
> pre-registered corpus-size-branch treatment: `min(|B|,40)` papers were
> extracted blind-first, with model outputs revealed only after commitment and
> used solely as post-hoc discrepancy checkers; only any roster remainder beyond
> 40 received AI pre-fill plus field-by-field human verification, reported as a
> separate non-blind instrument.
>
> Level-A inter-model divergences were adjudicated with both model outputs
> visible and retained field-level evidence, rule and timestamp; this accepted
> anchoring exposure was covered independently by the Level-A audit. Human
> absence decisions used an explicit full-text-absence mode with a rationale,
> rather than a fabricated supporting quotation. Consolidation applied the
> frozen schema's structural applicability rule after resolving methodological
> eligibility and otherwise failed closed on every unresolved divergence.
>
> The concordant bibliometric tail — the only population too large to enumerate —
> was audited by a simple random sample of 40 papers, fully re-extracted blind; each
> field reports its raw error count with an exact Clopper–Pearson 95% interval,
> never pooled. Escalation thresholds (control rules, not acceptance tests) and an effort-overrun cut
> order were pre-registered in a dated OSF amendment before the production run. A
> corpus-wide programmatic grounding check required every extracted value to carry a
> verbatim supporting quote verified against the source PDF. Reviewer
> self-consistency was measured by a two-week test–retest on the consequential
> decisions; the single-reviewer ceiling — the inability to distinguish model
> unreliability from intrinsic variable ambiguity — is declared as a limitation of
> the registered design. Cohen's κ was considered and rejected as the headline
> statistic because preliminary power analysis showed it could not be certified for
> rare classes at any feasible sample size.

*(A shorter main-chapter version condenses this to one paragraph; kept in the annex.)*

---

## 12. Fixed parameters (C-2.3 — reviewer-approved and filed 2026-07-23)
1. **SRS audit:** n = **40** papers (seed 44) sampled from ALL eligible
   reconciled papers; cell-level census/divergence exclusions per §4a;
   per-field e_v/n_v with exact Clopper–Pearson 95% CIs (marginal per field);
   pre-specified error definitions per field type (§4a); overrun floor
   n = 30 per §6b.
2. **Third-model arbiter:** **none** (C-1.0's Gemini arbiter deleted — correlated
   noise, no attached claim). Irresolvable Tier-1 cases → human with quote.
3. **Fabrication defence:** corpus-wide grounding check (§3-Step-6) under the
   full §6.3 8-rule normalisation, with failure-pattern logging; replaces the
   ~10-paper contamination probe. Traceability claim only (§9).
4. **Censuses (never sampled, never cut):** concordant `3B=true`; FN candidate
   union (3 detectors + tiered triage + closure rule); concordant
   `borderline=true`; §3-Step-4b·i upstream lexicon hits. (The §3-Step-4b·ii
   upstream sample is n = 50, seed 44, take-all if frame < 50 — a sample, not
   a census.)
5. **Tier-2 size branch (§3-Step-5):** thresholds |B| ≤ 25 / ≤ 60 / > 60,
   registered before the roster is known; branch-B head size = **K = 25**
   (D1 closed 2026-07-13).
6. **Escalation rules + cut order:** §6a/§6b, substantively registered in the
   filed OSF amendment; explicitly control rules, not acceptance tests; Level-A
   trigger is absolute e_v ≥ 3 with n_v reported.
7. **Test–retest:** n = 30 consequential decisions (20 borderline-tagged + 10
   random, seed 44; take-all + fill if fewer than 20 borderline), ≥ 2 weeks
   after adjudication.
8. **Determinism canary:** n = 30 papers (seed 44), end-of-run, both surfaces,
   fixed config; flip = normalised field-value change; denominator = fields
   evaluable in both runs; any Tier-1 flip → human review.
9. **Seeds:** 42 (form pilot), 44 (all C-2 random draws) — unchanged.
10. **Execution surfaces:** one clean Claude Code application session + one
   clean Codex/ChatGPT application session; no model-invocation runner;
   sampling provider-managed; provenance per §10. Claude-side runtime
   configuration (thinking/effort) =
   **adaptive thinking, effort high** (D2 closed 2026-07-13), recorded in
   `run_metadata.json` and held fixed for the run.
11. **Operational durability:** authoritative local, non-iCloud storage;
    content-hashed packs and fail-closed locks; default batch size 5 with
    explicit approval between batches; reviewer atomic autosave plus
    browser-local recovery; no reveal, navigation or finalisation after a
    failed durable save.
12. **Consolidation precedence:** human finalised value → model concordance →
    unresolved, except the registered structural ineligibility rule in
    §3-Step-2a. Eligible-paper divergences never receive scripted precedence.

---

## 13. Decision record (closed 2026-07-13, reviewer in chat) + remaining gates

**D1 — CLOSED (option a):** the 25 < |B| ≤ 60 branch's blind-first head is a
**fixed K = 25 papers** in sector-priority order; total blind-first in that
branch is `25 + n_sub = min(|B|,40)`, where
`n_sub = min(15, |B|−25)`.

**D2 — CLOSED (option a):** Claude-side runtime configuration = **adaptive
thinking, effort high**, recorded in `run_metadata.json` and held fixed for
the whole run; the determinism canary re-runs under the same setting.

**D3 — DEFERRED by the reviewer (2026-07-13, "not a problem now"):** the
supervisor endorsements (hours/deadline plan; |B| > 60 contingency) are not
treated as blocking. The **rule stands regardless**: if |B| > 60 is observed,
extraction pauses and a dated amendment note is filed before proceeding.

**D4 — CLOSED.** C-2.2 was reviewer-approved on 2026-07-13. The final C-2.3
text, including the 2026-07-20 operational clarification and 2026-07-21
contingency correction, was reviewer-approved on 2026-07-23. Its prospective
amendment was deposited the same day in OSF project `wh62r`, file ID
`6a61e15518c36790cda322f4`, before full-corpus production extraction.

**Methodological gates before production: CLOSED 2026-07-23.** The real
interactive seven-paper operational gate closed on 2026-07-20 with the
explicitly declared browser-data-loss deviation above; the corrected pipeline
completed Stage 4 with 7 consolidated records, locked Corpus B = 2, 0
unresolved fields and 0 cross-check flags, and the full implementation suite
passed 227 tests. This pilot closure is an operational readiness result, not a
substitute for the production FN census, Level-A audit, test–retest or
determinism canary. Production packs still require a clean committed source
state, full-queue rebuild, and per-session runtime provenance.

---

## Appendix A — Human-hours budget (C-2.3, re-based on measured volumes)

> Wall-clock note (subscription execution): the model phases run inside
> rate-limited consumer-subscription windows and may require **several days of
> intermittent sessions** for ~900–1,000 extraction tasks per family. This
> affects calendar, not human-hours; both file-backed workspaces are resumable
> per paper and stop after every approved batch.

C-2.0's totals rested on two numbers that did not survive verification: a
~50–100-candidate census (the lexicon alone fires on 220/459 papers at the
current corpus; 214/445 when first measured) and a
4–15-paper Corpus B (denominator misread; true prevalence unknown). The
re-based arithmetic, by Tier-2 branch:

| Instrument | Estimate |
|---|---|
| FN candidate-union census (§3-Step-4, tiered triage) | ~20–27 h (~220–280 candidates: Tier-hit-B skims 2 min + Tier-hit-A reads 10–12 min + closure pass) |
| Upstream L1/L2 exclusion audit (§3-Step-4b) | ~3–4 h (metadata-only) |
| Tier-2 branch treatment (§3-Step-5) | branch ≤25: ~20–25 h · branch 26–40: integral blind-first, scaling with \|B\| · branch 41–60: 40 blind-first + AI-prefill verification remainder, ~35–55 h total · branch >60: pause + amendment/supervisor decision |
| Blind-first Tier-1 adjudication (§3-Step-3) | ~14–17 h (~120 units × 7 min) |
| Tier-3 anchored cleanup (§3-Step-3b) | ~7 h (~500–1,200 conflicts, batched) |
| SRS n=40 audit (§4a) | ~13 h (40 papers × 20 min) |
| Grounding-check failure resolution | ~2 h |
| Test–retest + canary review | ~3 h |
| OSF amendment + deposit packaging | ~4 h |
| **Total** | **~84–100 h** (branch ≤25) · **~99–130 h** (branch 26–60) — the 40–80 h budget of the redesign brief holds ONLY in the small-B branch with the §6b cuts applied; the timeline conflict this creates is a supervisor decision, not a protocol parameter. No unmeasured overlap discount is applied. |
