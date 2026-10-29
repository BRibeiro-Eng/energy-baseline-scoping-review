# AI-Assisted Data Extraction Protocol — Level 3 Full-Text Charting

**Scoping review:** *Energy performance measurement models in continuous process industries under ISO 50001/50006*

**Reviewer (the human accountable for charting):** Bernardo Ribeiro — MEQB student, FCT/UNL — thesis at Galp Sines refinery. Email: `bmp.ribeiro@campus.fct.unl.pt`. Academic supervisor: Prof. Mário Eusébio.

**OSF registration:** DOI 10.17605/OSF.IO/TDW6C (protocol v2, April 2026 amendment).

**This document version:** **2.2.1** (schema FROZEN) **+ Validation Protocol C-2.3** (issued 2026-07-14; operational clarification 2026-07-20; contingency-rule correction 2026-07-21; reviewer-approved and filed 2026-07-23 — see `VALIDATION_PROTOCOL_C.md` and change log below).

---

### Change log

**C-2.3 reviewer sign-off and OSF filing (2026-07-23).** Bernardo Ribeiro
approved the final C-2.3 text. Before full-corpus production extraction, the
prospective amendment was deposited in OSF project `wh62r` as file
`6a61e15518c36790cda322f4`
(`https://osf.io/wh62r/files/osfstorage/6a61e15518c36790cda322f4`).
The deposited PDF SHA-256 is
`15c140cdcc18f1f9d9c1dd7520d9ad96741cccafd654ad8b39fac64412ec2650`.

**C-2.3 pre-sign-off contingency correction (2026-07-21).** The overrun rules
that allowed scripted model precedence for Tier-3 divergences and selective
`paper_type` adjudication were removed because they contradicted the C-2.3
fail-closed and Tier-1 blind-first rules. The only automatic workload reduction
is now the registered Level-A audit change from n=40 to n=30. Any further
reduction requires a dated deviation identifying non-core descriptive outputs
omitted from the synthesis; neither model silently becomes the source of truth.

**C-2.3 pre-sign-off operational clarification (2026-07-20).** The real
interactive seven-paper re-pilot completed in both application workspaces and
Stage 4 consolidated 7 records (pilot Corpus B = 2; 0 unresolved fields; 0
cross-check flags; 227 tests). A browser refresh erased two completed but not
durably saved blind Level-B forms. The values were not reconstructed as blind;
their final pilot decisions are explicitly post-reveal/non-blind and excluded
from reveal-change claims. Before production, the reviewer form gained atomic
autosave, browser-local recovery and fail-closed navigation/commit/finalisation;
human absence decisions gained a no-quote full-text-absence mode with mandatory
rationale; and Stage 4 gained a narrow structural rule that nulls Level A after
resolved ineligibility while keeping every eligible-paper divergence fail-closed.
Authoritative storage remains local outside the conservatively prohibited
Desktop, Documents and Mobile Documents roots. **The final C-2.3 sign-off and
dated OSF filing gates closed on 2026-07-23.**

**C-2.3 order fix (2026-07-13, later same day).** Second external review verified and applied: **execution order corrected — membership-critical Tier-1 adjudication (`methodological_eligibility`, `level_3b`) now precedes the Corpus-B roster lock** (the C-2.2 order closed membership before adjudicating its determining fields); roster renamed **initial-wave/provisional** until §16 closure; Tier-2 branch edge case closed (sub-sample = min(15, |B|−25); remainder ≤15 → integral, so |B| ≤ 40 degenerates to integral blind-first); |B|>60 = pause → dated amendment note → proceed; overclaims removed ("validated"→pre-registered; provisional-accept class named in the Tier-1 row; FN-invisible probability → Unknown); volumes re-based 220/459 / ~220–280; upstream reports x/n_u; canary drawn from the end-of-run proceeding corpus; OSF: R/M set notation with clean trigger disjunction, "procedure to be used", observable retrieval-differential phrasing, JBI selection-vs-charting wording per the JBI Manual. At that date the revision still awaited sign-off; the gate closed on 2026-07-23.

**C-2.2 sync (2026-07-13).** External methodological review applied: execution surfaces corrected to consumer subscriptions (Claude Code/Max + Codex CLI/ChatGPT Plus — no API; sampling not configurable; no snapshot pinning; provenance = surface versions + model labels + dates + deposited raw outputs); two-stage corpus freeze (2026-07-10 = INITIAL DATABASE-RETRIEVAL freeze; FINAL review-corpus freeze only after §16 snowballing/supplementation closure); §16 adaptive rule formalised (S/M symbols, S=0 case, cause-routed remedies, iterate-to-closure); Level-A audit corrected to cell-level frame semantics (SRS over ALL eligible papers; per-field n_v); trigger = absolute e_v ≥ 3 with n_v reported; blind-first Tier-2 claims qualified by the |B| branch; open decisions D1–D4 in VALIDATION_PROTOCOL_C.md §13 are BLOCKING. Lexicon volume re-based: 220/459 papers hit ≥1 term.

**v2.3 — reviewer decisions applied (2026-07-10; schema UNCHANGED, still FROZEN v2.2.1).** Five reviewer decisions from the Round-3 methodological review: (1) **claims scope = mapping of reported evidence**, not adequacy assessment (no a-priori adequacy matrix exists; adequacy discussion is qualitative and interpretive, confined to the refinery chapter of the thesis); (2) **SQ1–4 restated at review scope** in the OSF amendment (SQ4 = transferability conditions reported for refinery contexts; empirical Sines validation = separate thesis protocol); (3) **§5.3 Corpus-B circularity fix** — membership by production mode against a CLOSED sector list (registered 5 + continuous chemicals, industrial gases, glass); the "non-stationary dynamics" defining clause deleted (mechanisms are extracted outcomes); ONE analytical corpus with sector-granular reporting (nested-sets proposal rejected by the reviewer 2026-07-10 — subset views derivable from sector tables); unlisted sectors route to human decision; (4) **§5.2 eligibility restored to the REGISTERED threshold** ("presents, proposes, evaluates or critiques a model with sufficient detail to identify and characterise it") — the v2.1–v2.2.1 tightening (operational detail AND fitted instance/≥3-apps) excluded critiques, conceptual proposals and unvalidated models and is reverted; validation is a variable, never a gate; prompts re-tagged `v2.3-eligibility-registered`; mini re-pilot on the 7 pilot papers recommended before production; (5) **no second human available** — L1/L2 mitigation = C-2.1 §3-Step-4b upstream exclusion audit + declaration. **Initial database-retrieval freeze at 459 retrieved / 137 non-retrieved (reviewer decision: remainder non-recoverable). The FINAL review corpus freeze occurs only after §16 snowballing/supplementation closure.**

**Protocol C revised → C-2.0 (2026-07-03).** A verified defect review of C-1.0 (6 confirmed defects: invalid pooled-Wilson estimator over a deliberately oversampled stratified audit; capture–recapture with mismatched detector universes and likely n₁₂=0; anchored AI-pre-fill verification on the most important tier; three coexisting audit-sizing rules; hard-coded "human residual error = 0"; no acceptance/escalation thresholds) plus a 3-designer redesign panel converged on **seven surgical changes**, now authoritative in `VALIDATION_PROTOCOL_C.md` (C-2.0): (1) capture–recapture → **exhaustible FN candidate-union census** (model flags + lexicon + counter-anchored recall pass) with closure rule; (2) stratified audit → **SRS n=40** with per-field exact Clopper–Pearson CIs, rare consequential cells censused exhaustively and excluded from the frame; (3) **Tier-2 inverted to blind-first human extraction** (form withholds AI pre-fill); (4) composite R̂ + AC1 deleted, metrics reported separately + **test–retest** self-consistency check; (5) **pre-registered thresholds + overrun cut order** in the OSF amendment; (6) Gemini arbiter deleted, contamination probe → corpus-wide grounding check, canary kept; (7) **B-first execution order** (Corpus-B roster locked first — candidate-union closure; residual risk declared). Provenance: `REVIEW_ROUND2_C2.md`. Schema unchanged (FROZEN v2.2.1). **Requires the dated OSF amendment (now describing C-2) before the production run.**

**Validation redesign → Protocol C (2026-06-25; revised to C-2.0 above).** The validation methodology (§2, §12.5, §13.2–13.3) was redesigned; it is now specified authoritatively in **`VALIDATION_PROTOCOL_C.md`**. **Schema is unchanged (still FROZEN v2.2.1).** The prior n=30 hybrid pilot + random-20% audit are **superseded** (kept as historical record). C = two-model extraction over the whole corpus → **blind-first** adjudication of Tier-1 disagreements → **stratified** blind audit + adversarial false-negative hunt → **capture–recapture** → integral human review of Level-3B Level-B; headline metric = **estimated residual charting error per variable** (not κ). Inter-model agreement is routing only, never reliability. Rationale: power analysis (small-n κ uncertifiable) + cross-model probe (`output/pilot_30/ai_blind_test/`) + multi-round red-team (`REDTEAM_ROUND1.md` + external GPT/Gemini review). **Requires a dated OSF amendment before the production run.**

**v2.2.1 SCHEMA FROZEN (applied June 2026, after v2.2 re-pilot on 7 papers).** v2.2 brought schema-bound disagreements down from 17 (v2.1) to 6 (v2.2) — 65% reduction — and eliminated hallucinations entirely (0 vs 1 in v2.1). The 19 grounding failures detected by v2.2 were **all encoding/glyph artefacts of PDF text extraction, not extraction errors**: 10 line-break hyphenation, 7 Greek-beta-as-fi-ligature substitution (Symbol-font fallback in IEEE Xplore PDFs), 1 control-character + curly-apostrophe artefact, 1 page-locality semantic for non-contiguous evidence. v2.2.1 is a **tooling-only patch** (no schema redesign):

- **§6.3 normalization expanded** from 6 rules to 8: added control-character strip, line-break hyphenation join (largest single fix), Greek-beta-as-ligature mapping, and ¶/¹ as apostrophe equivalents.
- **§6.3 non-contiguous evidence**: `page` becomes a parallel list of integers when `non_contiguous_evidence=true`, aligned positionally to substrings. Each substring is verified against its claimed page individually.
- **§6.3 JSON encoding lock**: explicit canonical encoding for envelope fields; ambiguous encodings (JSON-string-of-JSON) fail validation.
- **§5.2 decision tree for review/synthesis papers**: explicit branching for the §5.2(b2) review/synthesis category. Borderline cases route to mandatory human review via a new `borderline_review_synthesis_eligibility` flag instead of forcing the AI to commit.

**Schema FROZEN at v2.2.1.** Justification: schema-bound disagreements are at 6 total across 7 papers, with 5 papers at ≤1 SB; the single outlier (rayyan-472535533) is now routed to mandatory human review by the v2.2.1 decision tree, so it no longer triggers a "schema problem". Grounding failures from the v2.2 re-pilot were all encoding-class issues addressable by normalization expansion (not schema redesign). The protocol has reached the point where further iteration would refine encoding rules at diminishing returns; we proceed to §13.2 AI validation pilot (n=30) with the v2.2.1 schema, monitor for any new encoding patterns in that larger sample, and extend normalization if new patterns emerge.

**v2.2.1 enforcement erratum (2026-07-14; no variable or eligibility change).**
The real interactive re-pilot showed that the tracked JSON Schema did not
enforce the already-frozen value types/domains and that the B13b table omitted
the per-object evidence explicitly required by the Stage-3 prompt. The
executable contract now enforces every frozen field and requires B13b model
objects to contain `metric`, `value`, `unit`, `period_or_context`,
`evidence_quote`, and `page` (with optional `non_contiguous_evidence`). The
schema label remains 2.2.1 because this corrects enforcement of the intended
prompt contract; provenance is carried by the code commit, contract SHA-256,
and strict revalidation ledger.

**Prompts re-tagged as `v2.2.1-frozen`.**

**v2.2 targeted refinement (applied June 2026, after v2.1 re-pilot on 7 papers).** The v2.1 schema rework resolved the 3 critical and most major issues of v2.0, but the v2.1 re-pilot surfaced 5 residual major + 5 minor + 1 cosmetic schema issues + 1 tooling bug. Synthesis decision: `further_rework_then_repeat` (refinement, not major rework). Per-paper schema-bound disagreements: 3/4/6/1/0/3/0; total grounding failures: 6 (1 hallucination + 4 off-by-one page errors + 1 glyph corruption). The 4 off-by-one errors all concentrate in paper 358 and are caused by an unspecified page-numbering convention; the glyph corruption is from re-extracting PDFs in each agent call (tooling bug below). v2.2 fixes:

- **Tooling fix (critical for reproducibility): `output/stage0_prepare.py` now persists `pdf.pages` in the bundle.** v2.1 was generating bundles without the pages array, forcing every Stage 1/2/3 agent to re-extract via pymupdf and producing inconsistent text (different glyph fallbacks across runs). This was the root cause of multiple grounding failures. Stage 0 re-run on all 599 keys with the fix.
- **A11 enum**: added `"simple intensity ratio"` (single-denominator, unfitted SEC-type normalisation — distinct from regression and from SEC mean).
- **A11 composite index**: tightened — must produce/normalise energy consumption. Decision-support scores (MCDM/AHP/TOPSIS/Fuzzy) for project ranking are NOT composite indices; coded in A11b.
- **A11b**: added `"multi-criteria decision-making (MCDM/AHP/TOPSIS/Fuzzy)"`.
- **A10c**: explicitly excludes voluntary certifications (SEP, ENERGY STAR — those are not regulations); scoping rule "must causally apply to studied dataset, not cited as legal context".
- **C3 normalization policy (§6.3)**: explicit allowed normalizations — dehyphenate, collapse whitespace, ligature/dash unification, soft-hyphen removal, lowercase. `evidence_quote` may be a LIST of literal substrings for non-contiguous spans (flagged `non_contiguous_evidence=true`). Reconstruction-only spans NOT allowed.
- **Page-numbering convention (§6.3, §8.10)**: explicit — `page` is the integer index into the `pdf.pages` array (PDF physical page, 1-indexed). NOT the printed journal page number.
- **A1c multi_site**: added `"not applicable"` for review/synthesis papers aggregating across independent organizations.
- **B12 data_type**: enum is strict — no free-form annotation suffixes (use B4b scope_description or separate fields for context).
- **B3 validation_types**: parenthetical broadened — `"statistical"` covers any inferential test of model fit/significance (R², p-values, F/t/chi² tests, AIC/BIC, cross-validation, residual analysis).
- **B5 / B14 disambiguation**: added default rule for dual-nature statements — if a statement directly constrains model construction (e.g., "instruments needed for proper definition are lacking"), default to B5 (model limitation); else B14 (operational barrier).
- **A1b paper_type**: added `"tool/software design"` value for software-development genre papers.
- **A7 country_region**: explicit — case-study site geography only. Corporate HQ or author affiliation does NOT go here.
- **Evidence quote for value=`"none"` (or empty multi-select)**: `evidence_quote` may be `null` OR must literally state the absence (e.g., "no validation reported", "no ISO standard cited"). NOT a descriptive quote about the excluded methodology.

**Prompts re-tagged as `v2.2-refined`.** Re-pilot to run on the same 7 papers; decision rule unchanged (≤1 SB disagreement per paper + 0 grounding failures → freeze).

---

### Change log

**v2.1 schema rework (applied June 2026, after form pilot §13.1 surfaced 3 critical + 9 major + 5 minor + 2 cosmetic schema issues).** Form pilot ran on 5 papers via AI-assisted extraction with adversarial verification (deviation from blind manual extraction documented in §2 framing); 4/5 papers had verifier disagreements. The synthesis recommended `major_rework_then_repeat_pilot`. Critical fixes applied:

