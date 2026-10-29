# Deviations from the registered protocol (D1–D17)

Same content as Table A2 of the article, with the files that document each deviation. "Planned" is what the registration or an amendment fixed; "Executed" is what was done.

| ID | Planned | Executed | Evidence in this package |
|---|---|---|---|
| D1 | Screening in three successive levels (title, abstract, full text) | Title and abstract assessed together in one step; no separate counts for the first two levels | `data/02-screening/records_screened.csv` |
| D2 | Grey literature from reference organisations searched on their websites | Not searched; grey literature limited to what the two databases index | — |
| D3 | Extraction by a single human reviewer | Model-assisted extraction; the reviewer adjudicates and is responsible for the records | `docs/amendments/OSF_Amendment_TDW6C_C-2.3_submission.pdf`, `docs/protocol/VALIDATION_PROTOCOL_C.md` |
| D4 | Corpus B extracted by two model families | One model family (Claude Code) | `docs/amendments/OSF_AMENDMENT_STAGE_C_DRAFT.md`; `data/05-extraction-corpus-b/records/` |
| D5 | Page reference as given by the extraction model | Correctable when the quotation exists verbatim on a single other page | `code/pipeline/stage_c_grounding.py`; run metadata in `data/05-extraction-corpus-b/run-attempts/` |
| D6 | False-negative control for Corpus B with a reasoned human decision per candidate | Partial: a complete check of a risk subset defined by fixed criteria (5 publications) and seven decisions adjudicated on excerpts; no false negatives confirmed | `data/03-eligibility/false-negative-census/`; `docs/corpus-decisions/CORPUS_CLOSURE_2026-09-12.md` §1 |
| D7 | Human coverage of Corpus B: 11 publications blind and 31 with verification of the fields used in the results | Replaced by a model re-reading of 368 quoted values; later partly remedied by a human full-text search for omissions (65 report–term-family pairs), a random sample of 80 values and a reading of the 13 refinery reports, after prior exposure and not blind | `data/05-extraction-corpus-b/model-reread-2026-09/`; `data/06-late-verification/` (modules d7a, d7b, d7c) |
| D8 | Sub-question SQ4 on applicability to refining | Withdrawn on 16 September 2026, because without blind reading of the core refining studies the review cannot support transferability claims | — |
| D9 | Backward and forward citation searching, with a rule to extend the search | Not performed | `docs/prisma/SNOWBALLING_NOT_PERFORMED_2026-09-16.md` |
| D10 | Random audit of agreed Corpus A values (40 publications), with a corpus-wide recheck of any field with three or more errors | Executed late, under Amendment 3, on all 40; threshold reached in four fields, whose corpus-wide recheck was not executed | `data/06-late-verification/` (module d10) |
| D11 | Re-test of 30 reviewer decisions, with escalation to all decisions of a field with more than one changed decision | Executed late, under Amendment 3; escalation executed for membership (17 decisions) and not for eligibility (43 decisions), for time | `data/06-late-verification/` (modules d11, d11x) |
| D12 | Repeat extraction of 30 publications to test model stability | Not performed; the application versions have changed since the extraction, so a fixed-configuration comparison is no longer possible | — |
| D13 | Terminology search in title/abstract exclusions (sample of 50) | Executed late, under Amendment 3; 16 of the 50 sampled records judged without an abstract | `data/06-late-verification/` (module d13) |
| D14 | Yield analysis by search string | Not performed; the origin field was empty in the analysis data set | `code/late-verification/d14_yield.py` (the check that found the field empty) |
| D15 | Rule for deciding that two extractions agree (not specified) | Comparison on the normalised form; rule revised on 21 September 2026, raising agreed sector values from 145 to 201 and country from 144 to 178 | `data/04-extraction-corpus-a/reconciliation/cell_provenance.csv`; `code/bibliometrics/` |
| D16 | Re-adjudicated membership changes applied to the corpora | Not applied: one report would leave Corpus A (330; no agreed values) and two would enter Corpus B (42; not charted); the analysis keeps Corpus A at 331 and Corpus B at 40, 39 charted | `data/03-eligibility/corpora.csv` (column `late_verification_change`) |
| D17 | No language model to make or pre-fill a decision in the checks of Amendment 3 | In the Corpus A audit (d10) and the reading of the refinery reports (d7c), ChatGPT (gpt-6.1-sol, high reasoning) summarised the reports, located passages and drafted the recorded evidence and justifications, also after the reference values were revealed; decisions taken and recorded by the reviewer | `data/06-late-verification/responses/d10.jsonl`, `d7c.jsonl`; `data/06-late-verification/d7c_adoption.json` |

## Records decided by the assistant on the reviewer's instruction

Three final decisions in `data/06-late-verification/responses/d11x.jsonl` were written by the assistant (Claude) on the reviewer's explicit instruction, after the reviewer reviewed the escalated decisions and asked for re-adjudications that had widened the registered sector list to be reverted. Each of these events carries a `recorded_by` field saying so. The decision is the reviewer's; the record says who typed it.
