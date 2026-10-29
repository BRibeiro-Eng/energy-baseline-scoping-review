# 05 — Corpus B extraction (Stage C)

- `records/`: the 39 charted Corpus B records, one model family (deviation D4), instrument frozen 13 September 2026 (`code/prompts/corpus-b/`). Every value has a verbatim quotation and a physical page, checked by `code/pipeline/stage_c_grounding.py`.
- `run-attempts/`: metadata of every extraction attempt (raw transcripts not released; `provenance/EXCLUDED.md`).
- `quarantine-log/`, `human-verdicts/`, `pilot/`, `triage_worklist.csv`: run control.
- `model-reread-2026-09/`: the September re-reading of 368 quoted cells by a second pass of the same model family and the reviewer's triage (deviation D7). Final states: 234 confirmed, 111 corrected, 18 removed, 5 retained. These describe the workflow, not extraction accuracy.

The human checks of Corpus B done in October 2026 are in `data/06-late-verification/` (modules d7a, d7b, d7c).
