# Supplementary Tables S1–S3

The supplementary tables of the article, as CSV files and as one workbook (`Supplementary_Tables_S1-S3.xlsx`, one sheet per table). They are generated from the records of this package by `code/supplementary/make_supplementary.py`, which first checks 27 counts reported in the article and stops if any differs.

| File | Table |
|---|---|
| `S1_search_strings.csv` | S1 — search strings and record counts by database |
| `S2a_reports.csv` | S2a — the 39 charted Corpus B reports: number of models, mechanism and adaptation occurrences, reproducibility fields, feed or product characteristics discussed but not used |
| `S2b_models.csv` | S2b — the 140 models: context, dependent quantity, model form, variables, data, boundary, re-estimation, validity domain, fit and out-of-sample result |
| `S2c_measurement.csv` | S2c — the 163 measurement entries (one per energy carrier and model) |
| `S2d_mechanisms.csv` | S2d — the 130 mechanism occurrences |
| `S2e_adaptations.csv` | S2e — the 88 adaptation occurrences |
| `S2f_corrections.csv` | S2f — every value changed by the later checks, before and after |
| `S3_corpus_a.csv` | S3 — the 331 Corpus A publications with the field values on which the two model extractions agreed, and the status of every field |

Corpus B tables are in the state analysed in the article: the extracted records (`data/05-extraction-corpus-b/records/`), with the decisions of the September 2026 model verification (`code/verification_v1/overlay.py`, `data/05-extraction-corpus-b/model-reread-2026-09/verifier/decisoes_2026-09-17.json`) and the corrections of the later checks (`data/06-late-verification/`) listed in S2f. The fouling and catalyst mechanisms found by the full-text search for omissions are reported in the article but not added to S2d, as in Figure 4. Verbatim quotations for every value are in the records.

In S3, a value is given only where the two model extractions agreed (status `model agreement; no full human validation`); single extractions, unresolved divergences and missing extractions are left empty, as in the article.

Vocabulary: `docs/data-dictionary.md`.