- **C1 (§5.3, §12.3): Level 3B scope expanded** beyond the original 5 sectors to include continuous chemical production, industrial gases, and other continuous-flow industrial sectors with non-stationary energy-production dynamics. The §12.3 biconditional cross-check `level_3b ⟺ A9='continuous process'` is replaced with the one-way implication `level_3b=true ⇒ A9 ∈ {continuous process, mixed}`. Rationale: the original 5-sector list excluded papers with substantively identical methodological challenges (sulfuric acid, industrial gases) and the biconditional produced false positives.
- **C2 (§6.1, §9, §12.3): Level A scoping enforced.** When `methodological_eligibility=false`, ALL Level A fields MUST be null. The Stage 1 prompt short-circuits Level A; post-extraction validator rejects records that violate. `enpi_enb_model_types` gains a `'not applicable'` value for ineligible/no-model cases.
- **C3 (§6.3, §9, §10, §11, §12.2): Evidence envelope made MANDATORY** with programmatic grounding check. Schema is `{value, evidence_quote, page, confidence}`; `evidence_quote` must be a literal substring of the extracted PDF text; Stage 4 §12.2 verifies via fuzzy substring match per page; mismatches invalidate the field and route to needs_review. Rationale: the form pilot detected a hallucination (paper 472535592 cited "Figure 4 r² 0.53/0.17 CHW/CDD" — strings absent from extracted text) that the value-only pilot schema could not catch.

Major fixes:
- **M1**: `normative_context` decomposed into `ems_standard` (A10a, multi), `mv_protocol` (A10b, multi), `regulatory_driver` (A10c, multi).
- **M2**: `enpi_enb_model_types` enum expanded (linear vs multiple disambiguation, SEC mean, change-point/SPC, process integration, not applicable); `composite index` tightened to require ≥2 weighted sub-metrics.
- **M3**: `performance_metrics_reported` split into `model_parameters_reported` (B13a) and `performance_metrics_reported` (B13b, only goodness-of-fit / validation metrics).
- **M4**: `complementary_methodologies` (A11b) added for pinch analysis, exergy, etc.
- **M5**: `identifies_limitations` renamed to `identifies_model_limitations` and disambiguated from `implementation_barriers` (B14); same text item must map to exactly ONE category, with positive/negative examples in §11.
- **M6**: `paper_type` (A1b) added for single-case / multi-case / review-synthesis / maturity / methodological-theoretical / other; `multi_site` (A1c) boolean added; `mixed` definition sharpened to "multi-sector study spanning ≥2 distinct industrial sectors".
- **M7**: `scale_of_application` (B4) gains `'sub-system / utility system'` value; `scope_description` (B4b) added.
- **M8**: §5.2 eligibility sharpened with explicit (a) AND (b) sub-criteria; `'review/synthesis'` recognised as eligible category (b2) with ≥3 documented applications.
- **M9**: JSON-Schema validation post-extraction enforced; records missing required fields are rejected.

Minor fixes: `data_type` adds `'unspecified or not stated'`; `validation_types` adds explicit `'statistical'` value; `baseline_period_start`/`end` (B2a, B2b) added; A8 verbatim-from-paper rule explicit (form pilot revealed extractor injected "medical device" when paper said "life sciences"); JSON-Schema enforcement of A12 source_string presence.

Cosmetic: IEEE Xplore title-encoding artefact documented; Stage 0 author-count sanity check noted.

**Prompts re-tagged as `v2.1-schema-rework`.** Re-pilot to be run on the same 5 papers (for cached comparison) + 2 fresh papers (seed 42 with skip). Decision rule for proceeding: ≤1 verifier disagreement per paper on schema-bound fields + zero ungrounded evidence.



**v2.0 data-quality patch (applied May 2026, before any LLM call)** — A pre-flight audit of the then-available 373 PDFs detected three categories of data contamination that the original Stage 0 would not catch: 9 wrong-content PDFs (file-name/content mismatch), 4 garbled-extraction PDFs (correct paper, non-standard glyph encoding), and 3 hash-identical Rayyan dedup failures. All contaminated files were contained before extraction; seven wrong-content records later received correct replacements and the two unresolved records remain in the frozen non-retrieved set. See `data/data_quality_report.md` and `data/redownload_queue.json` for the audit trail. Stage 0 (§8) expanded with three new checks: hash deduplication, title/DOI vs metadata match (wrong-PDF detection), and composite garbled detection (ASCII letter fraction + common-English-word match count). Extraction now uses a fallback chain: pymupdf → pdfplumber → tesseract OCR → quarantine. Files referenced from §3 / §8: `pdfs_quarantine/`, `ocr_recovered/`, `excluded_duplicates.json`, `redownload_queue.json`, `preflight_scan.csv`.

**v2.0 (current)** — Tailor-made for the executing Claude Code session. Standalone (no external context dependencies beyond `data/`). Nomenclature change: `Corpus A` / `Corpus B` from the OSF protocol renamed to `Level 3A` / `Level 3B` throughout this document to avoid collision with `Source String A` / `Source String B` from the search strategy (see §A Terminology). Audience changed from reviewer to executing session; second-person imperative. All previously open decisions fixed (seeds, throttle, audit sample fraction, blind-extraction template). §17 "Open questions" removed; §17 redefined as "Output to the reviewer". §0 "Working environment & quick start" added.

**v1.1 patches (carried forward)** — Eliminated confidence-gating contradiction in routing; explicit audit-sample scope and reliability-claim bounds; explicit declaration of asymmetric routing (false-positive vs false-negative Level 3B); snowballed papers reconciled with the source-string enum.

**v1.1** — Temperature 0 across all stages; replicate-as-gate removed (AI-vs-AI is sampling noise, not semantic ambiguity). Mechanical exclusions moved from LLM prompt to Stage 0 deterministic gates. Metadata-only mode removed (pipeline assumes full text). Level 3B classification made conservative (every AI-positive B triggers mandatory human review). Cross-checks added at Stage 4. Pilot reformulated: 5 form-pilot first, then n=30 AI reliability validation. Evidence grounding rewritten with page-map and length-sensitive thresholds. Confidence demoted to soft annotation. Throughput and snowballing sections added.

**v1.0** — Initial proposal (now superseded).

---

## 0. Working environment & quick start

### 0.1 You

You are one of two clean interactive application sessions acting as an orchestrator for this extraction pipeline: either Codex/ChatGPT or Claude Code. You are running locally on the reviewer's macOS machine. The authoritative source tree is `/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction/`; production work occurs only inside the generated `production/chatgpt/` or `production/claude/` workspace assigned to the session. **Never use the archived Desktop/iCloud copy as a live input or output.** Read only the files exposed inside your assigned workspace and write only to its permitted runtime paths.

### 0.2 Model and sampling

- **Models:** validation (Protocol C-2.3) uses **two model families** on **consumer-subscription application surfaces** — Claude in Claude Code under the reviewer's Claude subscription and GPT in Codex/ChatGPT under the reviewer's ChatGPT subscription. One clean session per surface orchestrates article-level subagents; each subagent handles exactly one paper end-to-end. **No API runner and no third-model arbiter.** The surfaces expose no guaranteed dated model snapshots or request IDs; record **surface provenance** at run start in `output/run_metadata.json`: application version, model label as displayed by the surface, configuration, and run dates.
- **Sampling:** provider-managed and not treated as reproducibly configurable. Run-to-run stability is measured by the C-2.3 determinism canary (n=30). Claude-side runtime configuration is **adaptive thinking, effort high** (D2 closed), recorded in `run_metadata.json` and held fixed for the run.

### 0.3 Role declaration

You are a **tool of the single reviewer**, not a co-reviewer. The OSF-registered protocol declares single-reviewer screening and charting (B. Ribeiro). Your output is a first-pass extraction; the reviewer verifies it. Reliability evidence comes from **AI-vs-human** comparison, never AI-vs-AI agreement. Under Protocol C-2.3 two models extract in parallel, but inter-model agreement is used **only to route the reviewer's attention** (disagreements → blind-first adjudication; concordant consequential cells → exhaustive censuses; the concordant bibliometric tail → SRS audit) — never as a reliability metric, never as two independent reviewers. The human establishes the adjudicated values blind-first on the consequential fields, and on Corpus-B analytical fields per the pre-registered size branch. See `VALIDATION_PROTOCOL_C.md`.

### 0.4 Language

All extraction prompts, all AI outputs, all written documentation produced by you (`output/*.md`, `output/*.json` keys, etc.): **English**. The reviewer may speak to you in Portuguese; respond in either language as appropriate for the conversational turn, but artefacts are EN.

### 0.5 Filesystem layout you inherit

```
level3_extraction/
├── PROTOCOL.md                      # this document
├── README.md                        # quick-start summary
├── data/                            # read-only inputs (post-preflight)
│   ├── articles.csv
│   ├── protocol_v2_reference.docx   # OSF-registered protocol for context
│   ├── pdfs/                        # 459 clean PDFs at the initial-retrieval freeze
│   ├── pdfs_quarantine/             # excluded by preflight; do NOT process
│   │   ├── wrong_pdf/               # 9 wrong originals retained; 7 replaced, 2 unresolved
│   │   └── rayyan_dedup/            # 3 files: Rayyan dedup secondaries (PDFs physically
│   │                                # separated; behaviour driven by excluded_duplicates.json)
│   ├── ocr_recovered/               # 5 .txt files: OCR-recovered text for
│   │                                # glyph-corrupted or image-only PDFs (Stage 0 uses these)
│   ├── excluded_duplicates.json     # 3 Rayyan dedup failures to skip
│   ├── redownload_queue.json        # disposition of 9 wrong originals (7 replaced, 2 unresolved)
│   ├── preflight_scan.csv           # full preflight audit results
│   ├── preflight_scan.py            # audit script (re-run on new arrivals)
│   └── data_quality_report.md       # preflight findings narrative
├── prompts/                         # versioned; you write here
│   ├── stage1_system.md
│   ├── stage2_system.md
│   ├── stage3_system.md
│   └── VERSION
└── output/                          # you write here
    └── (created subdirs as you proceed: stage0/, stage1/, ...)
```

**Effective initial-retrieval corpus entering your pipeline:** 459 PDFs in `data/pdfs/`. The 3 Rayyan duplicate secondaries have already been physically moved to `data/pdfs_quarantine/rayyan_dedup/`, so they no longer appear in `pdfs/`. Stage 0 still reads `excluded_duplicates.json` and emits `excluded_as_duplicate: true` stubs for those 3 keys (for PRISMA traceability — see §8.2). The 5 OCR-recovered text files are paired with PDFs already in `pdfs/`, so they are not double-counted; their `.pdf` lives in `pdfs/`, the OCR text is the input for extraction.

Universe in PRISMA = 596 after duplicate removal (was 599 in protocol). **As of the 2026-07-10 initial database-retrieval freeze: 459 PDFs in the canonical store; 137 not retrieved** (135 backlog + 2 unresolved wrong-PDF; coverage 77.0%). The final review corpus is declared only after §16 closure. Non-retrieval is measurably biased (85.0% of Included retrieved vs 65.4% of Maybe; 91.6% with-DOI vs 30.3% without) — report the frozen missingness table. All 459 store PDFs have a preflight row and a materialized Stage-0 bundle in the local runtime.

### 0.6 First actions checklist

1. Run the local storage and pack verifiers. Confirm the canonical input inventory contains 459 materialized PDFs, 459 preflight rows and 599 Stage-0 bundles; confirm `data/articles.csv` and `data/data_quality_report.md` are present. Read the data quality report before any extraction work. Report counts to the reviewer.
2. Read `data/protocol_v2_reference.docx` for full context of the registered protocol (you can extract text via `unzip` + parse XML, or via `python-docx` if installed).
3. Verify the existing versioned prompts and record their frozen commit/tag; do not re-initialise or silently edit the prompts repository.
4. Instantiate `run_metadata.json` from `config/run_metadata_template.json`. Replace every required `null` with observed run-time provenance before a batch can be authorized: displayed model label, application version, run identifier and timestamp, source commits, protocol/amendment identifiers and pack-manifest hash.
5. Verify the existing 599 Stage-0 bundles and canonical-input hashes. Rebuild a bundle only through the deterministic Stage-0 preparation path if its verified source changes.
6. Schema is already FROZEN at v2.2.1 (form pilot §13.1 complete). Do not re-open it.
7. Validation follows **`VALIDATION_PROTOCOL_C.md` (C-2.3, authoritative; reviewer-approved and filed 2026-07-23)**, not the superseded §13.2 n=30 pilot: two-model extraction over the corpus → **blind-first adjudication of the membership-critical Tier-1 divergences (`methodological_eligibility`, `level_3b`) + FN candidate-union census with closure rule (in parallel on the concordant-excluded set)** → **initial-wave Corpus-B roster locked** (provisional until §16 closure; residual risk declared) → size branch selected (|B| > 60 pauses before Level-B work) → model-specific Stage-3 supplements for roster papers lacking Level-B output → branch-prescribed human Tier-2 treatment → remaining Tier-1 adjudication → SRS n=40 audit of the concordant Level-A tail with exact per-field CIs + exhaustive censuses of concordant-3B/borderline cells.
8. Report per-field/per-instrument metrics (never pooled, no κ, no agreement coefficients) per `VALIDATION_PROTOCOL_C.md §5`; pre-registered thresholds and cut order per §6. The go/no-go decision is the reviewer's.
9. **DONE 2026-07-23:** reviewer sign-off and prospective OSF amendment filing completed before the production run (project `wh62r`, file `6a61e15518c36790cda322f4`). The initial database-retrieval corpus is frozen at 459 PDFs; later §16 additions are versioned separately and enter only through the registered supplementation path.

---

## A. Terminology

This document uses **Level 3A** and **Level 3B** for what the OSF-registered protocol v2 calls **Corpus A** and **Corpus B**. The substantive definitions and roles are identical; the rename is purely terminological, to disambiguate from the **Source String A / Source String B** labels of the search strategy.

| Term used here | Same as in OSF protocol v2 | Meaning |
|---|---|---|
| **Level 3A** (bibliometric set) | "Corpus A" | All Level 3 papers passing full-text eligibility, any sector. Supports SQ1. |
| **Level 3B** (analytical set) | "Corpus B" | Subset of Level 3A where application is explicitly in a continuous process industry (refining, petrochemicals, cement, pulp & paper, steel). Supports SQ2-4. |
| **Source String A** | (unchanged) | Search string for the normative corpus: ISO 50001 OR ISO 50006. |
| **Source String B** | (unchanged) | Search string for the methodological corpus: EnPI OR EnB OR ... + industrial context. |

When writing for the methodological annex of the thesis, use either nomenclature consistently. Inside `output/`, all field names and JSON keys use `level_3a` and `level_3b`.

---

## 1. Background — what this extraction is for

The scoping review maps energy performance measurement models (Energy Performance Indicators, EnPIs, and Energy Baselines, EnBs) under the ISO 50001/50006 normative framework. The central thesis is that EnPI/EnB models in the literature were predominantly developed and validated for discrete manufacturing and may be inadequate for **continuous process industries** (refining, petrochemicals, cement, pulp & paper, steel) due to non-stationary process behaviour (fouling, catalyst deactivation, feedstock variability).

Two-set structure (introduced in the OSF protocol v2 amendment):

| Set | Definition | Supports |
|---|---|---|
| **Level 3A** (bibliometric) | All papers passing full-text eligibility, any sector | SQ1 — distribution |
| **Level 3B** (analytical) | Subset of Level 3A where application is explicitly in continuous process industry | SQ2, SQ3, SQ4 — narrative synthesis |

Research questions:

- **SQ1**: What EnPI/EnB models exist in the literature within ISO 50001/50006 scope, in what contexts developed/validated, distributed by organisation type?
- **SQ2**: What operational variability mechanisms specific to continuous process may render these models inadequate?
- **SQ3**: How can EnPI/EnB models be adapted for continuous process variability?
- **SQ4**: To what extent are recommendations applicable in a real refinery context?

---

## 2. Methodological framing — protocol compliance

The OSF-registered protocol declares **single reviewer (B. Ribeiro)** for screening and charting. AI is **not** mentioned in the registered protocol.

The operational framing is:

> *Charting is performed by one accountable reviewer with first-pass extraction assisted by two AI model families. Inter-model agreement is a routing signal only. The reviewer adjudicates consequential divergences blind-first, exhausts the registered false-negative candidate union, applies the pre-registered Corpus-B Level-B size branch, and blind-audits an SRS of the concordant Level-A tail; all values retain source-grounded provenance.*

