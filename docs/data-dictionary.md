# Data dictionary

Identifiers: every publication is identified by its Rayyan key, `rayyan-<9 digits>` (column `key` or `paper_id`, file names). The same key is used in every stage. `data/03-eligibility/corpora.csv` maps keys to titles and DOIs.

Booleans are written `true`/`false` (JSON) or `True`/`False` (CSV). `null` or an empty cell means the value was not recorded, which is not the same as "absent from the publication".

---

## 1. Screening — `data/02-screening/`

**`records_screened.csv`** — the 925 unique records screened on title and abstract.

| Column | Meaning |
|---|---|
| `key` | Rayyan key |
| `title`, `year`, `journal`, `issn`, `volume`, `issue`, `pages`, `authors`, `doi`, `language`, `keywords` | bibliographic fields as exported from Rayyan (Scopus/Web of Science records) |
| `screening_decision` | `Included` (355), `Excluded` (326) or `Maybe` (244), parsed from the Rayyan export tag `RAYYAN-INCLUSION`; `Maybe` records proceeded to full text |

Removed from the export: `abstract` (publisher text), `notes` (database export notes with author correspondence addresses), `publisher` (contains publisher e-mail addresses in Scopus exports), `url`, `location`, `pubmed_id`, `pmc_id`, export dates.

`excluded_duplicates.json`, `excluded_records.json`, `non_retrieved_records.json`: records removed as duplicates, excluded at title/abstract, and not retrieved at full text, with the reason recorded at the time.

## 2. Eligibility and corpus membership — `data/03-eligibility/`

**`corpora.csv`** — membership of every record that reached Corpus A, plus records touched by the late re-decisions.

| Column | Meaning |
|---|---|
| `paper_id` | Rayyan key |
| `in_corpus_a`, `in_corpus_b` | membership as locked on 12 September 2026 (Corpus A 331; Corpus B 40, of which 39 charted) |
| `group` | `A only` or `A and B` (original labels: `A sem B`, `B`) |
| `late_verification_change` | changes from the October 2026 re-decisions, `module:field:original->final` (e.g. `d11:methodological_eligibility:True->False`). Not applied to the counts of the article (deviation D16). |

**`tier1-adjudications/records/`** — the 82 publications whose eligibility or membership decisions diverged between the two model extractions, adjudicated blind by the reviewer. Four files per publication:

| File | Content |
|---|---|
| `<key>.blind.json` | the reviewer's blind decision, committed before anything was shown (`committed_at`) |
| `<key>.ai.json` | the two model proposals, shown only after a commit |
| `<key>.json` | the final decision, with the rule applied (`rule`) and the reviewer's justification; in all 82 it equals the blind decision |
| `<key>.state.json` | timestamps of creation, commit, reveal and finalisation; `blind_access_denials` lists attempts to open the model proposals before commit (empty in all 82) |

The reveal step was executed in full for 1 publication and partly for 3; for 5 the proposals were opened by an automated session, not by the reviewer; for the other 73 the blind decision was taken as final without a reveal. `docs/corpus-decisions/TIER1_CLOSURE_2026-09-09.md` records this and the one value an automated session changed, which was reverted.

Field groups: `eligibility` (`methodological_eligibility`, `ineligibility_reason`, `borderline_review_synthesis_eligibility`, `level_3b` = Corpus B membership, `paper_type`), `level_a` (Corpus A fields, see §3) and `level_b`.

**`false-negative-census/`** — the search for Corpus B false negatives among concordant decisions (deviation D6): candidates, the counter-anchored recall pass ("detector c") and its responses from both model surfaces, the roster lock of 12 September 2026, the triage queues, batches and the reviewer's verdicts. `detector-c/triage/verdicts/_exploratory_decision.json` records the dated decision not to expand the sector list (13 exploratory cases). The classifier's reasons (`triage/CLASSIFIER.json`, `triage/FILA_REVISAO.md`) were written by the model in Portuguese and are kept as produced; categories: `A_aplica` applies in a listed sector, `B_contexto` continuous context or unlisted sector, `C_mencao` mention only, `D_homonimo` homonym. Verdict values: `not_fn` (exclusion correct), `confirmed_fn` (false negative); sector `continuous-unlisted` marks an exploratory case.

## 3. Corpus A extraction — `data/04-extraction-corpus-a/`

`claude/` and `chatgpt/` hold the two independent pre-extractions, 448 records each:

