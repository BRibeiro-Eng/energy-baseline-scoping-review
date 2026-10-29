# Results — checks of the amendment of 16 October 2026 (late verification)

English rendering of `RESULTADOS.md`, which `code/late-verification/relatorio.py` generated on 2026-10-29 at 19:07 from `tasks/` and `responses/`. The numbers are in `resultados.json`; `code/late-verification/reproduce.sh` recomputes them. Each instrument is reported separately. Intervals are exact Clopper–Pearson 95 % intervals; "upper" is the one-sided 95 % upper bound. Times are the time items were open in the bench, idle time included.

**Model assistance (deviation D17).** d13, d11, d11x, d7a and d7b were carried out by the reviewer without a language model. In d10 and d7c the reviewer used ChatGPT (model reported as gpt-6.1-sol, high reasoning) to summarise the reports, locate passages and draft the recorded evidence and justifications, also after the reference values were revealed. The decisions were the reviewer's. d10 and d7c are therefore model-assisted checks.

## D13 · Exclusions at title/abstract screening

- Frame: 326 excluded records; abstract available for 200.
- Lexicon census: 13/13 reviewed; should have proceeded: 0.
- Random sample: 50/50 reviewed; should have proceeded: **0/50 (0.0 %–7.1 %; upper 5.8 %)**.
- Binding escalation (full re-screen): **not triggered**.
- Time: 0.61 h.

## D11 · Test–retest

- Completed: 30/30; flips: **4** (methodological eligibility 2, Corpus B membership `level_3b` 2).
- Fields with escalation (> 1 flip): methodological eligibility, `level_3b`.
- Membership changes (final ≠ original): 1 — `rayyan-472536674`, methodological eligibility, true → false (leaves Corpus A).
- Time: 7.01 h.

| Decision | Final | Commit |
|---|---|---|
| `rayyan-472535700` · eligibility | false | 2026-10-22 17:32 |
| `rayyan-472536054` · level_3b | false | 2026-10-22 18:07 |
| `rayyan-472535739` · level_3b | false | 2026-10-22 18:35 |
| `rayyan-472536674` · eligibility | false | 2026-10-22 19:12 |

## D11·E · Escalation of the retest

- Executed for `level_3b` (all 17 remaining decisions). Of the 43 eligibility decisions, 1 was completed and 42 were not, for lack of time; the eligibility escalation is reported as not executed. 18 of the 60 generated items were completed.
- Flips: **7** (all `level_3b`).
- Membership changes (final ≠ original): 3 — `rayyan-472535657` (false → true), `rayyan-472535750` (true → false; the report is not in Corpus A), `rayyan-472536587` (false → true). Not applied to the corpora (deviation D16).
- Three decisions have a second `final` event (`rayyan-472536379`, `-472536661`, `-472536742`): the assistant typed them on the reviewer's explicit instruction, to revert re-adjudications that had widened the registered sector list (two) and to record the reviewer's decision on one more; each carries `recorded_by`. The last event counts.
- Time: 15.4 h (includes long idle intervals).

| Decision | Final | Commit |
|---|---|---|
| `rayyan-472535657` | true | 2026-10-23 10:24 |
| `rayyan-472535750` | false | 2026-10-23 10:33 |
| `rayyan-472536379` | true | 2026-10-23 10:46 |
| `rayyan-472536587` | true | 2026-10-23 11:21 |
| `rayyan-472536588` | true | 2026-10-23 11:30 |
| `rayyan-472536661` | false | 2026-10-23 11:45 |
| `rayyan-472536742` | false | 2026-10-23 11:52 |

## D7·A · Census of absences by lexicon

39 Corpus B reports × 7 term families = 273 units; 65 with a match, all reviewed.

| Family | Units with a match | No match | Reviewed | (a) irrelevant | (b) already coded | (c) omissions | Complete |
|---|---|---|---|---|---|---|---|
| C code/data availability | 8 | 31 | 8 | 5 | 1 | **2** | yes |
| F fouling/degradation | 12 | 27 | 12 | 7 | 1 | **4** | yes |
| K catalyst | 6 | 33 | 6 | 4 | 0 | **2** | yes |
| Q feed/product quality | 11 | 28 | 11 | 1 | 5 | **5** | yes |
| R re-estimation | 2 | 37 | 2 | 0 | 2 | **0** | yes |
| T temporal / out-of-sample validation | 17 | 22 | 17 | 11 | 4 | **2** | yes |
| V validity domain | 9 | 30 | 9 | 6 | 3 | **0** | yes |

Omissions (15), with the corrected value as recorded (Portuguese notes in `responses/d7a.jsonl`):