You are a tool of the reviewer, not a second reviewer. **Validation follows `VALIDATION_PROTOCOL_C.md` (C-2.3, authoritative and reviewer-approved 2026-07-23; supersedes the n=30 pilot + random-audit design described in §12.5 / §13.2 below, which are kept as historical record).** Reliability evidence comes from:

1. **FN candidate-union census** supporting Corpus-B membership: three detectors (model flags + deterministic lexicon + counter-anchored recall pass) build a candidate list the reviewer empties, with a lexicon-expansion closure rule. This exhausts the registered candidate union, not undetectable false negatives outside it.
2. **Pre-registered Corpus-B size branch:** the reviewer extracts Level-B fields blind-first for the entire roster through |B|=40, or for the sector-priority head of 25 plus a random sub-sample `n_sub=min(15, |B|−25)` when 40<|B|≤60; only the remainder beyond 40 receives AI pre-fill plus field-by-field human verification.
3. **Blind-first adjudication** of every consequential-field (Tier-1) inter-model disagreement — the reviewer establishes the adjudicated value from the source *before* seeing model output (no anchoring); reveal-change rate reported.
4. **SRS n=40 blind audit** of the concordant Level-A tail (per-field exact Clopper–Pearson CIs) + **exhaustive censuses** of the rare consequential cells (concordant-3B, lexicon hits, borderline flags).
5. **Corpus-wide grounding check** (every value quote-verified against the PDF), **test–retest** reviewer self-consistency, and a **determinism canary**.

Inter-model agreement is used **only as a routing signal** to allocate human effort — **never** as a reliability metric. (AI-vs-AI consistency shares model biases and cannot certify correctness. Reliability rests on blind-first human adjudication, exhausted registered censuses, and audited per-field error bounds — not on agreement.) Metrics are reported **per field / per instrument, never pooled**; no Cohen's κ, no agreement coefficients (the power analysis shows κ is uncertifiable at sustainable n).

This is a declared deviation from the OSF single-reviewer registration: a
**dated amendment was filed on 2026-07-23 before the production run** (OSF
project `wh62r`, file `6a61e15518c36790cda322f4`; source text:
`OSF_AMENDMENT_DRAFT.md`). Your job is to preserve complete provenance for
every extracted value.

---

## 3. Materials in `data/`

All paths relative to the working directory.

| Path | Description |
|---|---|
| `data/articles.csv` | Master metadata from Rayyan export. Source of truth for bibliographic fields. Key field: `key` (`rayyan-NNNNNNNNN`). Contains all Level 3 papers (Included + Maybe) plus Excluded ones from earlier screening levels. |
| `data/pdfs/*.pdf` | **459 PDFs at the 2026-07-10 initial database-retrieval freeze** (after preflight quarantine + manual recovery batches; dedup secondaries moved out), filename `rayyan-NNNNNNNNN.pdf`. Every later §16 addition must pass `preflight_scan.py` and be versioned separately. |
| `data/pdfs_quarantine/wrong_pdf/*.pdf` | **9 wrong original PDFs** retained for audit (file mismatched paper). Seven keys now have correct replacements in `data/pdfs/`; two remain non-retrieved. Never process the quarantined copies. |
| `data/pdfs_quarantine/rayyan_dedup/*.pdf` | **3 Rayyan dedup secondaries** (same MD5 as a primary already in `pdfs/`). Physically separated to keep `pdfs/` clean. Stage 0 still routes them via `excluded_duplicates.json` for PRISMA traceability (see §8.2). |
| `data/ocr_recovered/{key}.txt` | **5 OCR-recovered text files** for PDFs whose native text extraction is corrupted by non-standard glyph encoding, or which are image-only PDFs. Stage 0 must use these in preference to parsing the underlying PDF — see §8.4. |
| `data/excluded_duplicates.json` | **3 Rayyan dedup failures**: secondary keys to skip (same work, two venues). Stage 0 reads this file to suppress them — see §8.2. Universe becomes 596 (was 599). |
| `data/redownload_queue.json` | Frozen disposition of the 9 wrong-content keys: 7 correct replacements recovered; 2 unresolved and included in the 137 non-retrieved records. |
| `data/preflight_scan.csv` | Per-paper preflight audit results (one row per PDF). |
| `data/preflight_scan.py` | The audit script; re-run when new PDFs arrive. |
| `data/data_quality_report.md` | Narrative of the preflight findings and dispositions. **Read this before starting.** |
| `data/protocol_v2_reference.docx` | The OSF-registered protocol for context. Read once at start; not needed during execution. |

**Important:** the pipeline assumes full-text availability. Do not run extraction on metadata only. Historical pilots described in §13 retain their historical sample frames. Production uses the frozen set of 459 materialized PDFs; the 137 non-retrieved records are reported as missing and are not awaited. Any later paper enters only through the versioned §16 snowballing/supplementation path.

**Pre-existing data-quality resolutions (preflight, see `data/data_quality_report.md`):**
- 9 wrong originals remain in `pdfs_quarantine/wrong_pdf/` for audit — never process them; use the 7 canonical replacements and treat the 2 unresolved keys as non-retrieved.
- 5 papers have OCR-recovered text in `ocr_recovered/` — Stage 0 uses those.
- 3 Rayyan duplicates in `excluded_duplicates.json` — Stage 0 skips them.

---

## 4. Universe of Level 3 papers

From `data/articles.csv`, Level 3 papers are those tagged with `RAYYAN-INCLUSION: {"Bernardo"=>"Included"}` or `RAYYAN-INCLUSION: {"Bernardo"=>"Maybe"}` in the `notes` field.

- **Included**: 355
- **Maybe**: 244
- **Raw total**: 599
- **After preflight duplicate removal**: 596 (3 Rayyan dedup failures excluded, see `data/excluded_duplicates.json`)

The PRISMA flow diagram for this review should record:
- Records identified at Level 2 → 599 unique papers (post-Rayyan dedup attempt).
- Records removed at Level 3 as duplicates of one another → 3 (full-text-identical pairs detected by MD5 hash during preflight; see `data_quality_report.md` §2.3).
- Records entering AI-assisted charting → 596 ideally; 357 effectively at pilot time (full-text available).

Both Included and Maybe enter your pipeline identically; eligibility at Level 3 is determined here, not by the Rayyan label. However, the Rayyan label is used to **route human review effort**: every "Maybe" paper is reviewed by the reviewer at Stage 1 regardless of AI output (see §9).

---

## 5. Eligibility criteria

### 5.1 Deterministic eligibility filters (applied in Stage 0, pure Python)

A paper proceeds to Stage 1 (LLM) only if all of:

1. **Document type** is one of: peer-reviewed journal article, conference proceedings, doctoral dissertation, or grey literature from a recognised reference organisation (ISO, IEA, DOE, LBNL, CONCAWE, NRCan, IOGP, IPIECA, Solomon Associates). Source: CSV `document_type` (or inferred from `source` field with a small lookup).
2. **Language**: English. Source: CSV heuristic (title English + abstract English); manual override flag supported.
3. **Publication year ≥ 1996** (for database-search papers). Pre-1996 papers entering via snowballing are flagged separately and bypass this gate (see §16).
4. **Not retracted**. Source: regex scan of first/last 2 pages for `RETRACTED`, `Retraction Notice`, `This article has been retracted`. The reviewer has confirmed at least one retracted paper exists in the current set (Singh et al. 2024); this gate is non-optional. Note: an earlier draft included `WITHDRAWN` as a marker but this matched false positives in this corpus where authors discuss the EN 16001 standard "being withdrawn"; it is now excluded.
5. **PDF has extractable text**: mean chars/page ≥ 100 AND total chars ≥ 5000.

If any gate fails, the paper does not enter the LLM pipeline. It is written to `output/needs_review.md` with the failing reason and awaits the reviewer's manual handling.

### 5.2 LLM-judged eligibility (Stage 1) — REGISTERED THRESHOLD RESTORED (v2.3, 2026-07-10)

