> Translated from Portuguese for this release. Original: `REVEAL_DIGEST.pt.md` (same folder), SHA-256 `989edc67794a3d965fca5664301c8559aa65478a71303252cbd0e984fb8360b3`. The original is the record; this translation is for reading.

# Reveal digest — Tier-1 census, 2026-09-01

All 82 are committed; the blind snapshots are frozen and nothing here changes them.
This tells you **where to look**; it does not replace the reveal: open the paper in the form
(`http://127.0.0.1:5051`) and any change is logged in `{key}.reveal_changes.jsonl`.
Papers you do not open stay `committed`.

Structural note: in the 90 cells the two twins disagree with each other by construction, so
your answer always matches one and always misses the other. The reveal here is not "both disagree
with you" — it is **what the disagreeing twin quoted**, and whether it quoted something you did not weigh.

## Whom you sided with

| field | Claude | ChatGPT |
|---|--:|--:|
| `methodological_eligibility` | 18 | 49 |
| `level_3b` | 13 | 10 |
| **total** | **31** | **59** |

On eligibility you sided with the inclusive reader in 73% of cases. On `level_3b` you were
balanced, even slightly on Claude's side. That is informative: if you were
simply following ChatGPT, `level_3b` would show the same pattern. It does not.

## Priority 1 — you recorded absence, the twin quotes a page (22)

The sharpest: you wrote `not_reported_after_full_text_review` and the twin points to a
verbatim quotation with a page. Either the twin invented the quotation, or something escaped you. The models'
quotations pass the grounding check against the paper's text, so the first hypothesis
is unlikely. **Worth the ~30 min.**

