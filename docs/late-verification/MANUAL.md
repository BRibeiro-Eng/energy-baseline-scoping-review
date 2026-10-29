> Translated from Portuguese for this release. Original: `MANUAL.pt.md` (same folder), SHA-256 `38026ba5c551edbb77811ad349990b85ee7b75ff9b7719ad572d128173ce07a0`. The original is the record; this translation is for reading.

# Manual — Amendment 3: late verification (14–31 Oct 2026)

*Release note: this is the working manual written for the reviewer before the checks, addressed to him in the second person; "me" is the assistant that prepared the bench. Execution departed from it where the results say so (`data/06-late-verification/RESULTS.md`, `docs/deviations.md`): D14 was not done, the D11 escalation was done for membership only, and the records were deposited on GitHub/Zenodo instead of OSF. Paths are those of the working directory of the review; in the package, `tarefas/` is `data/06-late-verification/tasks/` and `respostas/` is `responses/`.*

What you are going to do: execute, in this order, the instruments of Amendment 3 to TDW6C. They are four registered deviations done now (D13, D11, D10, D14) and the human verification of Corpus B that replaces D7. The bench (`bancada.py`) shows you each item and saves each decision. `relatorio.py` turns everything into the article's numbers.

**Hard deadline:** submission by **31 Oct** (APC waiver). Execution closes on **29 Oct**, which is the date written in the amendment. Whatever is not done by then is reported as not done.

---

## Map of the folder `level3_extraction/verificacao_2026-10/`

| File | What for |
|---|---|
| `MANUAL.md` | this manual |
| `lexico_camada_A.json` | layer A lexicon; deposit it together with the amendment |
| `AMENDMENT_FILED.txt` | interlock: you create it in step 0; without it nothing is drawn |
| `emenda/` | **exact** copy of the file you deposit on OSF |
| `dados/` | OpenAlex abstracts (already there), Rayyan export (step 0), D14 exports (step 8) |
| `build_tasks.py` | draws and generates `tarefas/` (runs once, after the deposit) |
| `bancada.py` | the interface, at http://127.0.0.1:8765 |
| `tarefas/` | what the bench shows; `tarefas/_ref/` holds the hidden references — **do not open** |
| `respostas/*.jsonl` | your decisions; append only, never edit by hand |
| `relatorio.py` | generates `RESULTADOS.md` + `resultados.json` |
| `d14_yield.py` | yield by string (step 8) |

You only need `python3`, no packages. Run everything from `~/LocalResearch/Screening/level3_extraction`.

---

## Calendar

| Day | Step | Hours (yours) |
|---|---|---|
| Wed 14 – Thu 15 | **0** · review, deposit and generate tasks | 1–1.5 |
| Thu 15 – Fri 16 | **2** · D13 exclusions; **3** · D11 retest | 2–3 + 3–4 |
| Sat 17 – Sun 18 | **4** · D7·A absences | 3–5 |
| Mon 19 | **5** · D7·B 80 cells | 5–6 |
| Tue 20 – Thu 22 | **6** · D10 Level-A audit | 10–13 |
| Fri 23 – Mon 26 | **7** · D7·C refining map | 8–13 |
| one evening with b-on | **8** · D14 | 1–2 |
| Tue 27 – Wed 28 | **9** · report and article update | 6–8 |
| Thu 29 | Mário reviews; deposit of the records on OSF | — |
| Fri 30 | **10** · submission (31 is slack) | 1–2 |

Total: about 40–55 h. The order is not cosmetic: it is that of the amendment (§7). D13 and D11 come first because they can change who is in Corpus A or B. Do not swap it without recording why.

---

## Step 0 · Review, deposit and generate the tasks (today–tomorrow)

**0.1 Review the amendment** (`OSF_Amendment_TDW6C_A3_late-validation_2026-10-14.docx`). Check in particular:
- §1: the sentence "not prospective with respect to the review's results". It is true and it is what protects you; do not soften it.
- §3.1: the escalation becomes **binding** with a single false negative in the D13 random sample. If you do not accept re-screening the 326 in that case (≈ 11 h), change this **before** depositing, never after.
- §3.2: the retest escalation with more than one flip in the same field means re-deciding up to 67 decisions (≈ 6 h). Same reasoning.
- §4.2: n = 80 cells. You can lower it to 60 before the deposit; afterwards, no.
- §4.3: the 13 reports of Table A1 are those of the article's map.

**0.2 Rayyan export with abstracts — before `build_tasks`.** Today 126 of the 326 excluded records have no abstract (OpenAlex gave 200). The D13 lexicon census runs on title + abstract, so the abstracts must come in **before** the draw.
- In Rayyan: open the review → *Export* → CSV, with *abstracts* included.
- Save as `verificacao_2026-10/dados/rayyan_export.csv`.
- The script accepts `key` + `abstract` columns; if `key` is missing, it links by title.
- If Rayyan does not give the abstracts, go on without them. D13 records the source of each abstract and counts separately those without one.