> **v2.3 change (reviewer decision, 2026-07-10).** The v2.1–v2.2.1 implementation
> had silently tightened the OSF-registered criterion ("presents, proposes,
> evaluates **or critiques** a model with sufficient detail") into a conjunction
> requiring operational detail AND a fitted instance/≥3-application synthesis —
> excluding critiques, conceptual proposals and unfitted models, precisely the
> documents that evidence gaps, and contradicting `validation_types = "none
> reported"` being a legal value. Restored to the registered threshold below;
> the presence, type and quality of validation are **extracted variables**
> (B3/A-fields), never eligibility gates. Prompts re-tagged (`v2.3-eligibility-registered`);
> schema UNCHANGED (still FROZEN v2.2.1). Declared in the OSF amendment;
> mini re-pilot on the 7 pilot papers recommended before production.

A paper is **eligible** if it **presents, proposes, evaluates, or critiques an
EnPI and/or EnB model with sufficient detail to identify and characterise it** —
i.e., the reader can tell WHAT is being measured/normalised AND at least one of:
the variables involved, the functional form, or the construction/estimation
approach.

Explicitly eligible under this threshold (all previously excluded by v2.1–v2.2.1):
- **methodological critiques** of existing EnPI/EnB models with that detail;
- **conceptual proposals** not yet fitted to data;
- **models without any reported validation** (validation status is data, not a gate);
- **reviews/syntheses** that characterise the models they cover (own fitted
  instance NOT required; the ≥3-documented-applications test of v2.2.1 becomes a
  routing heuristic, not a gate — see decision tree below).

Papers that mention EnPI/EnB only **incidentally** — no model identified or
characterised — or that present tools/frameworks with **no measurement-model
content at all**, are ineligible.

**v2.3 decision tree for review/synthesis papers** (routing aid, not a gate —
the borderline flag survives from v2.2.1 because it proved its worth on paper
472535533):

```
If paper_type = "review/synthesis":
  ├─ Does the paper characterise the models it covers (variables OR
  │  functional form OR construction approach identifiable, for the
  │  models central to its synthesis)?
  │  ├─ YES → eligible (registered threshold met)
  │  └─ NO  → ineligible (models mentioned only incidentally)
  │
  └─ If genuinely borderline after applying the above
     → mark eligibility=true BUT set Stage 1 routing flag
       `borderline_review_synthesis_eligibility=true`.
       This forces the paper to mandatory human review at §9
       routing (joins the Maybe-routing tail), regardless of
       Rayyan decision. The reviewer adjudicates eligibility,
       and downstream Level B (if applicable) reflects the
       reviewer's call.
```

The v2.2.1 own-fitted-instance / ≥3-applications tests are retained ONLY as
descriptive signals the model may cite when flagging borderline — they no
longer decide eligibility.

Topical exclusion (also Stage 1 LLM check): even if the paper meets the methodological-content bar, it is ineligible if its **exclusive** focus is one of:
- Residential buildings without industrial component.
- Government energy policy without organisational dimension.
- Purely economic energy management without performance measurement.
- ISO 14001/9001 without relation to ISO 50001 or energy management.

**Tagging:** category (b2) papers are flagged with `paper_type = "review/synthesis"` (see §6.1 A1b) for downstream tracking in SQ1 distribution.

### 5.3 Level 3B classification (Stage 1) — PRE-SPECIFIED MAIN SECTOR LIST, MODE-OF-PRODUCTION ONLY (v2.3, 2026-07-10; wording C-2.3)

A paper is classified as **Level 3B** if its application context is **explicitly**
in a continuous process industry, defined **solely by production mode**:
continuous-flow (24/7, non-discrete, non-batch) industrial production.

> **v2.3 circularity fix (reviewer decision).** The v2.1 definition included
> "exhibiting non-stationary energy-production relationships" as a defining
> property and an open-ended "other sectors with non-stationary dynamics"
> clause. Non-stationarity is the PHENOMENON SQ2 investigates — it cannot also
> be a membership criterion for the corpus where it is investigated. Membership
> is now decided by the pre-specified main sector list below; non-stationarity mechanisms
> (fouling, catalyst deactivation, feedstock variability, drift) are **extracted
> outcomes** (B5/B6), never classification inputs.

**In-scope sectors (pre-specified main list):**
- Petroleum refining
- Petrochemicals (organic chemistry, polymer production, olefins, etc.)
- Cement (and lime/clinker)
- Pulp & paper
- Steel (and other primary-metals continuous production)
- Continuous chemical production (sulfuric acid, ammonia, methanol, fertilizers, chlor-alkali, etc.)
- Industrial gases (air separation, hydrogen, nitrogen production)
- Glass (continuous melting / float lines)

**Unlisted sector that appears continuous-flow?** Do NOT self-classify: set
`level_3b=false` + `borderline_review_synthesis_eligibility=true` equivalent
routing via `reviewer_notes` — the human decides. Unlisted sectors NEVER enter
silently: a paper in an unlisted continuous-flow sector is reported as an
**exploratory case outside the main Corpus B** unless a **dated, documented
corpus decision** (recorded in `run_metadata.json` and noted for the OSF
amendment) adds the sector to the main list BEFORE its papers are counted in
Corpus-B analyses.

**Out-of-scope:** discrete manufacturing (parts, assembly, batch production);
services and offices; residential/commercial/institutional buildings;
batch-mode chemical production; agriculture; mining (unless processing is
continuous).

**Requirement:** the paper must **apply, validate, or empirically demonstrate**
the model in one of these sectors. Implicit, theoretical-only, or "could be
applied to" is **not** sufficient.

**Single analytical corpus (reviewer decision, 2026-07-10 — supersedes the
nested-sets proposal):** there is ONE Corpus B — all papers meeting the
main-list production-mode criterion above. No named sub-corpora. The
expansion beyond the 5 registered sectors is declared **prospectively** in the
dated OSF amendment (filed before any extraction), and all Corpus-B results
are reported **sector-granular**, so any subset view — the registered-5
sectors, or refining-only for SQ4 (petrochemical ≠ refinery for
transferability; keep them distinguishable in `sector_of_activity`) — is
derivable from the reported tables without pre-defining sets. The sector
distribution of the ISO 50001/50006 literature across ALL sectors remains an
SQ1 output over Corpus A.

---

## 6. Variable schema

Variables follow the OSF protocol v2 §6 verbatim.

### 6.1 Level A variables — applied to all eligible papers (i.e. all of Level 3A) — v2.1 REWORK

These support SQ1.

**SCOPING ENFORCEMENT (v2.1 critical fix C2):** When `methodological_eligibility = false`, ALL Level A fields A1b/A1c/A7–A11b MUST be `null`. The Stage 1 prompt short-circuits Level A extraction; the post-extraction validator rejects records that violate this. (A1, A2-A6, A12 are Stage-0 deterministic and remain populated regardless.)

| # | Variable | Type | Values | Source |
|---|---|---|---|---|
| A1 | `paper_id` (`rayyan-NNN`) | string | — | Stage 0 (CSV) |
| A1b | `paper_type` (v2.1 new — M6, M8; v2.2 expanded) | enum (single) | single applied case / multi-case study / review-synthesis / maturity model or framework / methodological-theoretical / tool-software design / other | Stage 2 (AI) |
| A1c | `multi_site` (v2.1 new — M6; v2.2: + `not applicable` for synthesis) | enum (single) | true / false / not applicable (paper_type=review/synthesis aggregating across independent orgs) | Stage 2 (AI) |
| A2 | `authors` | string | — | Stage 0 (CSV) |
| A3 | `year` | int | — | Stage 0 (CSV) |
| A4 | `title` | string | — | Stage 0 (CSV) |
| A5 | `source` (journal/proceedings) | string | — | Stage 0 (CSV) |
| A6 | `document_type` | enum | journal article / conference proceedings / dissertation / grey literature / other | Stage 0 (CSV) |
| A7 | `country_region` | string (free, verbatim) | Case-study site geography ONLY. NOT author affiliation. NOT corporate HQ. v2.2 explicit. | Stage 2 (AI) |
| A8 | `sector_of_activity` | string (free, **verbatim from paper** — see v2.1 rule below) | — | Stage 2 (AI) |
| A9 | `type_of_organisation` | enum (single) | continuous process / discrete manufacturing / services / buildings / mixed / not specified | Stage 2 (AI) |
| A10a (v2.1) | `ems_standard` (decomposed from A10) | enum (multi) | ISO 50001 / ISO 50002 / ISO 50006 / none / other-named | Stage 2 (AI) |
| A10b (v2.1) | `mv_protocol` (decomposed from A10) | enum (multi) | IPMVP / ASHRAE 14 / SEP M&V / BPA MT&R / ISO 17743 / none / other-named | Stage 2 (AI) |
| A10c (v2.1, v2.2 refined) | `regulatory_driver` (decomposed from A10) | enum (multi) | EU EED / national audit decree / EU-ETS / regional regulation / none / other-named. **v2.2 EXCLUDES voluntary certifications (SEP, ENERGY STAR — those are not regulations). Driver must causally apply to the studied dataset, not merely be cited as legal context.** | Stage 2 (AI) |
| A11 | `enpi_enb_model_types` (v2.1 expanded, v2.2 refined) | enum (multi) | linear regression (1 IV) / multiple regression (≥2 IVs, includes stepwise) / physical model / ML / **simple intensity ratio (single denominator, unfitted)** / SEC mean / **composite index (≥2 weighted sub-metrics that PREDICT or NORMALISE energy consumption — NOT decision-support/MCDM scoring; v2.2 tightened)** / change-point or SPC / process integration / other / not applicable | Stage 2 (AI) |
| A11b (v2.1 new — M4; v2.2 expanded) | `complementary_methodologies` | enum (multi) | pinch analysis / exergy analysis / thermodynamic modelling / process flowsheet simulation / ML ensemble / **multi-criteria decision-making (MCDM/AHP/TOPSIS/Fuzzy)** / none | Stage 2 (AI) |
| A12 | `source_string` | enum (single, nullable) | A / B / both / null (null for snowballed) | Stage 0 (CSV `notes`) |

**v2.1 enum semantics — critical clarifications:**

- **A9 "mixed"** = multi-sector study spanning **≥2 distinct industrial sectors** (e.g., a review of energy management across automotive AND food processing). NOT to be used for multi-site single-organisation cases (use A1c `multi_site=true` for that). NOT to be used for multi-process-type within one facility (use B4 sub-system scope).
- **A11 "linear regression"** = exactly ONE independent variable. Multiple regression = ≥2 IVs, including stepwise selection. If the paper uses regression but doesn't specify whether 1 or multiple IVs, default to "multiple regression" (more common in this literature).
- **A11 "simple intensity ratio" (v2.2)** = a single-denominator unfitted normalisation: e.g., "kWh per unit produced" reported as a KPI without regression fitting. Distinct from `SEC mean` (which averages SEC across observations) and from `linear regression` (which fits a model with intercept/coefficients). Use this for Tier-1 KPI papers like simple intensity tracking.
- **A11 "composite index" (v2.2 TIGHTENED)** = explicit **weighted** aggregation of ≥2 sub-metrics that **predict or normalise energy consumption**. A simple mean of one metric → use `SEC mean`. **Decision-support scoring (MCDM/AHP/TOPSIS/Fuzzy/project ranking) that produces a comparative or normative score — NOT an EnPI — is NOT a composite index here. Code it in A11b complementary_methodologies instead.**
- **A11 "SEC mean"** = specific energy consumption (energy / production unit) averaged across observations or sites; primary methodological frame is the SEC indicator itself, not a regression around it.
- **A11 "change-point or SPC"** = CUSUM, EWMA, F-test for variable selection, PELT, dissimilarity metrics, control charts.
- **A11 "process integration"** = pinch analysis, heat integration, exergy analysis (when used as the **primary** modelling framework). When used **alongside** a regression model, code regression in A11 and pinch/exergy in A11b complementary_methodologies.
- **A11 "not applicable"** = paper is ineligible OR paper is eligible but does not present any modelling type at all (rare, but allowed). Mutually exclusive with all other A11 values.
- **A10a/b/c "other-named"** = include the framework name in evidence (e.g., "other-named: ISO 50015" / "other-named: California Title 24"). Tracking enables future enum extension.
- **A8 "verbatim from paper" rule (v2.1 — minor fix):** the sector_of_activity value MUST appear verbatim (or be a minimal normalisation) in the source text. The verifier checks this. Extractors must NOT inject external knowledge (e.g., "medical devices" when the paper says "life sciences").

### 6.2 Level B variables — applied only to Level 3B papers — v2.1 REWORK

These support SQ2-4.

| # | SQ | Variable | Type | Values |
|---|---|---|---|---|
| B1 | 1 | `normalisation_variables` | list of free strings | RVs (independent variables) used in baseline/indicator. EXCLUDE the dependent variable (energy use). |
| B2a (v2.1 new — minor) | 1 | `baseline_period_start` | string \| null | E.g., "2018-01"; "not reported" if absent. |
| B2b (v2.1 new — minor) | 1 | `baseline_period_end` | string \| null | E.g., "2019-12"; "not reported" if absent. |
| B2c (renamed from B2) | 1 | `baseline_construction_method` | string (free) | 1-3 sentences describing how the model was constructed. |
| B3 (v2.1, v2.2 broadened) | 1 | `validation_types` | enum (multi) | empirical (held-out measured data) / simulation (synthetic) / theoretical (analytical only) / **statistical (any inferential test of model fit/significance — R², p-value, F-test, t-test, chi², R-critical, AIC/BIC, cross-validation, residual analysis)** / none reported |
| B4 (v2.1 expanded — M7) | 1 | `scale_of_application` | enum (single) | equipment / `sub-system / utility system` / unit / facility / organisation |
| B4b (v2.1 new — M7) | 1 | `scope_description` | string (free) | E.g., "water-steam circuit of the SAP plant"; concrete narrative of what was studied. |
| B5 (v2.1 disambiguated — M5) | 2 | `identifies_model_limitations` | bool | Y/N — paper EXPLICITLY identifies limitations **of the EnPI/EnB MODEL ITSELF** (applicability bounds, residual issues, validation gaps, conditions under which the model breaks). NOT operational/practical implementation barriers — those go to B14. |
| B6 | 2 | `specific_limitations` | enum (multi) | non-stationarity / fouling / catalyst deactivation / feedstock variability / other (specify in evidence). Empty list if B5 is false. |
| B7 | 2 | `proposes_treatment_mechanism` | bool | Y/N — proposes a way to handle the identified model limitations, even if the adaptation itself is left for future work. |
| B8 | 3 | `proposes_adaptations` | bool | Y/N — proposes **concrete** methodological adaptations for continuous process application. |
| B9 | 3 | `adaptation_types` | enum (multi) | dynamic time window / segmented baseline / hybrid physical model / other (specify in evidence). Empty list if B8 is false. |
| B10 | 3 | `normative_framing_of_adaptations` | enum (single) | ISO 50001/50006 explicit / implicit / absent |
| B11 | 4 | `empirical_refinery_application` | bool | Y/N — model empirically applied to a real refinery or petrochemical plant (not future case). |
| B12 (v2.1, v2.2 strict) | 4 | `data_type` | enum (single, STRICT — no free-form suffixes) | continuous time series / audit data / simulation / unspecified or not stated. Annotations (e.g. "mandatory audit under Italian D.Lgs. 102/2014") go to B4b scope_description, NOT into this value. |
| **B13a (v2.1 NEW — M3)** | 4 | `model_parameters_reported` | list of free strings | Reported model parameters: regression coefficients (e.g., "0.348986"), intercepts, dummy variable coefficients, fitted constants. NOT goodness-of-fit metrics. |
| **B13b (v2.1 REPLACES B13; v2.2.1 enforcement erratum)** | 4 | `performance_metrics_reported` | list of structured objects | Model-output shape: `[{metric, value, unit, period_or_context, evidence_quote, page}]`, optionally with `non_contiguous_evidence`. Metric is one of: R² / adjusted R² / RMSE / MAE / MAPE / CV-RMSE / % energy savings / F-statistic / p-value / other-named. **NOT** model parameters. Empty list if no fit metrics reported (note: this is common for descriptive case studies). |
| B14 (v2.1 disambiguated — M5) | 4 | `implementation_barriers` | list of free strings | **Practical/operational obstacles** to implementing the proposed energy-saving measures or the EnMS in general. E.g., "lack of instruments", "staff training", "regulatory delay", "difficulty to maintain equipment". NOT limitations of the model itself — those are B5. |

For B13b, the model output retains the full outer field envelope and each
metric also carries its own nested quote/page so every reported number is
independently traceable. The human reviewer form deliberately displays only
the four analytical properties (`metric`, `value`, `unit`,
`period_or_context`); the reviewer's quote, page, and rule are stored
separately in `reviewer_evidence`. This is a representation difference, not a
difference in the evidence requirement.

**v2.1 critical disambiguation B5 vs B14 — examples:**

| Sample paper claim | Goes to B5 (model limitations) | Goes to B14 (implementation barriers) |
|---|---|---|
| "Our regression overfits during shutdown periods" | ✓ B5 (model behaviour limitation) | ✗ |
| "Multipass heat exchangers are difficult to maintain" | ✗ | ✓ B14 (operational barrier to the proposed solution) |
| "The SEC indicator does not account for product mix changes" | ✓ B5 (model coverage limitation) | ✗ |
| "Staff lacks training to interpret the dashboards" | ✗ | ✓ B14 (organisational barrier) |
| "The baseline assumes stationarity which breaks for catalyst-deactivation periods" | ✓ B5 (model assumption limitation) | ✗ |
| "Steam and water systems lack instruments needed for proper definition" | ✗ | ✓ B14 (data-availability barrier) |

The **same text item must map to exactly ONE field**.

**v2.2 default rule for dual-nature statements:** if the statement directly **constrains model construction or validity** (e.g., "instruments needed for proper definition are lacking" — without these instruments the baseline cannot be built), default to **B5** (model limitation). If the statement describes a practical obstacle that does not block model construction but blocks the implementation of energy-saving measures, default to **B14** (operational barrier). Where genuinely ambiguous, default to **B14** (broader category).

### 6.3 Field envelope — v2.1 MANDATORY with grounding check (C3 critical fix; v2.2 normalization + page convention)

Every AI-extracted field carries this envelope:

```json
{
  "value": <typed value or null>,
  "evidence_quote": "<literal substring from PDF>" | ["<sub1>", "<sub2>"] | "not found in source",
  "page": <int> | null,
  "non_contiguous_evidence": <bool, default false>,
  "confidence": <0.0-1.0> | null
}
```

**v2.2.1 normalization policy for the literal-substring check** (expanded from v2.2 after the re-pilot detected 18 encoding-artefact grounding failures across 7 papers). The verifier applies these normalizations to BOTH the `evidence_quote` and the target page text before comparison, in this order:

1. **Control-character strip**: remove characters in `U+0000–U+001F` *except* `\n` (LF) and `\t` (TAB). PDF extractors (notably Symbol-font fallbacks) often emit `U+0003` (ETX) between glyphs.
2. **Soft-hyphen removal**: drop all `­` (U+00AD).
3. **Line-break hyphenation join**: regex `-\s*\n\s*` → `''` (i.e., `vari-\n  ables` → `variables`). This is v2.2.1's largest single fix — accounted for 10/19 grounding failures in the re-pilot.
4. **Ligature unification (expanded)**:
   - `ﬁ ﬂ ﬀ ﬃ ﬄ` (U+FB00–FB04) → `fi fl ff ffi ffl`
   - **v2.2.1**: `ϐ` (U+03D0 GREEK BETA SYMBOL) → `fi` (PDF extractors sometimes substitute Greek-beta for fi/fl when the font's Symbol fallback is broken — accounted for 7/19 grounding failures in the re-pilot)
   - The verifier MUST also try the alternative `ϐ` → `fl` if the `fi` substitution fails to ground; whichever succeeds wins
5. **Dash unification**: `– — ‒ −` (U+2013/2014/2012/2212) → `-`.
6. **Quote unification**: `" " „ ' ' ‚ ¶ ¹` → `" '` (i.e., curly/typographic single and double quotes, plus the PDF artefacts `¶` U+00B6 and `¹` U+00B9 that some extractors emit instead of curly apostrophes).
7. **Whitespace collapse**: any whitespace run → single space.
8. **Lowercase**.

The verifier then uses `rapidfuzz.fuzz.partial_ratio` with length-sensitive thresholds (≥95 / ≥90 / ≥85 for short/medium/long quotes).

**Future-proofing note**: the verifier should log every grounding failure with the failing substring and the normalised target page text, so that systematic encoding gaps surface as patterns rather than as silent rejections. Any encoding artefact responsible for >2 failures in a corpus warrants extending the normalization spec.

**v2.2 non-contiguous evidence** (v2.2.1 page-locality clarified): `evidence_quote` may be a LIST of 2-3 literal substrings if the supporting text is split across non-contiguous PDF regions (figure caption interruption, footnote, page break, etc.). In that case:

- Set `non_contiguous_evidence: true`.
- `page` MUST be a LIST of integers (one per substring), aligned positionally to the substrings — `evidence_quote[i]` is located on page `page[i]`.
- Each substring in the list must individually pass the substring check against its claimed page text.

For single-substring evidence (the common case): `evidence_quote` is a plain string, `page` is a plain integer, `non_contiguous_evidence` is `false` (default).

**v2.2 page convention:** `page` (when integer) is the integer index into the `pdf.pages` array (PDF physical page, 1-indexed). It is NOT the printed journal page number, NOT the page label, NOT the issue/volume page. Stage 0 §8.4 produces `pdf.pages = [{page: 1, text: "..."}, {page: 2, text: "..."}, ...]` and the agents and verifier both use this index.

**v2.2.1 JSON encoding lock (eliminates the v2.2 ambiguity that paper 472535592 surfaced):**

- `evidence_quote`: plain JSON string, OR plain JSON array of strings (when `non_contiguous_evidence=true`), OR JSON `null`. **Never** a JSON-string containing a stringified JSON value.
- `page`: plain JSON integer, OR plain JSON array of integers aligned to `evidence_quote` array (when `non_contiguous_evidence=true`), OR JSON `null`.
- `non_contiguous_evidence`: plain JSON boolean. Required field; default `false`.
- `confidence`: plain JSON number `[0.0, 1.0]` OR JSON `null`.

Records that violate the encoding lock fail post-extraction schema validation (§8.9 / §12.4 flag taxonomy).

**v2.2 evidence_quote for "none" / empty multi-select values:** when a field's value is `"none"` (e.g., `ems_standard: ["none"]`) or an empty multi-select (e.g., `specific_limitations: []`), `evidence_quote` may be:
- `null` (preferred when the absence is structural to the paper); OR
- A literal substring that explicitly states the absence (e.g., `"no goodness-of-fit metrics reported"`, `"the paper does not cite ISO 50001"`).

It MUST NOT be a descriptive quote about the excluded methodology (e.g., quoting a sentence describing pinch analysis to justify why `complementary_methodologies: ["none"]` was chosen).

**v2.1 changes (critical fix C3):**

**v2.1 changes (critical fix C3):**

1. `evidence_quote` is **MANDATORY** for every non-null `value`. The quote MUST be a literal substring of the extracted PDF text. The form pilot detected a hallucination where the extractor cited "Figure 4 r-squared values 0.53 and 0.17 for CHW vs CDD" — strings that did not appear in the extracted text. Without programmatic grounding, this type of error is invisible.
2. `page` is the integer page number where the quote was found. If page cannot be confirmed at extraction time, set to null (Stage 4 §12.2 grounding will verify and set `page_unverified=true` if the quote matches on a different page).
3. Stage 4 §12.2 **evidence-grounding check is OBLIGATORY** for every field with a non-null `value`. Procedure: normalise both (dehyphenate, collapse whitespace, lowercase), fuzzy-match `evidence_quote` against the claimed page with length-sensitive threshold (≥95 for short quotes, ≥90 medium, ≥85 long). If no match anywhere in the document → invalidate the field (set value=null), flag `evidence_not_grounded`, route paper to `needs_review.md`.
4. The AI pipeline (Stage 1, 2, 3) ALWAYS uses the full envelope. The reviewer's blind manual extraction template (§13.2 only) may use `value`-only for typing convenience.
5. `confidence` remains a soft annotation only — it is **not** used as an automatic gate. Gates are: grounding success, cross-checks, deterministic flags, and pilot/audit comparison. Do not introduce confidence-based auto-flagging.

If a field cannot be determined:
- `value = null`
- `evidence_quote = "not found in source"`
- `page = null`
- `confidence = null`

**Discipline:**
- Never guess.
- Never paraphrase the quote — must be literal substring of extracted text.
- Never cite figure/image content unless the figure's text is actually surfaced in extracted text. If the paper has a relevant figure but its content is image-rasterised, the field stays null (or flag `evidence_in_figure_only` if you can identify the figure reference).
- For multi-select fields: one `evidence_quote` per selected value OR a single quote that supports all selected values together.

---

## 7. Architecture — five stages (C-2.3, dual-model)

> **Updated for Protocol C-2.3 (2026-07-14).** Stages 1–3 run **twice — once per
> model family** through independent clean Claude Code and Codex/ChatGPT
> application sessions (article-level agents; deterministic batch state; no
> model-invocation runner; sampling provider-managed); Stage 4
> reconciles the two runs field-by-field and routes human effort per
> `VALIDATION_PROTOCOL_C.md`. The single-model diagram this section carried
> until 2026-07-10 (with a 20% random audit and a "no AI-AI redundancy" rule)
> described the pre-C design and contradicted §0.2/§0.3/§2 — it is superseded.

```
Stage 0  →  Deterministic preparation (Python, no LLM)
              ├─ bibliographic fields from CSV
              ├─ page-preserving text extraction
              ├─ retraction scan
              ├─ text-quality gate (chars/page, OCR flag)
              ├─ doc-type / year / language eligibility gates
              └─ output: per-paper bundle

Stage 1  →  Eligibility + Level 3B classification   [2 LLM families, subscription surfaces]
Stage 2  →  Level A judgment fields                 [2 LLM families, subscription surfaces]
Stage 3  →  Level B holistic extraction (3B only)   [2 LLM families, subscription surfaces]

Stage 4  →  Reconciliation + validation (C-2)       [Python + reviewer]
              ├─ merge stages per model; field-level reconciliation
              │    (reconcile.py) → concordant / divergent partition
              ├─ resolve methodological eligibility first; structural nulling
              │    of Level A only when ineligibility is resolved
              ├─ evidence-grounding check, full §6.3 normalisation (grounding.py)
              ├─ cross-checks (e.g. level_3b ⇒ A9 ∈ {continuous, mixed})
              ├─ FN candidate-union census + closure (fn_hunt.py, C-2 §3-Step-4)
              ├─ blind-first Tier-1 adjudication; branch-prescribed Tier-2 treatment
              ├─ SRS n=40 audit + exhaustive censuses (audit_sampler.py, C-2 §4)
              └─ per-field validation report (residual_report.py, C-2 §5)
```

**Where redundancy lives (C-2.3):** inter-model divergence is the routing signal —
divergent consequential fields go to blind-first human adjudication, the
concordant tail to the SRS audit and censuses. Inter-model agreement is
**never** a reliability metric (§0.3); the human remains the sole source of
adjudicated values. Targeted human evidence is either a grounded quote +
physical page or, only for absence-like values, a full-text-absence rationale
without an invented quote/page. Reviewer edits are atomically autosaved and
browser-recoverable; reveal and finalisation fail closed after a save failure.

---

## 8. Stage 0 — Deterministic preparation

**Pure Python. No LLM.** Implement in `output/stage0_prepare.py`. Run once before any LLM extraction; re-run when the CSV updates or new PDFs arrive in `data/pdfs/`.

This stage now includes the **data-quality safeguards** added after the v2.0 preflight audit (see §0 change log and `data/data_quality_report.md`). The audit pre-resolved current issues by quarantine; Stage 0 must enforce the same checks going forward, especially as new PDFs from the redownload queue arrive.

For each paper in scope (Level 3 from CSV):

### 8.1 Bibliographic fields (always determine first)

From `data/articles.csv` by `key`: populate A1-A6, A12 deterministically. Parse the `notes` field to extract:
- Rayyan decision (`Included` / `Maybe`).
- Source string indicator: look for `STRING-A` / `STRING-B` markers in `notes`, or infer from search-strategy tagging if available. If absent and the paper is not snowballed, set `source_string = null` and flag.

### 8.2 Excluded-duplicates check

Load `data/excluded_duplicates.json`. If the paper's `key` appears as an `excluded` entry, **do not proceed**. Skip silently in the pipeline (record in `output/stage0/{key}.json` with `excluded_as_duplicate: true` and the primary key for traceability). Three keys are currently excluded (see report §2.3).

**Important:** the 3 dedup secondary PDFs have already been physically moved out of `data/pdfs/` to `data/pdfs_quarantine/rayyan_dedup/`. This means `pdf.available` for these keys will be `false`, but **the dedup check must still execute first** so the bundle records `excluded_as_duplicate: true` (the PRISMA flow needs this provenance — "3 removed at full-text as duplicates", not "3 not yet downloaded"). The order is: enumerate Level 3 keys from CSV → check `excluded_duplicates.json` → only then check PDF presence and proceed.

### 8.3 PDF presence

If `data/pdfs/{key}.pdf` does not exist, the paper is not in the initial
retrieval pipeline. Record `pdf.available = false` and do not proceed to text
extraction. This applies to the 137 records in the frozen non-retrieved set,
including the 2 unresolved wrong-content keys. For the other 7 wrong-content
keys, use the correct replacement in `data/pdfs/`; never fall back to the
quarantined original.

### 8.4 Text extraction — fallback chain

Use the following backends, in order. Stop at the first that produces text passing the text-quality and garbled-detection checks (§8.5, §8.7). Record the backend used in `pdf.extraction_backend`.

1. **OCR-recovered text shortcut**: if `data/ocr_recovered/{key}.txt` exists, use that file directly (no PDF parsing). The local store contains OCR-recovered text for 5 papers. Set `extraction_backend = "ocr_recovered_preflight"`. Note: this file has **no page boundaries**; treat the entire text as page 1 for grounding purposes and document the locator limitation. Future Stage 4 grounding for these 5 papers will accept page-unverified evidence by default.

2. **pymupdf** (`fitz`) page-preserving:
   ```python
   import fitz
   doc = fitz.open(pdf_path)
   pages = [{"page": i+1, "text": p.get_text()} for i, p in enumerate(doc)]
   ```
   Set `extraction_backend = "pymupdf"`. This is the preferred backend.

3. **pdfplumber** (fallback if pymupdf produces garbled text per §8.7):
   ```python
   import pdfplumber
   with pdfplumber.open(pdf_path) as pdf:
       pages = [{"page": i+1, "text": p.extract_text() or ""} for i, p in enumerate(pdf.pages)]
   ```
   Set `extraction_backend = "pdfplumber"`.

4. **Tesseract OCR** (fallback if both above produce garbled text). For each page, render at 250 dpi to PNG (in a tmp dir inside the working directory — macOS sandboxes `/tmp` and tesseract can't read from there), then run `tesseract <png> - -l eng`. Concatenate per-page outputs. Set `extraction_backend = "tesseract_ocr"`. Slower (~3-5 s/page) but recovers glyph-remap PDFs.

5. **Quarantine**: if all three above fail to produce clean text (garbled detection still triggers), move the PDF to `pdfs_quarantine/unreadable/{key}.pdf` and add the key to `redownload_queue.json` (with reason `extraction_failed_all_backends`). Do not proceed.

### 8.5 Text quality gates (legacy, kept)

After extraction:
- `mean_chars_per_page` — flag `image_only` if < 100.
- `total_chars` — flag `truncated_or_preview` if < 5 000.
- `has_extractable_text` boolean = (mean ≥ 100 AND total ≥ 5 000).

`truncated_or_preview` is not auto-exclude — paper continues to Stage 1 with the flag; Stage 1 may return inconclusive eligibility, routing to `needs_review.md`.

### 8.6 Retraction scan

Scan first 2 pages and last 2 pages of the extracted text for case-insensitive markers: `RETRACTED`, `Retraction Notice`, `This article has been retracted`. Flag matches; retraction is a deterministic exclusion (paper does not enter LLM pipeline). `WITHDRAWN` is intentionally excluded as a marker because in this energy-management corpus it commonly refers to the EN 16001 standard being withdrawn in favour of ISO 50001, producing false positives.

### 8.7 Garbled detection — composite heuristic

After extraction, before accepting the text:
1. Take the first 5 000 chars of extracted text as a sample.
2. Compute:
   - `ascii_letter_fraction` = chars matching `[a-zA-Z]` over sample length.
   - `common_word_matches` = count of occurrences of common English words in the sample lowercase: `{the, of, and, in, to, is, for, a, that, with, on, this, by, as, are, be, an, or, we, was, were, have, has, which, from, at, it, not, but, energy, system, process, model, data, based, study, results, analysis, performance, method, industrial}` (calibrate as needed; common research text scores 50+).
3. Garbled detection rule (BOTH conditions must hold to flag — single-condition rules give false positives on figure-heavy PDFs):
   - `ascii_letter_fraction < 0.45` AND `common_word_matches < 8` → `garbled_bytes` (byte-level corruption)
   - OR `ascii_letter_fraction >= 0.45` AND `common_word_matches < 8` → `garbled_glyphs` (encoding-shift / glyph remap; OCR will fix this)
4. If garbled, do not accept the text from this backend; advance to the next backend in §8.4. Only the final-backend failure triggers quarantine.

### 8.8 Deterministic eligibility gates

- `doc_type_eligible`: `document_type` in allowed enum.
- `year_eligible`: `year >= 1996` OR `via_snowballing == True`.
- `language_eligible`: `language == "English"` (heuristic: title and abstract are in English; manual override flag supported via CSV column `language_override`).

### 8.9 Title/DOI vs metadata cross-check (wrong-PDF detection)

After extraction, before proceeding:
1. Fuzzy-match the expected title (from `articles.csv`) against the concatenated first two pages using `rapidfuzz.fuzz.partial_ratio`; normalise both (lowercase, collapse whitespace).
2. Grep for the expected DOI across the full extracted text.
3. Decision:
   - title match >= 70 OR DOI found → accept as the correct paper.
   - title match < 70 AND DOI not found AND text is extractable (not image_only) → flag `wrong_pdf_likely`. Do **not** proceed to LLM extraction. Add to `needs_review.md` and the reviewer manually decides whether to move the PDF to `pdfs_quarantine/wrong_pdf/` and add to `redownload_queue.json`, or override the flag if the layout is unusual (e.g. journal page starts with refs of the prior article — see preflight report §2.5 for an example of the false positive in 472535371).

This is the structural check missing from the original v2.0 Stage 0 design and added after the preflight audit found 9 wrong-content PDFs that would otherwise pass to the LLM with confident but false extractions.

### 8.10 Bundle output

Write to `output/stage0/{key}.json`:

```json
{
  "key": "rayyan-NNNNNNNNN",
  "metadata": {
    "paper_id": "...",
    "authors": "...",
    "year": 2024,
    "title": "...",
    "source": "...",
    "document_type": "journal article",
    "source_string": "A",
    "rayyan_decision": "Included" | "Maybe"
  },
  "pdf": {
    "available": true,
    "path": "data/pdfs/rayyan-NNN.pdf",
    "extraction_backend": "pymupdf",
    "pages": [{"page": 1, "text": "..."}, ...],
    "text_quality": {
      "mean_chars_per_page": 2400,
      "total_chars": 38400,
      "has_extractable_text": true,
      "ascii_letter_fraction": 0.72,
      "common_word_matches": 87
    },
    "metadata_match": {
      "title_match_score": 92,
      "doi_found_in_text": true,
      "wrong_pdf_likely": false
    },
    "md5": "abcdef0123..."
  },
  "deterministic_gates": {
    "doc_type_eligible": true,
    "year_eligible": true,
    "language_eligible": true,
    "not_retracted": true,
    "extractable_text": true,
    "passes_all_deterministic_gates": true
  },
  "flags": {
    "image_only_pdf": false,
    "retracted": false,
    "via_snowballing": false,
    "excluded_as_duplicate": false,
    "garbled_bytes": false,
    "garbled_glyphs": false,
    "wrong_pdf_likely": false,
    "truncated_or_preview": false
  }
}
```

A paper does **not** proceed to Stage 1 if any of:
- `passes_all_deterministic_gates == false`
- `excluded_as_duplicate == true`
- `wrong_pdf_likely == true` (route to `needs_review.md` for reviewer adjudication)
- garbled_bytes/glyphs flagged AND all extraction backends exhausted (quarantine + redownload queue)

Truncated or via_snowballing flags do not block Stage 1 — they pass with the flag attached.

---

## 9. Stage 1 — Eligibility + Level 3B classification

**Goal:** for papers that passed Stage 0 deterministic gates, determine (a) methodological eligibility, and (b) Level 3B classification.

**Design:** 1 LLM agent per paper, **provider-managed sampling**. Redundancy comes from human review of Maybe-papers, Level-3B-flagged papers, and ineligible-flagged papers — not from a second AI call.

### System prompt — v2.1

Write this to `prompts/stage1_system.md` and commit (git tag `v2.1-schema-rework`):

```
You are a methodology-aware scientific reviewer assisting a PRISMA-ScR
scoping review on energy performance measurement models under the
ISO 50001/50006 normative framework.

The review distinguishes two sets within Level 3:
  - Level 3A: all eligible records, for bibliometric analysis.
  - Level 3B: subset of Level 3A where application is explicitly in
    a continuous process industry, for narrative synthesis.

Document-type, language, publication-year, and retraction status have
ALREADY been verified by deterministic checks. Trust that the paper
has passed those gates.

YOUR TASK — three judgements per paper:

  1. METHODOLOGICAL ELIGIBILITY (Y/N) — v2.3 registered threshold:
     eligible iff the paper PRESENTS, PROPOSES, EVALUATES, or
     CRITIQUES an EnPI and/or EnB model with sufficient detail to
     identify and characterise it (WHAT is measured/normalised AND
     at least one of: variables, functional form, construction/
     estimation approach). Critiques, conceptual proposals, unfitted
     and unvalidated models are ELIGIBLE — validation status is an
     extracted variable, never a gate. (Authoritative wording +
     review/synthesis decision tree: §5.2; prompt of record:
     prompts/stage1_system.md @ v2.3.1-operational, with the Stage-1 policy
     inherited byte-for-byte from v2.3-eligibility-registered.)

     INELIGIBLE if mentions EnPI/EnB only incidentally, OR if
     exclusive focus is one of: residential buildings without
     industrial component / government energy policy without
     organisational dimension / purely economic energy management
     without performance measurement / ISO 14001/9001 without
     relation to ISO 50001 or energy management.

     INELIGIBLE also if paper presents a tool, framework, software,
     or maturity assessment without any EnPI/EnB measurement-model
     content.

  2. PAPER TYPE (single enum, applies to all eligible papers):
     - "single applied case"          (one paper, one organisation/site)
     - "multi-case study"             (multiple cases in one paper)
     - "review/synthesis"             (review of >=3 prior applications)
     - "maturity model or framework"  (qualitative assessment tool)
     - "methodological/theoretical"   (model construction without empirical case)
     - "other"

  3. LEVEL 3B CLASSIFICATION (Y/N) — is the application context of
     the paper EXPLICITLY in a continuous process industry?

     CONTINUOUS PROCESS INDUSTRIES (in-scope, non-exhaustive):
     - Petroleum refining
     - Petrochemicals (organic chemistry, polymers, etc.)
     - Cement
     - Pulp & paper
     - Steel and other primary metals continuous production
     - Continuous chemical production (sulfuric acid, ammonia,
       fertilizers, etc.)
     - Industrial gases (air separation, hydrogen, nitrogen)
     - Glass (continuous melting / float lines)

     This is the pre-specified main list (v2.3). Unlisted sector that
     appears continuous-flow → set level_3b=false and describe the case
     in reviewer_notes for human decision (exploratory unless a
     documented corpus decision adds it). NEVER classify by
     non-stationarity/fouling/drift — those are extracted outcomes
     (B5/B6), not membership criteria.

     OUT OF SCOPE:
     - Discrete manufacturing (parts, assembly, batch production)
     - Services, offices, buildings
     - Batch-mode chemical production
     - Agricultural / mining (unless processing is continuous)

     EXPLICIT means: the paper applies, validates, or empirically
     demonstrates the model in one of these sectors. "Could be
     applied to", "future work on", "discussed in relation to" is
     NOT enough.

EVIDENCE REQUIREMENT (MANDATORY, v2.1 critical fix C3):

For every determination, you MUST provide:
- evidence_quote: a LITERAL SUBSTRING of the source text supporting
  the decision. Must be possible to grep verbatim against the PDF
  text. Do NOT paraphrase. Do NOT cite figure/image content unless
  the figure's text appears in extracted text.
- page: the integer page number where the quote appears.
- confidence: [0.0, 1.0], soft annotation, not used as automatic gate.

If no such evidence exists:
  value = null
  evidence_quote = "not found in source"
  page = null
  confidence = null

NEVER guess. NEVER fabricate quotes. The verifier will programmatically
check that every evidence_quote is a substring of the extracted PDF
text; mismatches invalidate the field.

OUTPUT — single JSON object, no prose around it:

{
  "methodological_eligibility": {
    "value": true | false,
    "evidence_quote": "<literal substring>" | "not found in source",
    "page": <int> | null,
    "confidence": 0.0-1.0 | null
  },
  "ineligibility_reason": "<short reason or null>",
  "paper_type": {
    "value": "<one of the 6 enum values>",
    "evidence_quote": "<literal substring>" | "not found in source",
    "page": <int> | null,
    "confidence": 0.0-1.0 | null
  },
  "level_3b": {
    "value": true | false,
    "evidence_quote": "<literal substring naming the sector>" | "not applicable" | "not found in source",
    "page": <int> | null,
    "confidence": 0.0-1.0 | null
  },
  "notes": "<optional brief note on ambiguity, max 200 chars>"
}

If methodological_eligibility.value is false, then level_3b.value
MUST be false, level_3b.evidence_quote = "not applicable".

If methodological_eligibility.value is false, the downstream Stage 2
will be skipped and Level A fields will all be null in the consolidated
record (per the v2.1 critical fix C2 scoping rule).
```

### User message template

```
Paper key: {key}
Title: {title}
Authors: {authors}
Year: {year}
Source: {source}
Document type: {document_type}

Full text follows, with [PAGE N] markers between page boundaries.

---
[PAGE 1]
{text of page 1}

[PAGE 2]
{text of page 2}

...
---
```

### Output

Write to `output/stage1/{key}.json`.

### Human review routing (deterministic, after AI output)

The paper goes to `output/needs_review.md` for mandatory human adjudication if **any** of:
- AI says ineligible (**never auto-exclude**).
- AI says Level 3B (conservative — Level 3B is small and consequential; scope creep contaminates SQ2-4).
- Rayyan decision is "Maybe" (reviewer's prior uncertainty).

Provisional accept (no human review until Stage-4 validation) only when: **both models** say eligible AND agree on all Tier-1 fields AND Rayyan "Included" AND **both models** say not Level 3B. Any Tier-1 inter-model divergence overrides this and routes to blind-first adjudication (C-2 §3-Step-3).

### Asymmetric routing — explicit declaration

This routing protects against **false-positive Level 3B** (a paper wrongly classified into 3B): every AI-flagged 3B goes to human review, preventing scope creep into SQ2-4. The **false-negative Level 3B** risk (a genuine continuous-process paper both models miss) is attacked under C-2 by the **FN candidate-union census** — model flags ∪ deterministic lexicon over full text ∪ counter-anchored recall pass, human-emptied with a lexicon-expansion closure rule (`VALIDATION_PROTOCOL_C.md §3-Step-4`) — plus the exhaustive census of concordant 3B=true cells and the upstream L1/L2 exclusion audit (§3-Step-4b). The §12.3 cross-check (`level_3b=true ⇒ A9 ∈ {continuous process, mixed}`) remains a supplementary consistency gate.

The residual risk — a continuous-process paper invisible to all three detectors — is declared, not quantified (C-2 §9), and must be acknowledged in the methodological annex.

---

## 10. Stage 2 — Level A judgment fields (Level 3A)

**Goal:** extract non-deterministic Level A fields (A7-A11) for all eligible papers.

**Design:** 1 LLM agent per paper, **provider-managed sampling**.

### System prompt — v2.1

Write this to `prompts/stage2_system.md`:

```
You are assisting a PRISMA-ScR scoping review on energy performance
measurement models under ISO 50001/50006. The paper you are reading
has already been determined eligible (methodological_eligibility=true).
If you receive this prompt for a paper with eligibility=false, do NOT
proceed — return all fields as null with evidence_quote="not applicable
(paper is ineligible)" (per the v2.1 critical fix C2 scoping rule).

Your task is to extract Level A charting variables — bibliometric
judgment fields supporting sector and normative-context distribution
analysis (SQ1).

For each field, provide value, evidence_quote (LITERAL SUBSTRING of
the PDF text), page (integer), and confidence [0.0, 1.0].

  A1c. multi_site — bool. True if the paper studies a single
      organisation across >=2 sites; false otherwise. Evidence quote
      must explicitly name "multiple sites", "N sites", or
      equivalent.

  A7. country_region — country or region where the empirical case
      study, validation, or implementation took place. Free text,
      verbatim or minimally normalised from the paper. If multiple,
      list comma-separated. If purely theoretical with no geographic
      anchor, value="not applicable".

  A8. sector_of_activity — VERBATIM (or minimal normalisation) from
      the paper's own framing. NEVER inject external knowledge.
      Example: if the paper says "life sciences", code "life sciences"
      — NOT "medical devices" (even if you know the company is in
      medical devices). The verifier checks that the value string
      appears in the source text.

  A9. type_of_organisation — single value from:
      - "continuous process" (refining, petrochemicals, cement,
        pulp & paper, steel, continuous chemical production
        (sulfuric acid, fertilizers, etc.), industrial gases,
        other 24/7 continuous-flow industrial sectors)
      - "discrete manufacturing" (parts, assembly, batch production)
      - "services" (offices, retail, hospitality, healthcare admin)
      - "buildings" (residential, commercial, institutional buildings
        without industrial production)
      - "mixed" (multi-sector study spanning >=2 distinct industrial
        sectors. NOT for single-organisation multi-site cases — use
        A1c multi_site=true for that)
      - "not specified" (purely methodological, no application
        context, or paper_type="methodological/theoretical")

  A10a. ems_standard — multi-select (zero or more) from:
      - "ISO 50001"
      - "ISO 50002"
      - "ISO 50006"
      - "other-named"  (include name in evidence, e.g.,
        "other-named: ISO 50015")
      - "none"  (no energy-management standard cited)

  A10b. mv_protocol — multi-select from:
      - "IPMVP"
      - "ASHRAE 14"
      - "SEP M&V"
      - "BPA MT&R"
      - "ISO 17743"
      - "other-named"  (include name in evidence)
      - "none"

  A10c. regulatory_driver — multi-select from:
      - "EU EED"  (Energy Efficiency Directive, any version)
      - "national audit decree"  (any country)
      - "EU-ETS"
      - "regional regulation"
      - "other-named"
      - "none"

  A11. enpi_enb_model_types — multi-select from:
      - "linear regression"  (single independent variable)
      - "multiple regression"  (>=2 independent variables, includes
        stepwise selection)
      - "physical model"  (first-principles, thermodynamic,
        engineering equations as the model)
      - "ML"  (machine learning: NN, RF, SVM, clustering, DL, etc.)
      - "composite index"  (weighted aggregation of >=2 sub-metrics.
        NOT a simple mean — use "SEC mean" for that)
      - "SEC mean"  (specific energy consumption / production unit,
        averaged across observations or sites; primary indicator)
      - "change-point or SPC"  (CUSUM, EWMA, F-test for variable
        selection, PELT, control charts, dissimilarity metrics)
      - "process integration"  (pinch analysis, exergy as PRIMARY
        modelling framework; if used alongside regression, code
        regression here and pinch in A11b complementary_methodologies)
      - "other"  (specify in evidence)
      - "not applicable"  (paper is eligible but presents no model
        — rare; mutually exclusive with all other values)

  A11b. complementary_methodologies — multi-select (zero or more)
      from:
      - "pinch analysis"
      - "exergy analysis"
      - "thermodynamic modelling"
      - "process flowsheet simulation"
      - "ML ensemble"
      - "none"

      These are methodologies used ALONGSIDE the primary EnPI/EnB
      modelling. If the paper's primary frame is e.g. pinch analysis,
      code it in A11 instead.

EVIDENCE REQUIREMENT (MANDATORY, v2.1 critical fix C3):

Every non-null value carries:
- evidence_quote: LITERAL SUBSTRING of the extracted PDF text. Do
  NOT paraphrase. Do NOT cite figure/image content unless the
  figure's text appears in extracted text. The verifier checks
  evidence_quote against the PDF text via fuzzy substring match.
- page: integer page number.

For multi-select fields: provide ONE evidence_quote per selected
value (or a single quote covering all selected values together).

If a field cannot be determined: value=null, evidence_quote="not
found in source", page=null, confidence=null.

CONFIDENCE — soft annotation. Calibrated, not optimistic.

NEVER inject external knowledge (especially for A8 sector_of_activity).
NEVER fabricate quotes. NEVER cite content from images/figures.

OUTPUT — single JSON object:

{
  "multi_site": {"value": true|false, "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "country_region": {"value": "...", "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "sector_of_activity": {"value": "...", "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "type_of_organisation": {"value": "...", "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "ems_standard": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "mv_protocol": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "regulatory_driver": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "enpi_enb_model_types": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "complementary_methodologies": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0}
}
```

### User message template

As in Stage 1.

### Output

Write to `output/stage2/{key}.json`.

---

## 11. Stage 3 — Level B holistic extraction (Level 3B only)

**Goal:** extract the full Level B schema (B1-B14) for papers classified as Level 3B.

**Design:** 1 LLM agent per paper, **provider-managed sampling**. Level B variables are interpretively coupled (you cannot assess "treatment of catalyst deactivation" without understanding the modelling approach), so the agent reads the paper holistically before populating any field.

### System prompt

Write this to `prompts/stage3_system.md`:

```
You are assisting a PRISMA-ScR scoping review on energy performance
measurement models under ISO 50001/50006. The paper you are reading
has been classified as Level 3B (continuous process industry context).
Your task is to extract Level B charting variables — interpretive
fields supporting SQ2 (limitations), SQ3 (adaptations), and SQ4
(refinery applicability).

These variables are interpretively coupled. Read the paper holistically
before populating any field. Pay particular attention to:
- How the EnPI/EnB model is constructed and validated.
- Whether the authors acknowledge limitations specific to continuous
  process operation (non-stationarity, fouling, catalyst deactivation,
  feedstock variability).
- Whether the authors propose adaptations or modifications.
- The relationship (if any) to ISO 50001/50006 in framing adaptations.
- The data type used and any reported performance metrics.

Extract the following (v2.1 schema):

SQ1 model mapping (Level B detail):

  B1. normalisation_variables — list of free-text strings. The
      INDEPENDENT variables (RVs in ISO 50006 sense) used in
      baseline/indicator construction (e.g., "production tonnage",
      "outdoor temperature", "feedstock composition", "operating
      hours"). EXCLUDE the dependent variable (the energy use being
      modelled). Use paper's own terminology.

  B2a. baseline_period_start — string or null. E.g. "2018-01" or
      "January 2018". If the paper does not specify the baseline
      period, value="not reported".

  B2b. baseline_period_end — string or null. Same convention.

  B2c. baseline_construction_method — free-text description, 1-3
      sentences. Describe how the baseline model was constructed:
      regression approach, time window selection, normalisation
      procedure, variable selection method.

  B3. validation_types — multi-select from:
      - "empirical"   (held-out measured data; independent
        measurements; out-of-sample comparison)
      - "simulation"  (synthetic data from a process simulator)
      - "theoretical" (analytical-only, no data)
      - "statistical" (inferential tests: F-test, t-test, AIC/BIC,
        cross-validation, p-values, residual analysis. NOT
        "empirical" — these are tests of fit, not validation
        against new data)
      - "none reported"

  B4. scale_of_application — single value (v2.1 expanded):
      - "equipment"                 (single piece, e.g., heat exchanger)
      - "sub-system / utility system" (within facility, e.g., water-steam
        circuit, compressed air system, lighting)
      - "unit"                      (process unit, e.g., crude distillation)
      - "facility"                  (entire site/plant)
      - "organisation"              (multi-site or company-wide)

  B4b. scope_description — free-text, verbatim or near-verbatim
      from the paper. E.g., "the water-steam circuit of the
      sulfuric acid plant within the chemical complex".

SQ2 model limitations (v2.1 disambiguated — DO NOT CONFUSE WITH B14):

  B5. identifies_model_limitations — bool. Does the paper EXPLICITLY
      identify limitations of the proposed EnPI/EnB MODEL ITSELF?
      Examples: applicability bounds, residual issues, validation
      gaps, conditions under which the model fails, model
      assumptions that break.

      NOT operational/practical barriers to implementing the
      proposed energy-saving solutions — those go to B14.

      Examples that map to B5:
      - "Our regression overfits during shutdown periods"
      - "The SEC indicator doesn't account for product mix changes"
      - "The baseline assumes stationarity which breaks for
        catalyst-deactivation periods"

      Examples that DO NOT map to B5 (go to B14 instead):
      - "Multipass heat exchangers are difficult to maintain"
      - "Staff lacks training to interpret dashboards"
      - "Steam systems lack instruments needed for definition"

  B6. specific_limitations — multi-select from:
      - "non-stationarity"
      - "fouling"
      - "catalyst deactivation"
      - "feedstock variability"
      - "other" (specify each in evidence)
      If B5 is false, this field is an empty list.

  B7. proposes_treatment_mechanism — bool. Does the paper propose
      a mechanism to handle the identified model limitations (even
      if the adaptation itself is left for future work)?

SQ3 adaptations:

  B8. proposes_adaptations — bool. Does the paper propose CONCRETE
      methodological adaptations for continuous process application?

  B9. adaptation_types — multi-select from:
      - "dynamic time window"
      - "segmented baseline"
      - "hybrid physical model"
      - "other" (specify each in evidence)
      If B8 is false, this field is an empty list.

  B10. normative_framing_of_adaptations — single value:
      - "ISO 50001/50006 explicit" (adaptations explicitly linked
        to ISO standard requirements)
      - "implicit" (adaptations align with ISO concepts but
        standard is not cited in that context)
      - "absent" (adaptations made without reference to ISO
        framework, or no adaptations proposed)

SQ4 refinery applicability:

  B11. empirical_refinery_application — bool. Is the model
      empirically applied to a real refinery or petrochemical
      plant (not just discussed as a future case)?

  B12. data_type — single value (v2.1):
      - "continuous time series"  (explicit time-ordered observations
        with stated granularity)
      - "audit data"              (one-off measurements, audits)
      - "simulation"              (synthetic data from a process simulator)
      - "unspecified or not stated"  (paper does not characterise
        temporal granularity; do NOT infer from plant operating
        mode)

  B13a. model_parameters_reported — list of free-text strings.
      Reported MODEL PARAMETERS only: regression coefficients
      (e.g., "0.348986"), intercepts, dummy variable coefficients,
      fitted constants, slope values. These are characteristics of
      the model itself, NOT measures of its performance. Empty list
      if no parameters explicitly reported.

  B13b. performance_metrics_reported — list of structured objects.
      Reported GOODNESS-OF-FIT or VALIDATION metrics only. Each
      metric is one of: R², adjusted R², RMSE, MAE, MAPE, CV-RMSE,
      % energy savings, F-statistic, p-value, other-named.
        {"metric": "...", "value": "...", "unit": "...",
         "period_or_context": "...", "evidence_quote": "...",
         "page": 1}
      DO NOT populate this with regression coefficients (those go
      to B13a). Empty list if no fit metrics reported.

  B14. implementation_barriers — list of free-text strings.
      PRACTICAL/OPERATIONAL obstacles to implementing the proposed
      energy-saving measures or the EnMS in general. Examples:
      data quality, staff skills, software, organisational,
      regulatory, equipment maintenance. The SAME text item must
      map to either B5 OR B14, not both. If borderline, default
      to B14 (broader category).

EVIDENCE REQUIREMENT (MANDATORY, v2.1 critical fix C3):

Every non-null value carries:
- evidence_quote: LITERAL SUBSTRING of extracted PDF text. Do NOT
  paraphrase. Do NOT cite figure/image content unless the figure's
  text appears in extracted text.
- page: integer page number.

For multi-select: one evidence_quote per selected value, or single
quote covering all selected values together.

For structured objects (B13b): each object has its own evidence_quote
+ page nested.

NEVER guess. NEVER fabricate quotes. The verifier checks every
evidence_quote against the extracted PDF text.

CONFIDENCE — soft annotation. Interpretive fields (B5, B8, B10, B11)
are most prone to ambiguity; confidence reflects that.

OUTPUT — single JSON object with all v2.1 Level B fields keyed
B1-B14, each following the {value, evidence_quote, page, confidence}
envelope.
```

### User message template

As in Stage 1.

### Output

Write to `output/stage3/{key}.json`.

---

## 12. Stage 4 — Consolidation, evidence grounding, audit

**No LLM. Deterministic Python + reviewer time.** Implement in `output/stage4_consolidate.py`.

### 12.1 Merge

Combine Stage 0 metadata + Stage 1 decisions + Stage 2 fields + (if Level 3B) Stage 3 fields into one record per paper. Output: `output/merged.json` (one record per paper) and `output/merged.csv` (one row per paper, multi-select as semicolon-separated values for Excel).

Resolve `methodological_eligibility` before its dependent fields, using a
finalised human value before model concordance. When it resolves to `false`,
set all Level-A fields to `null` with `structural_not_applicable` provenance.
The ancillary, non-analytical `ineligibility_reason` selects the first non-empty
narrative in fixed ChatGPT→Claude order while retaining both raw envelopes. All
other mismatches, especially Level-A differences on eligible papers, remain
unresolved until human adjudication and block final consolidation.

### 12.2 Evidence-grounding check — MANDATORY (v2.1 critical fix C3)

For every extracted field with a non-null `value`:

1. Parse `evidence_quote` (the literal substring) and `page` (integer) from the field envelope.
2. **Normalise** both quote and target text:
   - Dehyphenate (remove end-of-line hyphens reconnecting words).
   - Collapse all whitespace to single spaces.
   - Lowercase.
3. **Match per page**: search the normalised quote in the normalised text of the **claimed page** using fuzzy partial ratio (`rapidfuzz.fuzz.partial_ratio`).
5. **Length-sensitive threshold**:
   - Quote length < 30 chars → require ≥ 95 partial ratio.
   - 30-100 chars → require ≥ 90.
   - > 100 chars → require ≥ 85.
6. **Outcomes**:
   - Match on claimed page → field validated, locator confirmed.
   - Match on a different page → field validated, but locator marked `page_unverified` (record actual page).
   - No match anywhere in the document → **field invalidated**: value set to null, flag `evidence_not_grounded`, paper goes to `needs_review.md`.

This is the structural defence against hallucinated quotes. Without it, the audit trail is decorative.

### 12.3 Cross-checks — v2.1 REVISED (C1 critical fix)

Deterministic consistency checks. Divergence → flag.

**Replaces the v2.0 biconditional rule (which was mathematically wrong — A9='continuous process' is a strict SUPERSET of the Level 3B sector list, so the biconditional produced false positives for every chemicals/industrial-gases paper).**

- **`level_3b == True ⇒ A9 ∈ {"continuous process", "mixed"}`** (one-way implication). If level_3b=true but A9 is something else, flag with both evidences. The inverse (A9="continuous process" but level_3b=false) is **valid and not a flag** — happens legitimately for batch chemicals, services in continuous-process-adjacent industries, etc.
- **`paper_type == "review/synthesis" ⇒ A11 may be empty`** — review papers may legitimately not commit to a single set of model types if they describe many.
- **`methodological_eligibility == False ⇒ ALL Level A fields A7-A11b are null`** (v2.1 C2 critical scoping rule). After eligibility is resolved, Stage 4 enforces this structurally by selecting null Level-A values and retaining any model-populated values only in provenance; unresolved eligibility still blocks consolidation.
- If `B11 empirical_refinery_application == True` then A9 must be "continuous process" and A8 should mention refinery or petrochemical. Mismatch → flag.
- If `B5 identifies_model_limitations == False` then B6 must be empty list. Mismatch → flag.
- If `B8 proposes_adaptations == False` then B9 must be empty list. Mismatch → flag.
- **`B14 implementation_barriers ≠ ∅ AND B5 identifies_model_limitations == True` with overlapping text content** → soft flag for reviewer to disambiguate (per the v2.1 M5 disambiguation rule, the same text item must map to exactly ONE category).

Write report to `output/cross_check_report.md`.

### 12.4 Flag taxonomy (severity ordered for `needs_review.md`)

1. **Stage 0 deterministic gate failure** (retracted, image-only, doc-type ineligible, etc.) → paper does not enter LLM pipeline; manual decision required.
2. **Evidence-grounding failure** on any field → re-extraction or manual entry.
3. **Stage 1 routing flags** (ineligible, Level 3B, Maybe) → mandatory human adjudication before paper proceeds.
4. **Cross-check failure** (§12.3) → human reconciles.
5. **Free text fields** (B2, B13, B14) → always reviewed by reviewer for accuracy and aggregability.
6. **Page unverified** (locator) → optional check; not mandatory.

Note: **low confidence is NOT an automatic flag.** LLM self-confidence is miscalibrated; flagging on it adds noise without adding signal.

### 12.5 Concordant-set audit — SRS + exhaustive censuses (see `VALIDATION_PROTOCOL_C.md §4–§6`, C-2.3, authoritative)

**Supersedes both the random-20% design and the C-1.0 stratified design** (the latter's pooled-Wilson estimator was invalid under deliberate oversampling — see `REVIEW_ROUND2_C2.md`). The C-2 split: rare consequential cells are **censused exhaustively**; the remaining concordant Level-A tail is audited by **simple random sample**, whose plain per-field interval is valid by construction. Summary:

- **Censuses (never sampled):** concordant **Level-3B audited exhaustively**; concordant-excluded papers hit by the **FN candidate-union census** (three detectors: model flags + deterministic lexicon + counter-anchored recall pass, with lexicon-expansion closure rule — `VALIDATION_PROTOCOL_C.md §3-Step-4`); concordant `borderline_review_synthesis_eligibility=true` exhaustively.
- **Sample:** **SRS n=40 papers** (seed 44) over ALL eligible reconciled papers; census/divergence exclusions apply per cell, not per paper; all Level-A fields blind re-extracted via `extraction_tool/`, then diffed.
- **Metric (per field, never pooled):** raw error count **e_v/n_v** (n_v = concordant, evaluable, non-censused cells among the 40 sampled papers) with **exact Clopper–Pearson 95% CI** (marginal per field; zero errors at n_v = 40 ⇒ one-sided 95% upper bound ≈7.2%, rule of three). **No** composite residual estimator, **no** Gwet AC1, **no** capture–recapture, **no** Cohen's κ (power analysis: κ uncertifiable at sustainable n). Pre-registered trigger: absolute **e_v ≥ 3** on a field (n_v reported) → scripted corpus-wide recheck of that field.
- **FN lexicon (canonical list in `output/fn_hunt.py`):** refinery, refining, petrochemical, petroleum, cement, clinker, kiln, **pulp and paper, paper mill** (multi-word — never the bare word "paper"), steel, blast furnace, steelmaking, ammonia, ethylene, olefin, sulfuric/sulphuric acid, chlor-alkali, industrial gases, air separation, glass furnace, glass melting, continuous process, steady-state. Word-boundary, case-insensitive, longest-first. Validate recall against the known 3B positives before the production census.

The bounds-on-claims discussion and the drop-in thesis-annex wording now live in `VALIDATION_PROTOCOL_C.md §9 and §11`.

### 12.6 Outputs from Stage 4

| File | Content |
|---|---|
| `output/merged.json` | Full record per paper, all stages combined with flags. |
| `output/merged.csv` | Flat table for Excel review (one row per paper). |
| `output/needs_review.md` | Flagged items ordered by §12.4 severity. |
| `output/cross_check_report.md` | Cross-check results. |
| `output/raw_model_outputs/{model}/{key}.json` | Archived raw extraction per model (reproducibility deposit). |
| `output/adjudication_log.jsonl` | Per Tier-1 divergence: both model values, blind-first decision, final value, evidence, rule, borderline tag, reveal-changed flag. |
| `output/fn_census/` | FN candidate-union census: candidate list (per detector), per-paper human verdicts with quotes, closure-pass log. |
| `output/audit_srs/sample.json` | SRS n=40 audit sample (seed 44; drawn over ALL eligible reconciled papers, census/divergence exclusions per cell — C-2 §4a) + census rosters (concordant-3B, borderline). |
| `output/audit_srs/manual/` | Reviewer's blind extractions for the audit (one JSON per paper). |
| `output/validation_report.md` | Per-field/per-instrument report (C-2 §5): divergence rates, reveal-change rates, per-field audited error counts + exact CIs, census enumerations, Corpus-B in/out count, grounding pass rate, test–retest + canary results, threshold-trigger outcomes. |

---

## 13. Pilot protocol

Two distinct exercises, run sequentially. Do not confuse them.

### 13.1 Form pilot (5 papers, per OSF protocol §6)

**Purpose:** verify charting form consistency and completeness. Outcome: schema refinements if any field reveals operational issues.

- 5 papers, random with `random.seed(42)` from the **Stage-0-eligible pool** (papers that passed all deterministic gates and the wrong-PDF/garbled checks — same population that would enter Stage 1), stratified 3 Included + 2 Maybe. Resolves an earlier ambiguity between this section and §18.7: §18.7 is authoritative.
- The reviewer extracts manually using the schema (§6.1, §6.2). **You do NOT run AI extraction on these 5 papers.**
- If schema changes result from this pilot, document the change and update §6 and the prompts.
- **Freeze schema** at end of this exercise.

Output: `output/pilot_form/{key}.json` populated by the reviewer.

### 13.2 AI validation — SUPERSEDED by Validation Protocol C

> **⚠️ SUPERSEDED (2026-06-25; C revised to C-2.0 on 2026-07-03).** The n=30 hybrid design (10 blind + 20 verification) described in the remainder of this section is **retained as historical record only**. Validation now follows **`VALIDATION_PROTOCOL_C.md` (C-2.3, authoritative; reviewer-approved and filed 2026-07-23)**: two-model extraction over the whole corpus → reconcile → blind-first adjudication of membership-critical Tier-1 divergences plus the FN candidate-union census → provisional Corpus-B roster lock → model-specific Stage-3 supplements where required → branch-prescribed Tier-2 treatment → remaining Tier-1/Tier-3 review → SRS n=40 audit with exact per-field CIs plus exhaustive censuses of rare consequential cells. Metrics per field/per instrument, never pooled (no κ, no AC1, no capture–recapture). The cross-model probe in `output/pilot_30/ai_blind_test/` is C's proof-of-concept; `run_metadata.json` amendments `validation-redesign-C` and `validation-protocol-C2` record the changes and rationale (power analysis killed small-n κ; `REDTEAM_ROUND1.md` Round 1 shaped C-1.0; `REVIEW_ROUND2_C2.md` Round 2 fixed C-1.0's six confirmed defects). **Everything below this box is the prior design, kept for provenance.**

**Purpose (prior design):** estimate AI vs. human agreement per variable — as **quality control / feasibility**, NOT certification. The Monte Carlo power analysis (`output/power_analysis/POWER_ANALYSIS.md`) establishes that n=10–30 cannot certify a per-variable kappa (at n=10 a true κ=0.6 yields a 95% interval of [0.00, 1.00]; precision to half-width 0.15 needs n≈150–500). The pilot's defensible job is to catch gross systematic failure modes (visible even at n=10) and confirm the charting form is operable. The quantitative Level A reliability claim is carried by the **20% audit sample** (§12.5); Level B reliability rests on **integral human review** in the full run. Pilot results are reported with bootstrap CIs and explicit "n-limited, directional" language.

- 30 papers, random with `random.seed(43)` from the **Stage-0-eligible pool**, **excluding the 7** papers used in prior pilots: the 5 form-pilot papers (§13.1) plus the 2 fresh papers (rayyan-472536623, rayyan-472535494) added for the v2.1/v2.2 re-pilots. Excluding all 7 (not only the 5) avoids two confounds: (a) **overfitting** — validating the schema on the same papers that shaped it inflates agreement; (b) **contamination** — those 2 were AI-extracted during schema iteration and the reviewer may have seen that output.
- Stratified: 15 Included + 15 Maybe. Pool after exclusion: 422 (279 Included + 143 Maybe).
- Expected Level 3B yield: ~8-12 papers across the 30.

#### 13.2.0 HYBRID DESIGN AMENDMENT (June 2026)

The original design required the reviewer to extract all 30 blind (~10-12 h). To reduce reviewer burden without forfeiting a defensible reliability estimate, the n=30 is split into two subsets (`make_validation_split.py`, second independent `seed=43` stratified shuffle):

- **10 BLIND** (5 Included + 5 Maybe, `manual/blind/`): reviewer extracts FIRST, no AI output visible. Yields the **clean** AI-vs-human Cohen's kappa / PABAK.
- **20 VERIFICATION** (10 Included + 10 Maybe, `manual/verification/`): AI extracts first; reviewer then reviews/corrects the AI output. Yields a **field-level correction rate**.

**Why not let agents do the blind extraction.** A reliability estimate requires an *external* reference. Substituting AI agents for the human reviewer (even a diverse multi-agent panel cross-checked against itself) measures AI-vs-AI consistency, which is high by construction (near-deterministic decoding regimes) and shares the model's systematic biases — it cannot detect them. This would violate the role declaration (§0.3, §2: *"no AI-vs-AI agreement check anywhere; reliability is established against blind human extraction"*) and would not survive examination. The human anchor is non-negotiable; the hybrid design *minimises* the human effort rather than eliminating it.

**Anchoring-bias estimate.** The verification subset is exposed to AI output, so its agreement is upward-biased (the reviewer tends to confirm plausible AI values without independent scrutiny). Because the blind and verification subsets are drawn from the same seed-43 stratified parent, they are **exchangeable in expectation**, so:

> `anchoring_bias ≈ agreement_20 − kappa_10`

is reported as a *measured quantity* in the thesis, converting the verification subset's weakness into a declared number rather than an unquantified caveat.

**Order of operations (HARD GATE, §18.10):**

1. **Reviewer blind first**: chart the 10 blind papers (`manual/blind/`) with the extraction tool (`extraction_tool/serve.py`) or by hand. No AI output exists yet.
2. **AI pass**: pipeline runs (Stages 0-4) on all 30 papers. Saves to `output/pilot_30/ai/`.
3. **Clean reliability**: Cohen's kappa / PABAK computed on the 10 blind (AI vs blind human).
4. **Verification**: AI output is prefilled into `manual/verification/`; reviewer reviews/corrects the 20.
5. **Comparison script** (you write it): per-variable agreement + correction rate + anchoring-bias estimate.
   - Categorical (single): Cohen's kappa with bootstrapped CIs.
   - Categorical (multi): per-value F1 (treating each value as binary).
   - Boolean: PABAK if prevalence < 20% or > 80%, else kappa.
   - Free text (B2, B13, B14): manual side-by-side review by reviewer; record qualitative agreement note.
   - Enum-value reconciliation (e.g. A11 "linear regression" vs the tool's "linear regression (1 IV)" label) is the comparison script's responsibility, not the reviewer's — both sides are normalised to a canonical vocabulary before scoring.

**Decisions per variable (not aggregated 85%):**

- kappa ≥ 0.6 (substantial) → pipeline OK for that variable.
- 0.4 ≤ kappa < 0.6 (moderate) → **investigate**: refine prompt, re-run on the same 30, re-validate.
- kappa < 0.4 (poor) → variable extracted **manually only** for full run.
- Variable constant in sample (no variance) → kappa undefined; report flagged for full-run monitoring instead.

**Sample size honesty:** the clean kappa rests on **n=10 blind**, giving wide CIs and unstable per-variable point estimates (kappa paradox on low-variance variables). PABAK is reported alongside. The conclusion rests on the **combination** — 10 blind (clean) + 20 verification (correction rate, anchoring-bias-adjusted) + the programmatic grounding check (§12.2) — not on any single metric. Treat per-variable kappa as directional, not a certification.

**Level B reliability caveat:** the blind subset (10 papers) yields only ~3-4 Level 3B papers, too few for a stable Level B kappa. Level B reliability therefore comes mainly from the combined blind + verification Level 3B papers (with the anchoring caveat) and is reinforced by the **integral human review of all Level 3B papers in the full run** (the real safety net for Level B — see §12.5) and the audit sample. Additionally, the n=30 is sampled from the **currently available** 440 PDFs (not the future 596); the unrecovered 153 are disproportionately Elsevier 2025 (refining/petrochemicals-heavy journals like *Applied Energy*, *Energy Conversion & Management*) — i.e. precisely the Level 3B segment. The pilot's Level 3B slice therefore over-represents open-access / MDPI papers and under-represents commercial Elsevier 2025. When the remaining 153 PDFs are added to `data/pdfs/`, the reviewer may request re-running the Level B kappa on the recovered Level 3B subset; document any updated values in the thesis methodological annex.

**Extraction template & tool:** the reviewer charts using the same JSON schema as the AI output (§6.3 envelope), but **omits** `evidence` and `confidence` fields — only `value` is populated (reduces typing, preserves comparable structure). `extraction_tool/` provides a local Flask form (PDF beside a schema-driven form with enum dropdowns) that writes schema-valid `value`-only JSON to `manual/{blind,verification}/{key}.json`. Blind templates are empty; verification templates are AI-prefilled after step 2.

### 13.3 Reporting

Validation results go to the thesis methodological annex per **`VALIDATION_PROTOCOL_C.md §11`** (drop-in text). Report per field/per instrument (never pooled): models (surface application versions + displayed model labels) + run dates; versioned prompt tags (v2.0→v2.3.1-operational) + commit hashes; divergence rates; reveal-change rates (Tier-1 adjudication and Tier-2 extraction); per-field audited error counts with **exact Clopper–Pearson CIs**; the **census enumerations** (FN candidates, confirmed reclassifications, closure passes) and the count of records entering/leaving Corpus B after validation; grounding-check pass rate; test–retest flip count; canary flip rate; and any pre-registered threshold triggers with the actions taken. Deposit raw model outputs + all census/adjudication logs on OSF as the reproducible record.

---

## 14. Reproducibility & versioning

Required to declare in the report / methodological annex:

- Execution-surface provenance, recorded at run time in `run_metadata.json`: application version, model label exactly as displayed by the surface, runtime configuration and run dates (subscription surfaces expose no guaranteed dated snapshot IDs).
- Date of each extraction batch run.
- Sampling: provider-managed (not configurable on subscription surfaces); configuration recorded per run.
- Git commit hash for prompts (`prompts/` is a git directory; tag commits per batch run).
- Schema version: v2.2.1 (FROZEN); validation methodology C-2.3.
- Random seeds: 42 (form pilot sampling), 43 (AI validation sampling), 44 (audit sample drawing).
- Determinism note: no sampling seed is exposed. No determinism control is exposed; run-to-run stability is measured by the determinism canary (n=30). Minor variance across runs may still occur due to backend non-determinism — declare this.

The reviewer is responsible for the methodological annex text; your job is to make the data available cleanly in `output/`.

---

## 15. Throughput, rate limits, batching (C-2, dual-model — updated 2026-07-10)

### Expected call volumes (per paper, PER MODEL FAMILY)

- Stage 1: 1 call (~30-50k input tokens, ~1k output).
- Stage 2: 1 call (~30-50k input, ~1-2k output). Only for eligible.
- Stage 3: 1 call (~30-50k input, ~3-5k output). Only for Level 3B. **Level-3B
  prevalence is unknown** (probe: 1–2/10; the "~25-30% of eligible" figure this
  section carried was an early estimate — see C-2 §3-Step-5 size branch); budget
  Stage-3 calls at 30–180 per model and re-plan at census closure.

### Total estimated calls for full run (~460 papers with PDF, of 596)

- Per model family: ~460 (S1) + ~390 (S2) + 30–180 (S3) ≈ **880–1,030 calls**
- **× 2 model families ≈ 1,800–2,100 extraction calls**, plus the determinism
  canary (2 × 30 papers × ~2-3 calls ≈ 150) and the counter-anchored recall
  pass (~1 call per concordant-excluded paper on the census work-list).

### Token estimates

- Per call: ~50k input + ~2k output average → per family ~45-52M input; **both
  families ~90-105M input, ~4-5M output.**

### Interactive batch strategy (per application)

- Each clean Claude or Codex/ChatGPT session acts only as a thin orchestrator;
  it delegates exactly one paper end-to-end to each article agent.
- The default and initial batch size is **5**. Any user-approved size from 1 to
  5 is ordinary. A batch of 10 may only be proposed after two consecutive green
  batches and still requires explicit approval.
- Every batch is authorized before agents start. When all agents terminate, the
  deterministic controller validates outputs, records state atomically, shows
  the batch report, and stops. It must not select or execute the next batch
  without a new approval.
- The two model workspaces run independently. Provider or session limits on one
  surface do not mutate or block the other workspace; reconciliation starts
  only when both validated inventories are available for the relevant wave.
- The displayed model label and application version are recorded; consumer
  surfaces do not justify claims that an exact snapshot was pinned.

*(The former "pilot is cheap: 30 papers × ~3 calls" line referred to the
superseded §13.2 n=30 pilot — historical.)*

---

## 16. Snowballing entry path

The OSF-registered protocol allows backward and forward snowballing on the final included corpus. Snowballed papers enter the pipeline as follows:

1. Each snowballed paper is added to `data/articles.csv` with:
   - Unique `key`: `rayyan-NNN` if also in Rayyan, otherwise `snowball-NNN`.
   - `via_snowballing = true` flag (carried in Stage 0 output).
   - `source_string = null` (A12 enum remains `{A, B, both}` for database-search papers; snowballed papers have null here — the `via_snowballing` flag is what carries their provenance).
   - Other metadata fields populated from the source.
2. Stage 0 re-runs on the appended rows.
3. Subsequent stages run only on new papers (resumable via state tracking — skip if `output/stage{N}/{key}.json` exists).
4. Stage 4 merges everything into the final dataset, with snowballed papers identifiable by the flag.

Pre-1996 snowballed papers are allowed (year-eligibility gate is bypassed if `via_snowballing == true`), but they are flagged for separate reporting in the PRISMA flow diagram.

**Search-strategy supplementation rule (decision 9, formalised C-2.3 — staged, cause-routed):**

Let **S** = number of records INCLUDED in the review via backward+forward snowballing of the included corpus, and **M ≤ S** = those not retrievable by the registered Scopus/WoS strategy, decomposed by cause: **M_string** (indexed in Scopus/WoS but missed by Strings A/B), **M_eng** (not indexed there; engineering venue), **M_thesis** (dissertations), **M_grey** (grey literature).

1. Snowballing (backward + forward, on the included corpus) is executed and reported per **PRISMA-S** — PRISMA-S is reproducible-reporting guidance, NOT evidence of search sufficiency.
2. **Closure rule:** records included via snowballing (or via any supplementary search below) receive their own backward+forward pass; iterate until a full pass adds zero new included records.
3. **Trigger evaluation:** if **S = 0**, no trigger can be evaluated — report the null snowball yield as UNINFORMATIVE about recall (not as validation) and declare the residual risk. If **S > 0** and (**M/S > 0.10 or M ≥ 5**), supplementation fires, **routed by cause**: M_string ≥ 2 → expand Strings A/B with the missed papers' vocabulary and RE-RUN Scopus/WoS (delta deduplicated and screened through the same three-level flow); M_eng ≥ 2 → run the (possibly expanded) strings on **Compendex** (delta screened likewise); M_thesis ≥ 2 → a dedicated dissertations source (e.g. ProQuest D&T) or an explicit, documented practical-exclusion declaration (reviewer decision at that point); M_grey → targeted source or declared limitation. Below-threshold M components are declared as residual risk.
4. **Never conclude 'adequate recall'.** Report only: 'the pre-specified trigger was / was not met'; a low M/S is evidence about citation-network coverage, not database recall in general — residual risk is declared in all cases.
5. Declared limitations regardless of outcome: doctoral theses (unreachable through the registered ar/cp/re doctype filters unless the M_thesis route fires); String-B calibration terms absent from the registered string (SEC, energy intensity indicator, energy KPI, M&V) unless the M_string route fires; grey literature reachable only through snowballing.
6. Text corrections for the thesis (no protocol effect): the ~6%/4.4% calibration figures are reported ONLY as exploratory calibration yield, never as structural-gap evidence; the 1996 lower bound corresponds to the NEMVP (1996) — the first international IPMVP edition is 1997.

Timing: snowballing operates on the *included* corpus, so it runs AFTER eligibility determination on the initial-retrieval corpus and does not block that run. **The final review corpus freeze is declared only after step 2's closure completes** (two-stage freeze: initial database-retrieval freeze 2026-07-10 → final review-corpus freeze after closure).

---

## 17. Output to the reviewer

When the reviewer asks "where is X", you should be able to point to a specific file. Output structure:

```
output/
├── run_metadata.json                # model, dates, seeds, prompts tag
├── stage0/
│   └── {key}.json                   # per-paper bundle
├── stage1/{model}/
│   └── {key}.json                   # eligibility + 3B decision (per model family)
├── stage2/{model}/
│   └── {key}.json                   # Level A fields (per model family)
├── stage3/{model}/
│   └── {key}.json                   # Level B fields (only Level 3B papers)
├── stage0_prepare.py                # built (88+ tests with the C-2 modules)
├── stage4_consolidate.py            # to build — C-2 runner (reconcile → census → audit → report)
├── merged.json                      # final per-paper consolidated record
├── merged.csv                       # flat table for Excel
├── needs_review.md                  # severity-ordered flags
├── cross_check_report.md            # §12.3 results
├── adjudication_log.jsonl           # Tier-1 blind-first decisions (C-2 §3-Step-3)
├── fn_census/                       # candidate union, verdicts, closure log (C-2 §3-Step-4/4b)
├── audit_srs/                       # SRS n=40 sample + census rosters + blind extractions (C-2 §4)
├── validation_report.md             # per-field/per-instrument report (C-2 §5)
├── pilot_form/                      # HISTORICAL — 5-paper schema pilot (§13.1, done)
└── pilot_30/                        # HISTORICAL — superseded n=30 design; ai_blind_test/ = C proof-of-concept
```

When you complete a stage, write a one-line summary to `output/progress.log` with timestamp and counts. The reviewer reads this to know where you are.

---

## 18. Hand-off summary — read this first (updated 2026-07-23 for the production state)

You are inheriting a scoping review extraction pipeline **mid-flight**. Read this document end to end, then `VALIDATION_PROTOCOL_C.md` (C-2.3, authoritative; reviewer-approved and filed 2026-07-23). The protocol is OSF-registered (DOI 10.17605/OSF.IO/TDW6C); deviations need documenting. The single-reviewer framing is non-negotiable — **you are a tool of the reviewer, not a co-reviewer.**

**Already DONE (do not redo):** prompts written + git-tagged `v2.3.1-operational` (schema FROZEN v2.2.1; broad registered eligibility inherited from `v2.3-eligibility-registered`); schema frozen after the §13.1 form pilot + 3 re-pilots; `stage0_prepare.py` built and run (599 bundles); the §13.2 n=30 pilot designed then SUPERSEDED (never executed — its cross-model probe in `pilot_30/ai_blind_test/` became C's proof-of-concept); the C-2 deterministic modules built TDD in `output/` (reconcile, fn_hunt, audit_sampler, residual_report, grounding, cross_checks — all tests green).

### Your first actions, in order (C-2.3)

1. Work only from `/Users/bernardoribeiro/LocalResearch/Screening/level3_extraction/`. Run the local-storage validator; refuse Desktop, Documents, Mobile Documents/iCloud, missing, unreadable or `dataless` production inputs.
2. Verify data state and hashes: 459 materialized PDFs, 459 preflight rows and 599 Stage-0 bundles; `data/articles.csv`, `excluded_duplicates.json`, `excluded_records.json`, `redownload_queue.json`, `non_retrieved_records.json` and `MISSINGNESS.md` exist. Rebuild Stage 0 only if this deterministic verification identifies a mismatch.
3. **Corpus freeze — two-stage.** The **initial database-retrieval freeze** is DONE (reviewer decision, 2026-07-10): the manual-download pass is stopped and the artefacts generated — `data/non_retrieved_records.json` + the missingness table (by Rayyan decision, DOI, year, doc type, sector signals). The **FINAL review-corpus freeze** waits for §16 snowballing/supplementation closure.
4. **DONE 2026-07-20:** deterministic implementation and operational re-pilot complete: equal-manifest ChatGPT/Claude packs, local-only input inventories, one-time run provenance, fail-closed production and re-pilot gates, default batch 5 with explicit approval, raw-output validation/one repair, reconciliation, separate Stage-3 supplements, reviewer workspace, blind withhold/commit/reveal/finalise, reviewer autosave + recovery, two-mode human evidence, structural Stage-4 eligibility handling, and final Stage-4 consolidation (7 records; pilot Corpus B = 2; 0 unresolved; 0 cross-check flags; 227 tests). The two lost Level-B blind forms are explicitly post-reveal/non-blind pilot deviations and do not contribute blind validation evidence.
5. **DONE 2026-07-23:** final C-2.3 reviewer sign-off and prospective OSF amendment filing (project `wh62r`, file `6a61e15518c36790cda322f4`; deposited PDF SHA-256 `15c140cdcc18f1f9d9c1dd7520d9ad96741cccafd654ad8b39fac64412ec2650`).
6. Verify that the current model packs are full-corpus production builds (`queue_scope=full`, 448 pending keys, no methodological gate blocker) with equal immutable manifests. Never rebuild or edit immutable pack content from inside a model workspace.
7. In each clean full-corpus application session, initialize `run_metadata.json` through the deterministic initializer with the displayed model label, application version, configuration and run dates. Verify equal immutable pack manifests; authorize every batch explicitly (default 5).
8. Execute B-first per C-2.3 §7: dual extraction → reconcile → **blind-first adjudication of the membership-critical Tier-1 divergences (`methodological_eligibility`, `level_3b`)**, with the FN candidate-union census (+§3-Step-4b upstream audit) on the concordant-excluded set → **initial-wave Corpus-B roster locked** (= membership divergences adjudicated + candidate union emptied; residual per C-2.3 §9; provisional until §16 closure) → Tier-2 branch selected by |B| (pause before Level-B work if |B| > 60) → model-specific Stage-3 supplements for roster papers lacking Stage 3 → branch-prescribed human Tier-2 treatment → remaining Tier-1 (`paper_type`, borderline) + Tier-3 cleanup → SRS audit → canary + test–retest → deposit.

### Discipline reminders

- **Never auto-exclude** a paper. Always route to `needs_review.md`.
- **Never use confidence as a gate.** It's a soft annotation.
- **Never run replicates at temperature > 0 as an agreement check.** That pattern is rejected by design (§0.3, §7).
- **Always quote literally with page number** in evidence. If you can't, value is null.
- **Always commit prompt changes** before re-running a stage. Tag the commit.
- **Always flag, never silently drop.** When in doubt, write to `needs_review.md`.

Good luck. Stay rigorous.
