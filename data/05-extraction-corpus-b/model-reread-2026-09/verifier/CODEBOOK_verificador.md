> Translated from Portuguese for this release. Original: `CODEBOOK_verificador.pt.md` (same folder), SHA-256 `e0c32c34f5efd27f288a3c476b3df5fd4971284e76df2cbd0bfbd131395a0b0d`. The original is the record; this translation is for reading.

# Verification of Stage C quotations — instructions and codebook

*These are the instructions given to the verifying model in September 2026. The model was asked to write its reasons in European Portuguese, which is why the verifier's output (`resultados_verificador_2026-09-17.json`) is in Portuguese.*

You are verifying values coded by another model from scientific articles (a scoping review on energy performance models, EnPI/EnB, in continuous process industries). For each item you have: the recorded value (`orig`), the quotation (`quote`) and the physical page (`page`). In `pages[key]` you have the extracted text of that page and of the adjacent ones.

For each item decide, reading the quotation within its paragraph:
1. Is the quotation on the stated page (or an adjacent one)? The extracted text may have hyphenation, interleaved columns and ligatures (ﬁ, ﬂ); that is not a failure.
2. Does the quotation, read in the context of the paragraph, support the recorded value?
3. If it does not, what would the right value be, chosen ONLY from the allowed values below?

Be rigorous and conservative. Do not invent. Do not infer causes the article does not name. When in doubt, mark doubt — that is what it is for: the human reviewer will read only the items where you mark doubt, so a wrong confirmation of yours passes without review. Confirm with high confidence only when the sentence, read in its paragraph, clearly justifies the value.

## Definitions (from the extraction protocol)

**Mechanism vs. study limitation vs. barrier.** Mechanism = a limitation OF THE energy performance MODEL: it conditions whether the model can be built or trusted. Study limitation = a larger/different study would solve it without changing the model (sample, data access, scope). Barrier = people, money, organisation, maintenance. Proposing future work is not a limitation. Data quality and data length are a mechanism only if the article states the consequence for building/using the model.

**claim_status** (mechanisms):
- `general` — a property of methods in principle: a definition, a statement about regression in general, a caution taken from the literature. A definition of heteroscedasticity is general even in a case article.
- `applied to the case` — stated about the model OF THIS study (without being shown with the data).
- `empirically demonstrated` — shown with the data OF THIS study (result, figure, test, value).

**mechanism_cause** — only the physical/operational cause the article NAMES; `not stated` is the normal answer. Values: fouling; catalyst deactivation; feedstock quality or composition change; product mix or grade change; equipment degradation or ageing; operating mode or campaign change; ambient conditions; plant or process modification; concurrent improvement programme; other; not stated.

**mechanism_effect_on_model** — what it does to the model. Values: non-stationarity of the relationship (the PROCESS relationship changes); baseline drift or expiry (the MODEL/baseline expires and has to be redone); validity envelope exceeded; statistical misspecification; observability gap — quantity not measured; data quality — missing, erroneous or discontinuous data; insufficient data length for the model; multi-product allocation; baseload or non-productive energy; cross-site comparability; indicator not meaningful as defined; other; not stated.

**adaptation** — rolling window; segmented baseline; change-point; additional normalisation variable; hybrid physical-statistical; online re-estimation; outlier exclusion; weighted estimation; normalisation to a reference product; improved metering; other.
**status** — proposed (future, recommendation, conclusions "could/should"); implemented (done in the study); evaluated (compared with an alternative in the study).
**normative_framing** — ISO 50001/50006 explicit (the adaptation is justified by citing the standard); implicit (vocabulary of the standard — EnPI, EnB, relevant variables — without citing it for this adaptation); absent.
**addresses_mechanism** — K-id of the mechanism that the article EXPLICITLY links to this adaptation; empty if it does not. Never infer the link.

**C5 data_origin** — dedicated meter; site meter; invoice or utility bill; process historian tag; calculated from process data; laboratory assay; simulation; not reported.
**C5 boundary** — exact; allocated by rule; allocated by estimate; mismatch acknowledged; not reported. Origin and boundary are independent.
**C6 regime** — not stated; explicitly none in period; fixed, not mentioned; periodic, interval stated; event-triggered, trigger stated; rolling window; online or adaptive. A regime is declared only if the article says when/how the baseline is redone.
**C7 statement** — stated with numeric bounds (gives numerical limits of the model's validity); stated qualitatively; not stated.
**C8 OOS status** — reported (error on data NOT used in the fit: hold-out, cross-validation, test period); not reported; not applicable. Training R² is not out-of-sample validation.
**C13** (data_available / code_available) — yes; partial (some instances); no; not reported; not applicable. Data tabulated in the article itself count as available data only if they are the data used in the model.

## Output

Write a JSON file (list) with one object per item, ALL the items of the batch:
{"id": "MEC-001", "citacao_na_pagina": true|false, "veredicto": "confirma" | "corrige" | "nao_sustenta" | "retirar",
 "correcoes": {"campo": "novo valor"},   // only if veredicto = corrige; fields: effect, cause, claim, adaptation, status, framing, addresses, value
 "retirar_motivo": "...",                 // only if retirar (not a model limitation / duplicate / other)
 "confianca": "alta" | "media" | "baixa",
 "duvida": true|false,                    // true if confianca != alta OR veredicto != confirma
 "razao": "≤ 2 sentences in European Portuguese, concrete",
 "evidencia": "≤ 25 words of the page text that decide the question"}

(Keys and values were kept in Portuguese because they are the keys of the output files: `citacao_na_pagina` quotation on the page; `veredicto` verdict — `confirma` confirms, `corrige` corrects, `nao_sustenta` does not support, `retirar` remove; `correcoes` corrections; `retirar_motivo` reason for removal; `confianca` confidence — `alta`/`media`/`baixa` high/medium/low; `duvida` doubt; `razao` reason; `evidencia` evidence.)