**0.3 PDF of the amendment.** In Word: *File → Save as → PDF*. Deposit the PDF, as you did with C-2.3.

**0.4 Deposit on OSF.** Project **wh62r** → *Files* → *OSF Storage* → *Upload*:
- the amendment PDF;
- `lexico_camada_A.json`.

Open the PDF on OSF and copy the **GUID** from the URL (`osf.io/xxxxx`, five characters).

**0.5 Local copy and interlock.**
```bash
cd ~/LocalResearch/Screening/level3_extraction
mkdir -p verificacao_2026-10/emenda
cp ~/Downloads/OSF_Amendment_TDW6C_A3_late-validation_2026-10-14.pdf verificacao_2026-10/emenda/
shasum -a 256 verificacao_2026-10/emenda/*.pdf
cat verificacao_2026-10/AMENDMENT_FILED.txt.template   # copy, fill in and save without .template
```
The fields are `deposited:` (YYYY-MM-DD), `osf_file:` (GUID) and `sha256:` (the hash above). `build_tasks` refuses to run if the hash does not match a file in `emenda/`.

**0.6 Generate the tasks and freeze the draw.**
```bash
python3 verificacao_2026-10/build_tasks.py
git add verificacao_2026-10 && git commit -m "Emenda 3: depositada (OSF <GUID>), tarefas sorteadas seed 44"
```
The commit dates the draw before you see any item. **Do not** run again with `--force` without writing in the log why.

What you should see, approximately:

| Module | Tasks |
|---|---|
| d13 | 13 + 50 (changes with the Rayyan abstracts) |
| d11 | 30 |
| d7a | ≈ 65 |
| d7b | 80 |
| d7c | 13 |
| d10 | 40 |

---

## Step 1 · Using the bench

```bash
python3 verificacao_2026-10/bancada.py
```
The browser opens at http://127.0.0.1:8765. To stop: Ctrl+C. To resume, run it again: the state comes from the files.

- **Top:** one tab per module, with progress and time spent (time per item is measured automatically and goes into the report).
- **Left:** the list of items. ○ to do · orange ● = blind decision committed, reveal/conclusion pending · purple ● = done. "Only pending" filters the list.
- **PDF ↗** opens the PDF in a new tab, at the right page when there is one.
- **Cmd+Enter** presses the main button of the footer.
- **Drafts:** what you write in an item is kept in the browser until you save. Even so, do not leave items half done.
- **Blind modules (D11, D10, D7·C):** first you decide, then you **commit (irreversible)**, then you reveal the reference, then you conclude. The bench does not let you reveal without committing, nor rewrite a committed decision. Each reveal is logged with its time.
- **End of the day:** `git add verificacao_2026-10/respostas && git commit -m "respostas <dia>"`.

**Rules you do not break:**
1. You do not open `tarefas/_ref/`, the forms, the dossiers, the thesis or the article while doing a blind item. The bench cannot stop you; you are the one who guarantees it.
2. You do not edit `respostas/*.jsonl`. If you made a mistake in a non-blind module, go back to the item and save again: the last one counts, with the history. In a blind module, the error stays and you explain it in the note of the conclusion.
3. In D10 you follow the **order of the list**, which is the order of the draw. Only then does a cut at 30 remain a random sample.
4. You report everything, including what goes wrong.

---

## Step 2 · D13 — exclusions at screening (2–3 h)

**What it is:** 13 excluded records that the continuous-process lexicon caught (census) plus 50 drawn from the rest. For each, you decide whether the exclusion stands.

**How to decide.** Use the registered screening criterion: **could** the record present, propose, evaluate or criticise an EnPI/EnB model? When in doubt, it went to full text. It is not the eligibility question; it is "should I have gone to look at the PDF?".
- No abstract: open the DOI. If there is still no abstract, decide on the title and write so in the reason ("title only").
- The *chips* fill in frequent reasons; edit them if they do not fit.

**If you mark "should have proceeded":**
- find the PDF and decide eligibility (Corpus A? Corpus B?);
- record in `verificacao_2026-10/dados/d13_seguimento.md` the key, the decision, the page and the quotation;
- it is reported by name as a late inclusion, and does **not** enter the counts.

**Escalation (binding):** if **any** of the 50 of the random sample is "should have proceeded", you re-screen the titles and abstracts of the remaining excluded records before submission. Tell me and I generate the extra module.

## Step 3 · D11 — test–retest (3–4 h)

**What it is:** 30 of your 90 September decisions (67 on eligibility, 23 on Corpus B membership), drawn at random. You decide again, from the PDF only.