| # | key | field | yours | twin | p. | twin's quotation |
|--:|---|---|---|---|--:|---|
| 1 | `rayyan-472535700` | eligibility | False | chatgpt=True (c=0.99) | 3 | This implementation requires the estimation of a mathematical model that expresses the flow rate |
| 2 | `rayyan-472535511` | level_3b | False | chatgpt=True (c=0.98) | [22, 22] | Figure 11 presents the characteristics and proﬁles of six companies located in Colombia, in the  |
| 3 | `rayyan-472535541` | level_3b | False | chatgpt=True (c=0.98) | 28 | glass container production plant |
| 4 | `rayyan-472535648` | eligibility | False | chatgpt=True (c=0.97) | 5 | By developing the SEAPs for each of these cities historical energy consumption data were obtaine |
| 5 | `rayyan-472535653` | eligibility | False | chatgpt=True (c=0.96) | 11 | Methodology users must identify a region of interest, gather relevant input data including proje |
| 6 | `rayyan-472536054` | level_3b | False | chatgpt=True (c=0.95) | 2 | The majority of contributions address challenges in petrochemical industries, and namely in ethy |
| 7 | `rayyan-472536742` | level_3b | False | chatgpt=True (c=0.95) | 7 | At that time, seven companies from three industries, automobile assembly, wet corn refining, and |
| 8 | `rayyan-472535622` | eligibility | False | chatgpt=True (c=0.94) | 1 | the glass- tempering energy consumption per / m2 of glass will diminish two times. |
| 9 | `rayyan-472535739` | level_3b | False | chatgpt=True (c=0.93) | 7 | The target to improve energy intensity by 1 % annually has a positive impact because it helps us |
| 10 | `rayyan-472535519` | eligibility | False | claude=True (c=0.9) | 5 | The monitoring activities relates to the annual energy consumption of each heating system throug |
| 11 | `rayyan-472535636` | eligibility | False | chatgpt=True (c=0.9) | 2 | In addition the “relevant variables related to significant energy uses” (commonly called Drivers |
| 12 | `rayyan-472535719` | eligibility | False | chatgpt=True (c=0.9) | 5 | To have accurate building simulation results a  Calibrated Model is required, specifically confi |
| 13 | `rayyan-472535779` | eligibility | False | chatgpt=True (c=0.9) | 6 | The activation and deactivation of A/C units is based on the total building load’s control and e |
| 14 | `rayyan-472535628` | eligibility | False | chatgpt=True (c=0.88) | 2 | To determine the energy consumption from coal the quantitate consumption at the plant was measur |
| 15 | `rayyan-472535360` | eligibility | False | chatgpt=True (c=0.83) | 6 | Furthermore, a qualitative hypothesis test is carried out on the individual technologies. The EE |
| 16 | `rayyan-472535657` | level_3b | False | chatgpt=True (c=0.82) | [4, 3] | 4 Paper 21 -38.9 -45.69 -55.31 / We estimated the energy conservation from only the designated f |
| 17 | `rayyan-472535687` | eligibility | False | chatgpt=True (c=0.82) | 1 | The project target was an average hourly evening peak load shift of 2.50 MW. In the performance  |
| 18 | `rayyan-472536339` | eligibility | False | chatgpt=True (c=0.82) | 17 | In the case of hotels, it has obtained energy indicators, which are difficult to achieve for all |
| 19 | `rayyan-472536479` | eligibility | False | chatgpt=True (c=0.82) | 7 | To estimate the main benefits of using CWS and CWSP, a method of calculating the relative enviro |
| 20 | `rayyan-472535750` | eligibility | False | chatgpt=True (c=0.78) | [2, 2] | Modeled the current heating processes of the furnaces, and developed an in-depth understanding o |
| 21 | `rayyan-472536732` | eligibility | False | claude=True (c=0.6) | 1 | The article establish accounting frameworks of energy performance index(EPI) based on Logarithmi |
| 22 | `rayyan-472536603` | eligibility | False | claude=True (c=0.58) | [6, 4] | We used the energy baseline models developed in section 4.2 / The evaporator was modeled using a |

## Priority 2 — twin disagrees with confidence >= 0.9 (14)

Declared confidence is not evidence, but it focuses attention.

| # | key | field | yours | twin | p. | twin's quotation |
|--:|---|---|---|---|--:|---|
| 1 | `rayyan-472535489` | level_3b | False | chatgpt=True (c=0.99) | 3 | The company under study belongs to the steel industry and is in Colombia. |
| 2 | `rayyan-472535556` | eligibility | True | chatgpt=False (c=0.99) | 1 | In this study, performance assessment of two buildings in the Campus of Yasar University has bee |
| 3 | `rayyan-472536537` | eligibility | True | chatgpt=False (c=0.99) | 12 | a public residential care home in The Netherlands |
| 4 | `rayyan-472536674` | eligibility | True | chatgpt=False (c=0.99) | 4 | The instrumentation was implemented and tested on two pilot experimental office buildings in Nan |
| 5 | `rayyan-472536752` | eligibility | True | chatgpt=False (c=0.99) | 1 | The case study chosen is an institution within the education sub-sector, University College Cork |
| 6 | `rayyan-472535386` | level_3b | False | chatgpt=True (c=0.98) | 2 | since the incinerator is one of the refinery’s most hazardous units |
| 7 | `rayyan-472536569` | eligibility | True | chatgpt=False (c=0.97) | 1 | Using this cloud platform for home appliances could help the manufacturers to promote energy eff |
| 8 | `rayyan-472536356` | level_3b | False | chatgpt=True (c=0.96) | 3 | Continuous pharmaceutical manufacturing utilises twin-screw granulators to produce granulated so |
| 9 | `rayyan-472536518` | level_3b | True | claude=False (c=0.95) | None | not applicable |
| 10 | `rayyan-472536587` | level_3b | False | chatgpt=True (c=0.95) | 1 | Aluminum Smelter |
| 11 | `rayyan-472536661` | level_3b | False | chatgpt=True (c=0.95) | 2 | ADGAS owns and operates three LNG trains; LNG trains 1 & 2 are commissioned in 1977 while the hi |
| 12 | `rayyan-472535650` | level_3b | False | chatgpt=True (c=0.94) | 3 | The plant has more than 30 years with a hot dip galvanizing line with a capacity of 70,000 tons/ |
| 13 | `rayyan-472536379` | level_3b | True | chatgpt=False (c=0.9) | [1, 6] | case studies (3 steel mills) / every change in the batch process |
| 14 | `rayyan-472536714` | level_3b | True | claude=False (c=0.9) | 1 | This paper presents an approach used by Energy Star to implement manufacturing plant energy benc |

## The rest

Low-confidence disagreement or no strong quotation. Go through them in the reveal, but that is not where
the risk is.

## Afterwards

```bash
python3 production/reviewer_workspace/progress.py
```

The reveal-change rate that comes out of this is the anchoring-exposure figure of §3-Step-3.
It is reported raw — zero changes is a valid result, not a target.


*Note added for the release: the reveal was later executed only in part; see `TIER1_CLOSURE_2026-09-09.md`.*
