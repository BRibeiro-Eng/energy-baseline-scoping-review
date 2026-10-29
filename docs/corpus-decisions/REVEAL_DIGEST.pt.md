# Reveal digest — censo Tier-1, 2026-09-01

Os 82 estão commitados; os snapshots cegos estão congelados e nada aqui os altera.
Isto diz-te **onde olhar**, não substitui o reveal: abre o paper no formulário
(`http://127.0.0.1:5051`) e qualquer alteração fica registada em `{key}.reveal_changes.jsonl`.
Papers que não abras ficam em `committed`.

Nota estrutural: nas 90 células os dois twins discordam entre si por construção, portanto a
tua resposta bate sempre com um e falha sempre o outro. O reveal aqui não é «ambos discordam
de ti» — é **o que o twin discordante citou**, e se citou algo que não pesaste.

## Com quem ficaste

| campo | Claude | ChatGPT |
|---|--:|--:|
| `methodological_eligibility` | 18 | 49 |
| `level_3b` | 13 | 10 |
| **total** | **31** | **59** |

Na elegibilidade seguiste o leitor inclusivo em 73% dos casos. No `level_3b` ficaste
equilibrado, até ligeiramente do lado do Claude. Isso é informativo: se estivesses
simplesmente a seguir o ChatGPT, o `level_3b` teria o mesmo padrão. Não tem.

## Prioridade 1 — registaste ausência, o twin cita uma página (22)

Os mais afiados: escreveste `not_reported_after_full_text_review` e o twin aponta uma
citação verbatim com página. Ou o twin inventou a citação, ou passou-te algo. As citações
dos modelos passam o grounding check contra o texto do paper, portanto a primeira hipótese
é improvável. **Vale os ~30 min.**

| # | key | campo | tua | twin | p. | citação do twin |
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

## Prioridade 2 — twin discorda com confiança >= 0.9 (14)

Confiança declarada não é evidência, mas concentra a atenção.

| # | key | campo | tua | twin | p. | citação do twin |
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

## Os restantes

Discordância de baixa confiança ou sem citação forte. Passa-os no reveal, mas não é aí que
está o risco.

## Depois

```bash
python3 production/reviewer_workspace/progress.py
```

A taxa de reveal-change que sair daqui é a figura de anchoring-exposure do §3-Step-3.
Reporta-se em bruto — zero alterações é resultado válido, não é alvo a atingir.

