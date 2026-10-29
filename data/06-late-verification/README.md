# 06 — Human checks added after the first analysis (October 2026)

Executed under the amendment of 16 October 2026 (OSF `2zgx8`), after the results had first been reported in the dissertation. Not prospective with respect to the results; the checks on Corpus B are not blind (the reviewer had read the extraction forms). In d13, d11, d11x, d7a and d7b no language model made or pre-filled a decision. In d10 and d7c the reviewer used ChatGPT (gpt-6.1-sol) to summarise the reports, locate passages and draft the evidence and justifications recorded in `responses/`, including after the reveal; the decisions were his (deviation D17). Treat d10 and d7c as model-assisted checks.

| Module | Check | Deviation |
|---|---|---|
| d13 | Title/abstract exclusions: census of 13 lexicon matches + random 50 of 313 | D13 |
| d11 | Test–retest: 30 of 90 consequential membership decisions, re-decided blind | D11 |
| d11x | Escalation of d11 for the field with more than one flip (membership, 17 decisions); eligibility escalation (43) not executed | D11 |
| d7a | Census of absences: term list (`docs/amendments/lexico_camada_A.json`) over the 39 Corpus B full texts; 65 report–family units with a match read | D7 |
| d7b | Random 80 of the 350 result-bearing cells, each checked against the cited page | D7 |
| d10 | Audit of agreed Corpus A values: 40 random publications re-extracted blind (model-assisted, D17) | D10 |
| d7c | The 13 refinery and petrochemical reports, five fields, coded values withheld until commit (model-assisted, D17) | D7 |

- `tasks/`: what the reviewer was shown (seed 44; `MANIFEST.json` has every hash); `tasks/_ref/`: values withheld until commit.
- `responses/`: append-only decision logs (format in `docs/data-dictionary.md` §5).
- `resultados.json`: results; `RESULTS.md`: English report; `d7c_adoption.json`: which d7c values the article adopted and why. Recompute with `code/late-verification/reproduce.sh`.

`duration_s` includes idle time while an item was open; long idle intervals are visible in the logs and were not removed.
