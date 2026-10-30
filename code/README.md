# Code

The code is released as it was executed. Comments, docstrings and interface text are partly in Portuguese and were not translated, so that the files match the hashes recorded in the run metadata and task manifest (`provenance/source-map.tsv`). Paths inside the scripts refer to the working directory of the review (`level3_extraction/`); `provenance/source-map.tsv` maps every released file back to that layout.

| Folder | What it does |
|---|---|
| `pipeline/` | Corpus A pre-extraction control (batch controller, output validator, reconciliation, consolidation), the reviewer workspace for blind Tier-1 adjudication, the false-negative census and its triage, Corpus B Stage C (payloads, run, grounding, dossiers, compare) and their tests. Model calls went through subscription applications, not APIs; these scripts prepare inputs, check outputs and control the workflow. |
| `prompts/` | Frozen prompts, agent instructions and JSON schemas: `corpus-a/` (stages 1–3) and `corpus-b/` (Stage C, schema v2.3.0-C, SHA-256 in `SCHEMA_SHA256.txt`). |
| `bibliometrics/` | The Corpus A analysis package (`biblio/`), entry point `run_analysis.py`, tests, configuration. |
| `corpus-b-tables/` | Aggregation of the Corpus B records into the tables and the evidence map of the article. |
| `verification_v1/` | `overlay.py`: applies the decisions of the September 2026 model verification to the Corpus B records, in memory (used by `corpus-b-tables/` and `supplementary/`). |
| `supplementary/` | Builds the analysed state of the Corpus B records and Supplementary Tables S1–S3, after checking 29 counts of the article. |
| `late-verification/` | October 2026: task builder with the amendment interlock (`build_tasks.py`), local review bench (`bancada.py`), report (`relatorio.py`), escalation builder (`escalada_d11.py`), the D14 check (`d14_yield.py`) and `reproduce.sh`. |

Licence: MIT. See `REPRODUCE.md` for what can be rerun from the package.