- `raw/<key>.json`: the record as returned by the model;
- `validated/<key>.json`: the record after schema validation and normalisation; this is the input of the reconciliation;
- `validation_reports/<key>.json`: what the validator checked and changed;
- `agent_reports/` (Claude only): the agent's report for each extraction attempt (`<key>.attempt-<n>.md`);
- `run_metadata.json`, `PACK_LOCK.json`, `MANIFEST.sha256`: application, reported model, dates, and hashes of the input pack.

Record structure: `stage1` (eligibility), `stage2` (Corpus A fields), `stage3` (Corpus B supplement), plus `schema_version`, `prompt_tag`, `attempt`, `completed_at`. Fields and allowed values are defined in `code/prompts/corpus-a/schemas/article_output.schema.json`. Every coded value carries `evidence_quote` (verbatim, median 97 characters) and a page.

Corpus A fields: `paper_type`, `multi_site`, `country_region`, `sector_of_activity`, `type_of_organisation`, `ems_standard`, `mv_protocol`, `regulatory_driver`, `enpi_enb_model_types`, `complementary_methodologies`.

**`reconciliation/cell_provenance.csv`** — one row per publication × field (3310 cells): which value enters the analysis.

| Column | Meaning |
|---|---|
| `paper_id`, `field` | cell |
| `status` | `model agreement; no full human validation` (both extractions agree after normalisation; the value is used), `unresolved model divergence` (not used), `single model extraction` (not used), `no extraction` |
| `status_original` | the Portuguese label written by the analysis code |
| `claude`, `chatgpt` | the two normalised values |

## 4. Corpus B extraction — `data/05-extraction-corpus-b/`

**`records/<key>.json`** — the 39 Stage C records (schema v2.3.0-C, `code/prompts/corpus-b/schema.json`). Units: `applications` (a model applied to a context; 46) → `models` (140) with fields C1–C8 and C12; `mechanisms` (130 occurrences), `adaptations` (88), `study_limitations`, `implementation_barriers`, `C13_reproducibility`, `absence_declarations`, `reviewer_notes`. Each coded value has `quote` and a physical `page`; `page_as_recorded` keeps the extractor's locator when the grounding check corrected it (deviation D5).

**`run-attempts/<key>.attempt-<n>.metadata.json`** — one file per extraction attempt: application, reported model, timings, token counts, grounding errors that caused a retry.

**`quarantine-log/`** — records withdrawn from a run and why (`quarantine.jsonl`), and withdrawals later retracted (`*_retracted.jsonl`).

**`model-reread-2026-09/`** — the September re-reading of the 368 quoted cells (deviation D7):

- `v1_items_2026-09-17.json`: the 368 items (`id` such as `MEC-001`; `type` `MEC` mechanism (145), `MOD` model field (132), `ADP` adaptation (91); `path` in the record; `quote`; `page`; `support_class` `direct statement` or `requires inference`; `orig` = the extracted value);
- `verifier/resultados_verificador_2026-09-17.json`: the verifier's proposal per item;
- `verifier/decisoes_2026-09-17.json`: the reviewer's triage and the final state per item;
- `verifier/CODEBOOK_verificador.md` (+ English translation): instructions given to the verifier.

Portuguese keys in these files:

| Key | Meaning |
|---|---|
| `gerado` | generated (date) |
| `verificador` | verifier |
| `veredicto` | verdict: `confirma` confirms, `corrige` corrects, `retirar` remove, `nao_sustenta` quotation does not support the value |
| `confianca` | confidence: `alta` high, `media` medium, `baixa` low |
| `estado` | final state of the item after the reviewer's triage |
| `correcoes`, `retirar_motivo` | proposed corrections; reason for removal |
| `razao`, `evidencia` | reason; evidence (quoted) |
| `citacao_na_pagina` | quotation found on the page |
| `duvida`, `duvidas` | doubt(s) referred to the reviewer |
| `adjudicacao` | adjudication rule |
| `regras_pendentes` | pending rules |
| `controlo_seed44` | control sample drawn with seed 44 |
| `itens` | items |
| `decisao_autor` | the author's decision (`data` date, `quem` who, `regras` rules, `amostra_controlo` control sample) |
| final states | `confirmado` confirmed (234), `corrigido` corrected (111), `retirado` removed (18), `mantido` retained (5) |

## 5. Late verification — `data/06-late-verification/`

**`tasks/<module>.json`** — the tasks as generated on 16 October 2026 (seed 44): `module`, `kind`, `blind`, `registered` (the rule of the amendment), `frame` (size and definition of the sampling frame), `sample_order`, `tasks` (one entry per item). `tasks/MANIFEST.json` records the SHA-256 of each task file, the seed, the amendment hash and the git commit. `d13.redacted.json` replaces the publisher abstracts of `d13.json` by a placeholder; the original hash is in the manifest.

