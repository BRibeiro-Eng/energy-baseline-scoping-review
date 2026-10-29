# Deviations from the registered protocol (D1–D16)

Same content as Table A2 of the article, with the files that document each deviation. "Planned" is what the registration or an amendment fixed; "Executed" is what was done.

| ID | Planned | Executed | Evidence in this package |
|---|---|---|---|
| D1 | Screening in three successive levels (title, abstract, full text) | Title and abstract assessed in one pass; no separate counts for the first two levels | `data/02-screening/records_screened.csv` |
| D2 | Grey literature from reference organisations searched on their websites | Not searched; grey literature limited to what the two databases index | — |
| D3 | Extraction by a single human reviewer | Model-assisted extraction; the reviewer adjudicates and is responsible for the records | `docs/amendments/OSF_Amendment_TDW6C_C-2.3_submission.pdf`, `docs/protocol/VALIDATION_PROTOCOL_C.md` |
| D4 | Corpus B extracted by two model families | One model surface | `docs/amendments/OSF_AMENDMENT_STAGE_C_DRAFT.md`; `data/05-extraction-corpus-b/records/` |
| D5 | Page locator fixed by the extraction surface | Correctable when the quotation exists verbatim on a single other page | `code/pipeline/stage_c_grounding.py`; run metadata in `data/05-extraction-corpus-b/run-attempts/` |
| D6 | False-negative control for Corpus B with a reasoned human decision per candidate | Partial: an exhaustive pass on a deterministically defined risk subset (5 publications) and seven verdicts adjudicated on excerpts; no false negatives confirmed | `data/03-eligibility/false-negative-census/`; `docs/corpus-decisions/CORPUS_CLOSURE_2026-09-12.md` §1 |
| D7 | Human coverage of Corpus B: 11 publications blind and 31 with verification of result-bearing fields | Replaced by a model re-reading of 368 quoted cells; later partly remedied by a human full-text census of absences (65 units), a random sample of 80 cells and a reading of the 13 refinery reports, after prior exposure and not blind | `data/05-extraction-corpus-b/model-reread-2026-09/`; `data/06-late-verification/` (modules d7a, d7b, d7c) |
| D8 | Sub-question SQ4 on applicability to refining | Withdrawn on 16 September 2026, because without blind reading of the core refining studies the review cannot support transferability claims | — |
| D9 | Backward and forward citation searching, with a rule to extend the search | Not performed | `docs/prisma/SNOWBALLING_NOT_PERFORMED_2026-09-16.md` |
| D10 | Random audit of agreed Corpus A values (40 publications), with a corpus-wide recheck of any field with three or more errors | Executed late, October 2026, on all 40; threshold reached in four fields, whose corpus-wide recheck was not executed | `data/06-late-verification/` (module d10) |
| D11 | Re-test of 30 reviewer decisions, with escalation to all decisions of a field with more than one flip | Executed late, October 2026; escalation executed for membership (17 decisions) and not for eligibility (43 decisions), for time | `data/06-late-verification/` (modules d11, d11x) |
| D12 | Instability canary on 30 publications across batches | Not performed; the application versions have changed since the production runs, so a fixed-configuration comparison is no longer possible | — |
| D13 | Terminology search in title/abstract exclusions (sample of 50) | Executed late, October 2026; 16 of the 50 sampled records judged without an abstract | `data/06-late-verification/` (module d13) |
| D14 | Yield analysis by search string | Not performed; the origin field was empty in the analytical file | `code/late-verification/d14_yield.py` (the check that found the field empty) |
| D15 | Rule for deciding that two extractions agree (not specified) | Comparison on the normalised form; rule revised on 21 September 2026, raising agreed sector values from 145 to 201 and country from 144 to 178 | `data/04-extraction-corpus-a/reconciliation/cell_provenance.csv`; `code/bibliometrics/` |
| D16 | Re-adjudicated membership changes applied to the corpora | One report removed from Corpus A (no agreed values); two reports that would enter Corpus B not charted, synthesis kept over the 39 charted | `data/03-eligibility/corpora.csv` (column `late_verification_change`) |

## Records decided by the assistant on the reviewer's instruction

Three final decisions in `data/06-late-verification/responses/d11x.jsonl` were written by the assistant (Claude) on the reviewer's explicit instruction, after the reviewer reviewed the escalated decisions and asked for re-adjudications that had widened the registered sector list to be reverted. Each of these events carries a `recorded_by` field saying so. The decision is the reviewer's; the record says who typed it.