**How:**
1. Read the question and the criterion (the "Criteria" button opens the stage 1 prompt).
2. Open the PDF and decide Yes or No. Record the page and the quotation, or "not reported after full-text reading" with the grounds.
3. Commit. Then reveal the original decision.
4. If there is a **FLIP**, you re-adjudicate: final value, evidence and why they diverged. That final value is the one that counts for the corpus.

**Escalation:** more than one flip **in the same field** requires re-deciding all the other decisions of that field among the 90 (up to 67 or up to 23). Tell me and I generate the module. Each re-adjudicated flip that changes membership of Corpus A or B changes the article's counts.

## Step 4 · D7·A — census of absences by lexicon (3–5 h)

**What it is:** each unit is one report × one family of terms. Only units with matches appear; the others are recorded as "no match" automatically. Start with the core T, F, K, C, Q; R and V only at the end, if there is time.

**Screen:** on the left, what the extraction coded in that field; on the right, each match with context and a link to the page.

**Decision:**
- **(a) no relevant match:** the term appears, but not in the sense of the family. Example: "regeneration" in regenerative burners, for K.
- **(b) relevant and already coded:** the extraction already has it.
- **(c) relevant and NOT coded:** an omission. Page, quotation, affected field and corrected value are mandatory.

**What counts as relevant, by family:**

| Family | Counts if… |
|---|---|
| **T** | the model is evaluated on data it did not use in the fit. **Always** note whether those data are from a period **after** the fit (temporal block test), because that is what the article claims never happens. A random 80/20 split is out of sample but **not** a temporal block. |
| **F** | fouling, deposits or degradation are named as a cause of change in the energy relationship or of model error/limitation. An equipment cleaning described as a saving measure does not count, unless the text links it to the model. |
| **K** | catalyst activity, deactivation, regeneration or cycle named as such a cause. |
| **C** | code or data of the model available (repository, supplementary material, on request). |
| **Q** | quality or composition of the feed or the product used or discussed as an explanatory or normalising variable. |
| **R** | a rule or practice for re-estimating or updating the model or the baseline. |
| **V** | a validity domain for using the model. |

## Step 5 · D7·B — 80 cells (5–6 h)

**What it is:** 80 of the 350 cells on which the Corpus B results rest, drawn at random. Each shows the current value (already with the September decisions), the quotation and the page.

**Decision:**
- **Correct**;
- **Incorrect**, with the right value;
- **Undetermined**, with the reason (excluded from the denominator and reported separately).

The definitions of the values are in `stage_c/PROMPT_EXTRACTION.md` and `stage_c/verification_v1/verificacao_modelo/CODEBOOK_verificador.md`. Judge the value, not the quotation: if the value is right but the quotation is weak, it is "correct" with a note.

## Step 6 · D10 — Level-A audit (10–13 h, the heaviest block)

**What it is:** 40 Corpus A reports, drawn as in `audit_sampler.py`. For each you extract **blind** the Level-A fields on which the two models agreed. The other fields are listed as "outside the audit", because divergent or single-surface cells do not enter n_v. Not asking for those fields does not change the metric.

**How:**
1. Open the PDF; the definitions are in the buttons *Definitions (stage2)* and *Article type (stage1)*.
2. Fill in each field:
   - enum: "(no value in the text)" if the article does not say;
   - multi: tick `none` if none applies;
   - text: empty = no value.

   Page and quotation are optional, but they help when you reveal.
3. Commit and reveal. For each cell, classify the difference:
   - **same**;
   - **extraction error**;
   - **my error (extraction right)**: you went back to the PDF and the extraction was right;
   - **equivalent after normalisation**: the same content written another way.

   In free text (country, sector), "same" means no substantive difference; if not, justify.
4. **Registered metric = raw difference** (what you committed blind vs the agreed value). Your classification appears beside it, as "adjudicated".

**Escalation:** e_v ≥ 3 in a field requires a recheck of that field over the whole corpus. If it does not fit by 29 Oct, the field is reported marked as having reached the threshold.

**Permitted cut:** if time runs short, you stop at **30** (always a prefix of the list).

## Step 7 · D7·C — refining/petrochemical map (8–13 h)

**What it is:** the 13 reports of the article's map, read from end to end, with the coded values hidden until you commit.

**Mind the honesty:** it is **not blind-first**. You have already seen these values (map, Table A4, dossiers). The text says "values withheld during reading, after prior exposure". Even so, read the PDF as if you did not know.