**`tasks/_ref/<module>.json`** — the values the reviewer was checking against, withheld from the interface until commit in blind modules (d10, d11, d11x, d7c).

**`responses/<module>.jsonl`** — append-only event log, one JSON object per line:

| Key | Meaning |
|---|---|
| `ts` | timestamp (local time, with offset) |
| `task_id` | the task (usually the Rayyan key; `key|field` for d11/d11x) |
| `phase` | `answer` (non-blind modules); `commit` → `reveal` → `final` (blind modules; a commit is write-once) |
| `answer` | the reviewer's input (see below) |
| `duration_s` | seconds the item was open in the interface (includes idle time) |
| `recorded_by` | present only where the assistant typed a decision on the reviewer's instruction (3 events in d11x) |

Answer vocabularies by module:

| Module | Check | Values |
|---|---|---|
| d13 | title/abstract exclusions | `decision`: `stands` (exclusion stands) or `should_have_proceeded` (should have gone to full text; not used); `reason` free text (Portuguese) |
| d11, d11x | test–retest of membership decisions | `value` true/false, `mode` (`quoted`, `not_reported_after_full_text_review`), `page`, `evidence`; at reveal: `flip` (blind value ≠ original), `final_value`, `why` |
| d7a | census of absences | `decision`: `a_none` (match irrelevant), `b_coded` (already coded), `c_missed` (omitted by the extraction; `field_affected`, `quote`, `page`, `corrected_value` recorded) |
| d7b | sample of 80 cells | `decision`: `correct`, `incorrect`, `undetermined`; `correct_value` |
| d10 | audit of agreed Corpus A values | per field: `v_<field>` re-extracted value, `p_<field>` page/evidence, `c_<field>` comparison at reveal: `same`, `extraction_error`, `reviewer_error`; `n_<field>` note |
| d7c | refinery and petrochemical reports | `c5` boundary correspondence (`exact`, `allocated (by rule or estimate)`, `mismatch acknowledged`, `not reported`), `c6` re-estimation regime (`declared and executed`, `declared, not executed`, `fixed or not stated`), `c7` validity domain (`numerical bounds`, `qualitative`, `not stated`), `oos` out-of-sample result (`reported`, `not reported`, `not applicable`), `tb` test on observations from a period after the fit (`yes`, `no`, `not applicable`); each with `_page` and `_ev` (evidence); at final `_final`, `_why` and `diffs` |

Free-text notes (`reason`, `note`, `why`, `_ev`) are in Portuguese or English as typed; they are not translated, because they are the record.

**`resultados.json`** — results computed from the logs by `code/late-verification/relatorio.py`: counts, Clopper–Pearson intervals, flips, `membership_changes`. **`RESULTS.md`** is the English rendering; `RESULTADOS.md` the Portuguese one written by the script.

## 6. Results

**`results/corpus-a/tables/*.csv`** — tables of the registered bibliometric run (Corpus A, 331 publications), written by `code/bibliometrics/run_analysis.py`. Labels were translated after the run by a fixed map; numbers are unchanged. Original labels:

| Portuguese (registered run) | English (this package) |
|---|---|
| A sem B | A only |
| Por resolver / sem extração | unresolved / not extracted |
| Por classificar / outro | unclassified / other |
| Outros | Other |
| Não aplicável | not applicable |
| Por normalizar: localização em texto | not normalised: location as free text |
| Indústria não especificada | Industry, unspecified |
| Água / resíduos; Metais / metalomecânica; Edifícios / serviços públicos; Automóvel / componentes; Petroquímica / polímeros; Alimentação / bebidas / agricultura; Transportes / logística; Vidro / cerâmica; Têxtil / couro; Química / farmacêutica; Refinação de petróleo | Water / waste; Metals / metalworking; Buildings / public services; Automotive / components; Petrochemicals / polymers; Food / beverages / agriculture; Transport / logistics; Glass / ceramics; Textiles / leather; Chemicals / pharmaceuticals; Petroleum refining |

The figure files keep the Portuguese labels; `catalog.en.json` gives the English title and caption of each figure (`title_pt`, `caption_pt` keep the originals). Values in `comparison_*.csv` are percentages of the publications of each group; a publication can carry several labels, so columns can sum to more than 100.

**`results/corpus-b/tabelas_cap3_2026-09-18.json`** — the Corpus B aggregates (Portuguese key names: `verificacao_estados` = states of the September re-reading; `close13` = the 13 refinery and petrochemical reports; `mech_papers`, `adp_papers` = publications with at least one mechanism/adaptation). Values are those before the October 2026 corrections.
