> Translated from Portuguese for this release. Original: `ANALISE_CONTEUDO_2026-09-15.pt.md` (same folder), SHA-256 `b568bd84688a05baeeb2738928108f3215262b7838ff86110eaefd477a7c625b`. The original is the record; this translation is for reading.

# Stage C — what the 41 records say, and what can already be written
Date: 2026-09-15 · Basis: 41 validated records (0 problems), 49 applications, 144 models, 146 mechanism occurrences, 92 adaptations, 30 dossiers with 642 anchored quotations.

> **Level of evidence of everything below.** This is the extractor's reading, with every quotation anchored to its page, and nothing more. It is not V1 (human verification of each occurrence), nor V2/V3. The numbers serve to decide where to read, and to write the chapter after reading — not to go straight into a results table.

*Note added for the release: this working analysis precedes the decision of 2026-09-17 that reduced Corpus B to 40 (39 charted), the September model re-reading and the October 2026 human checks. Its counts are not those of the article.*

---

## 1. The five findings the corpus gives, and that bear writing

### 1.1 The literature reports symptoms, not causes
The `mechanism_cause` axis is almost empty: **92 of 146 occurrences (63%) are `not stated`** and another 19 are `other` — 76% with no recordable physical cause. The causes the thesis anticipated do not appear: **fouling = 1, catalyst deactivation = 0, equipment degradation = 1.**

This is stronger than the registered R4 ("the mechanisms are not those the thesis predicted"): the papers describe what goes wrong **with the model** and almost never say what in the process caused it. It is at once a finding about the literature and a finding about the instrument — one of the two registered axes returns almost nothing, and that has to be declared.

### 1.2 `claim_status` changes the composition of the result — it is the methodological backbone
**41 of 146 occurrences (28%) are `general`**: textbook statements, not results of the study. Practically the same as the pilot measured (27% in 30). But what matters is not the percentage, it is that **the order of the effects changes depending on whether everything or only what is demonstrated is counted**:

| effect on the model | papers (all occurrences) | papers (excluding `general`) |
|---|---|---|
| indicator not meaningful as defined | 16 | 12 |
| non-stationarity of the relationship | 15 | 12 |
| **statistical misspecification** | **13** | **8** |
| **observability gap — quantity not measured** | **12** | **12** |
| data quality — missing/erroneous/discontinuous | 11 | 10 |
| cross-site comparability | 11 | 10 |
| baseline drift or expiry | 7 | 4 |
| multi-product allocation | 6 | 3 |

`statistical misspecification` falls 13→8 and `baseline drift` 7→4: these are complaints the literature **repeats**. `observability gap` stays 12→12: it is never a textbook statement, it is always something someone found in the case. Counting all occurrences measures what the literature repeats, not what it demonstrates. That is the defect the field has, and the one the field justifies.

### 1.3 The registered prediction about effects is wrong — in two directions
R4 expected "observability, allocation and baseline drift to dominate". They do not: the leaders are `indicator not meaningful as defined` (22 occurrences), `statistical misspecification` (20) and `non-stationarity` (18); allocation has 8 and baseline drift 8. It has to be reported as a contradiction of the registered expectation, not silenced.

### 1.4 The papers propose a lot, and almost nothing anchored to the standard
**37 of 41 papers propose at least one adaptation** (92 in total; only 4 propose nothing). **The registered R7 — "two thirds propose nothing" — is inverted.** Two readings are possible, and both have to go into the text: either the expectation was wrong, or the instrument is generous in what it counts as an adaptation — **30 of the 92 (33%) are `other`**, which is a sign of a short taxonomy.

R6 ("normatively unanchored"), by contrast, holds well: `absent` 51, `implicit` 32, **`ISO 50001/50006 explicit` only 9 — 10%**.

R8 ("rarely linked to the mechanism they address") is badly worded: **46 link, 46 do not.** Half is not "rarely". The sentence has to change.

### 1.5 Reproducibility: the equations come, the rest does not
Over 41 papers: equations `yes` 24, coefficients `yes` 12, data available `yes` 4, **code available `yes` 0** (40 `not reported`, 1 `partial`). Zero code sharing in a corpus of 41 energy-modelling papers is a number that writes itself.

---

## 2. What supports the instrument results (R10–R13)

| field | reading |
|---|---|
| **C7 validity envelope** (144 models) | `not stated` 110 (76%), qualitative 16, **numerical bounds 18 (12.5%)** |
| **C6 re-estimation** | `fixed, not mentioned` 93 (65%), `not stated` 18, event-triggered 19, rolling 6, periodic 4, online 4 |
| **C8 out-of-sample** | `reported` 13 (9%), `not reported` 67, `not applicable` 64 · design: `none` 37, held-out 18, in-sample residuals only 7 |
| **C5 data origin** (169 entries) | `not reported` 55, calculated from process data 48, dedicated meter 23, site meter 17, invoice 7, simulation 12, historian tag 7 |
| **C5 boundary correspondence** | `not reported` 77, **`exact` only 50 (30%)**, allocated by rule 21, allocated by estimate 14, mismatch acknowledged 7 |

R10 — "the energy quantity is frequently **not** measured at the studied boundary" — carries the most weight per unit of evidence and is the one read against the Sines case. Exact correspondence is a minority.

---

## 3. Composition of the corpus, and what it does to SQ4

Sectors (49 applications): cement 11, steel and metals 10, petrochemicals 7, multiple 6, **refining 5**, pulp and paper 3, glass 3, continuous chemicals 2, industrial gases 1, outside the registered ones 1.

`refinery_or_petrochemical_case`: **14 applications with an empirical application** (7 refining + 7 petrochemical), 3 named without an application, 32 not.

This confirms what the matrix already said: most of the mechanism evidence is outside refining. Any number taken from the 11 of the core is a number about refining, not about the literature.

---

## 4. Can it be written yet?

**Yes, and more than it seems — but not the part that has not been verified yet.**

**Writable now, with no further verification:**
- The whole method chapter: protocol, PRISMA-ScR flow, the amendment and its three deviations, the instrument and the defects found and closed, the triage design, and the table of verification levels. It is the part most theses do badly, and this one has serious material.
- **Layer A (SQ1, R16–R18)**: it is not re-extracted; it rests on the Tier-3 instrument already registered. Nothing in Stage C changes what the chapter can say about SQ1.
- The descriptive characterisation of the corpus (§3 above) — **but only after deciding R0**: today those fields feed no registered result, and without R0 it is an unregistered result.

**Writable after targeted reading (not of the 1 364 cells):**
R1, R5, R6, R8 and R14 are existential at V1. They have the best evidence-to-effort ratio, and R5 is the backbone of the chapter.

**Not writable as registered:** R2, R3, R7, R12, R13 and part of R10 are denominators over the 42 and require V3, which the executed coverage does not have. Reportable at V2 over the sections read, declared.

**Blocked:** R15 / SQ4 until the blind-first reading of the 11.