- (C) `rayyan-472536588` p. 8 · C13 data availability → partial.
- (C) `rayyan-472536606` p. 10 · C13 data availability → partial.
- (F) `rayyan-472535550` p. 12 · mechanism: fouling of heat exchangers; effect: observability gap; applied to the case.
- (F) `rayyan-472535582` p. 1 · mechanism: fouling; effect: non-stationarity of the relationship; general.
- (F) `rayyan-472536455` p. 6 · mechanism: equipment degradation or ageing; effect: cross-site comparability; general.
- (F) `rayyan-472536695` p. 3 · mechanism: catalyst degradation; effect: other (potential influence on energy performance); applied to the case.
- (K) `rayyan-472536226` p. 6 · mechanism: catalyst activity; effect: other (constrains the energy optimum of the steam/carbon ratio); applied to the case.
- (K) `rayyan-472536695` p. 3 · the same mechanism as the F entry; recorded once.
- (Q) `rayyan-472535480` p. 7 · pulp quality/grade and raw material as product/feed characteristics discussed for separate baselines.
- (Q) `rayyan-472535585` p. 27 · coal moisture and energy content proposed for monitoring.
- (Q) `rayyan-472535794` p. 5 · feed moisture discussed as an explanatory factor of specific energy consumption.
- (Q) `rayyan-472536532` p. 11 · feed quality discussed as a potential explanatory variable.
- (Q) `rayyan-472536606` p. 7 · raw-material quality/mix and by-product moisture as explanatory factors; limestone hardness and moisture discussed but not included for lack of consistent data.
- (T) `rayyan-472536379` p. 4 · models A1/M1 and A1/M2: out-of-sample result reported; held-out split.
- (T) `rayyan-472536695` p. 7 · A1/M1: out-of-sample result reported; held-out split.

Time: 19.43 h.

## D7·B · Sample of extracted cells

- Frame: 350 result-bearing cells (of 368); sample 80; reviewed 80.
- Incorrect: **12/79 (8.1 %–25.0 %; upper 23.4 %)**; undetermined: 1.
- By type: mechanisms 8/30 incorrect; model fields 2/30 (+1 undetermined); adaptations 2/19.
- All 12 errors are in cells the September model re-reading had confirmed.
- Time: 3.51 h.

| Item | Report | Path | Corrected to |
|---|---|---|---|
| MEC-135 | `rayyan-472536693` | `mechanisms[3]` | effect_other_verbatim |
| MEC-067 | `rayyan-472535794` | `mechanisms[7]` | effect: statistical misspecification |
| MEC-133 | `rayyan-472536693` | `mechanisms[1]` | refers_to: paper-level argument |
| MEC-097 | `rayyan-472536487` | `mechanisms[1]` | claim_status: applied to the case |
| ADP-085 | `rayyan-472536693` | `adaptations[1]` | refers_to: paper-level argument |
| ADP-020 | `rayyan-472535582` | `adaptations[0]` | normative_framing: absent |
| MEC-123 | `rayyan-472536612` | `mechanisms[4]` | effect: other |
| MEC-014 | `rayyan-472535480` | `mechanisms[4]` | effect: other |
| MEC-012 | `rayyan-472535480` | `mechanisms[2]` | claim_status: general; effect: other |
| MOD-131 | `rayyan-472536695` | `…C5_measurement[1].data_origin` | data_origin: not reported |
| MOD-079 | `rayyan-472536226` | `C13_reproducibility.data_available` | data_available: yes |
| MEC-098 | `rayyan-472536501` | `mechanisms[0]` | effect: other |

## D10 · Audit of agreed Corpus A values (model-assisted, D17)

- Reports completed: 40/40 (contiguous prefix of the draw: 40).
- e_v raw = blind value differs from the agreed value (registered metric); e_v adjudicated = differences the reviewer attributed to the extraction after re-checking.

| Field | n_v | e_v raw | e_v adjudicated | ≥ 3? |
|---|---|---|---|---|
| complementary_methodologies | 28 | 0/28 (0.0–12.3 %; upper 10.1 %) | 0/28 | no |
| country_region | 18 | 0/18 (0.0–18.5 %; upper 15.3 %) | 0/18 | no |
| ems_standard | 30 | 2/30 (0.8–22.1 %; upper 19.5 %) | 1/30 | no |
| enpi_enb_model_types | 23 | 12/23 (30.6–73.2 %; upper 70.4 %) | 11/23 | **yes** |
| multi_site | 32 | 13/32 (23.7–59.4 %; upper 56.7 %) | 13/32 | **yes** |
| mv_protocol | 32 | 2/32 (0.8–20.8 %; upper 18.4 %) | 2/32 | no |
| paper_type | 32 | 5/32 (5.3–32.8 %; upper 30.1 %) | 5/32 | **yes** |
| regulatory_driver | 32 | 1/32 (0.1–16.2 %; upper 14.0 %) | 1/32 | no |
| sector_of_activity | 23 | 0/23 (0.0–14.8 %; upper 12.2 %) | 0/23 | no |
| type_of_organisation | 24 | 4/24 (4.7–37.4 %; upper 34.2 %) | 4/24 | **yes** |

The registered corpus-wide recheck of the four fields with e_v ≥ 3 was not executed. Time: 2.44 h.

## D7·C · Refinery and petrochemical reports (model-assisted, D17)

- Completed: 13/13; five fields per report (65 values).
- Blind reading vs value coded before the census, differences by field: boundary (c5) 5, re-estimation (c6) 2, validity domain (c7) 1, out-of-sample (oos) 1. Changes after the reveal: c6 1 (`rayyan-472535550`, back to the coded value). Final values differing from the coded: 8.
- Test on observations from a period after the fit: **no test in any report** (`no` 10, `not applicable` 3).
- Adopted in the article: 3 of the 8 (re-estimation of Hashim et al. 2019, numerical validity bounds of Beisheim et al. 2019, out-of-sample of Almanza and Leon-De-Los-Santos 2025). Not adopted: the 5 boundary changes, because the correspondence was inferred, not stated. Details in `d7c_adoption.json`.
- Time: 1.29 h.