**The five fields** (the strongest level among the report's models):

| Field | Options |
|---|---|
| C5 · boundary | exact / allocated (by rule or estimate) / mismatch acknowledged / not reported |
| C6 · re-estimation | declared and executed / declared, not executed / fixed or not stated |
| C7 · validity domain | numerical bounds / qualitative / not stated |
| C8 · out of sample | reported / not reported / not applicable |
| Temporal block | test on observations after the fit: yes / no / not applicable |

Each field takes evidence (page + quotation, or "not reported after full-text reading"). After the reveal you choose the final value; if it differs from yours or from the coded one, a reason is mandatory.

## Step 8 · D14 — yield by string (1–2 h)

You need b-on access (VPN or the NOVA network). The strings are in the protocol, §4.1:

**String A (Scopus):**
```
TITLE-ABS-KEY("ISO 50001" OR "ISO 50006") AND PUBYEAR > 1995 AND DOCTYPE(ar OR cp OR re)
```

**String B (Scopus):**
```
TITLE-ABS-KEY( ("energy performance indicator*" OR "EnPI" OR "energy baseline*" OR "EnB" OR "energy performance measurement" OR "energy performance monitoring") AND ("industrial" OR "industry" OR "manufacturing" OR "facility" OR "organization" OR "management system" OR "energy management" OR "ISO 50001" OR "continuous process" OR "refin*") ) AND PUBYEAR > 1995 AND DOCTYPE(ar OR cp OR re)
```

**In WoS (Core Collection):** replace `TITLE-ABS-KEY` with `TS=`, `PUBYEAR > 1995` with `PY=(1996-2026)` and `DOCTYPE` with `DT=(Article OR Proceedings Paper OR Review)`.

**Exports and files:**
- Scopus → *Export* → CSV, with at least *Title*, *DOI* and *Year*.
- WoS → *Export* → *Tab delimited file*, *Full Record*. The limit is 1000 per export; if exceeded, export in two and join.
- Save in `verificacao_2026-10/dados/d14/` as `scopus_A.csv`, `scopus_B.csv`, `wos_A.txt` and `wos_B.txt`.
- Run: `python3 verificacao_2026-10/d14_yield.py`.

Note the date and time of the search and the counts each database shows: they go into the article and into the execution note.

## Step 9 · Report and article (27–28 Oct)

```bash
python3 verificacao_2026-10/relatorio.py      # RESULTADOS.md + resultados.json
```
Send me `RESULTADOS.md` (and `D14_RESULTADOS.md`) and I update the article:
- **Table A2 (deviations):** the column becomes "Executed late (date); results in …" for D10, D11, D13 and D14. D7 is described by layers A–C. D12 keeps the reason of §3.4.
- **Methods, 3.4–3.5:** new validation paragraph; the sentence "absences not verified" goes or changes according to layer A.
- **Results:** every count that changes is replaced, and what changed is said.
- **Limitations:** "executed after the results were known" and "not blind-first in Corpus B".
- **Conclusion:** the D7 sentence goes into the past ("was completed…") or, if something was left undone, says exactly what.
- **Data availability:** points to the deposit of the next step.

**Deposit of the records on OSF (wh62r)**, before submission:
- `tarefas/` including `_ref/`;
- `respostas/`;
- `RESULTADOS.md` and `resultados.json`;
- `dados/d14/D14_RESULTADOS.md`;
- the scripts;
- the git commit hash.

## Step 10 · Submission (30 Oct)

- [ ] Final PDF compiled, reviewed by Mário
- [ ] Cover letter: editor's invitation, waiver until 31/10, scoping review, nothing submitted elsewhere
- [ ] Suggested reviewers (MDPI usually asks for 3–5; no conflicts of interest, from different countries)
- [ ] Supplements S1–S3 and PRISMA-ScR checklist (not published)
- [ ] CRediT confirmed with Nuno and Mário
- [ ] ORCID and affiliations the same everywhere; personal e-mail as corresponding
- [ ] Generative AI statement updated (the bench was written with AI; no decision was taken by AI)

---

## If time gets tight — cut order (already covered by the amendment)

1. Families **R** and **V** of D7·A (2nd priority): left undone and reported as such.
2. **D14:** stays "not done".
3. **D10** reduced from 40 to **30** (prefix of the list).
4. **D7·C** partial: the completed reports are reported by name.

**Never cut** D13, D11, the core of D7·A or D7·B: they are what supports the article's claims. Any other cut, outside these four, is a new deviation and must be declared.

## Common problems

| Symptom | Cause / solution |
|---|---|
| `[interlock] …` | `AMENDMENT_FILED.txt` is missing or wrong, or the hash does not match the file in `emenda/` |
| The bench says "no tasks generated" | run `build_tasks.py` (step 0.6) |
| The PDF does not open | `data/pdfs/<key>.pdf` is missing |
| Port in use | `python3 verificacao_2026-10/bancada.py --port 8800` |
| You committed a wrong blind decision | there is no way back; explain in the note of the conclusion. That is how it should be. |
