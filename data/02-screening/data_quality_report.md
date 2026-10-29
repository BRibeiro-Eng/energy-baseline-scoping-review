# Data Quality Report — Pre-flight Audit of Level 3 Corpus

**Generated:** 22 May 2026 (original); **updated 2 June 2026** (1st manual recovery batch); **updated June 2026** (2nd manual recovery batch).
**Universe:** 599 Level 3 papers (355 Included + 244 Maybe) per OSF protocol v2; **596 after de-duplication** (see §2.3).
**PDFs available:** 443 (74.3% of 599 universe; **post-recovery and post-quarantine**). Remaining 153 awaiting future download cycles.
**Scope of this report:** systematic verification of file-content correctness, encoding integrity, and duplicate detection *before* AI-assisted extraction begins, plus documentation of recovery batches added subsequently.

This report is part of the methodological annex of the thesis. It documents data quality issues detected and resolved prior to charting, alongside their disposition.

---

## 1. Methodology

A pre-flight script (`preflight_scan.py`) was run over the 373 PDFs to compute, per file:

- MD5 hash (for inter-file duplicate detection).
- Page count, total chars, mean chars/page (PDF text-extraction quality).
- ASCII letter fraction over the first 5 000 chars (byte-level garbled detection).
- Common-English-word match count over the first 5 000 chars, using a curated 35-word list including domain terms (energy/system/process/...) — calibrated empirically. A well-extracted research paper scores 50+; garbled extractions score < 8.
- Fuzzy title match (`rapidfuzz.partial_ratio`) of the expected title (from `articles.csv`) against the first two pages of the PDF.
- DOI grep across the full PDF text.

Output: `preflight_scan.csv` (one row per paper, with flags). Manual inspection of every flagged paper followed.

Heuristic flags raised:

| Flag | Trigger |
|---|---|
| `image_only` | mean chars/page < 100 |
| `truncated_or_preview` | total chars < 5 000 |
| `garbled_bytes` | ASCII letter fraction < 0.45 in a sample > 500 chars |
| `garbled_glyphs` | ASCII letter fraction OK but common-word matches < 8 (encoding-shift / glyph remap) |
| `wrong_pdf_likely` | title match < 70 AND DOI not found AND text is extractable |
| `hash_duplicate` | two or more PDFs share MD5 |

---

## 2. Findings — by category

### 2.1 Wrong-PDF files (n = 9) — quarantined

Files where the PDF content does not match the expected paper. These were either copied from the wrong source during the download phase or had identifier mix-ups in the b-on retrieval pipeline. **All nine are moved to `pdfs_quarantine/wrong_pdf/`** and added to `redownload_queue.json` for recovery once the FCT institutional IP / PerimeterX issue is resolved.

| Key | Expected (per articles.csv) | Actual PDF |
|---|---|---|
| rayyan-472535360 | Knayer & Kryvinska (2025) *Energy Reports* — EnMS vs EMS | UBA German Klimaschutz report 2018 |
| rayyan-472535447 | Kasturi & Ayalur (2022) *Energy for Sustainable Development* — textile SME India | Adelaar et al. (2004) Canadian Textiles NRCan study |
| rayyan-472535555 | Ali & Jaiswal (2019) IYCE — tire mfg energy audit | Russell & Gerdes (2016) IEEE TCS — four-wheel steer-by-wire |
| rayyan-472536454 | Kanchiralla et al. (2021) *Applied Energy* — food industry EnPI | Cacciari (2005) *Revista de Letras* — Portuguese toponymy |
| rayyan-472536458 | Woo et al. (2021) *Building and Environment* — blockchain energy MRV | Same Cacciari literary paper (shared MD5) |
| rayyan-472536459 | Abd Rahman et al. (2021) *J Building Engineering* — hospital green cert | Same Cacciari literary paper (shared MD5) |
| rayyan-472536529 | Gheorghiu et al. (2019) CIEM — university campus power | Kaleem & Chang (2016) IEEE Access — PS-LTE |
| rayyan-472535800 | Stănoiu (2011) — Standards for EnMS (II) | Kohl Springer book "Standards for Management Systems" |
| rayyan-472535801 | Stănoiu (2011) — Standards for EnMS (I) | Same Kohl book (shared MD5) |

Note: 472535800/801 were not caught by the title-match heuristic alone (the book title "Standards for Management Systems" partially matches the expected paper title "Standards for energy management systems"); they were identified by the hash-duplicate check combined with manual verification.

### 2.2 Garbled extractions, fully recovered via OCR (n = 4) — pipeline-eligible

These PDFs are the correct papers, but pymupdf and pdfplumber both fail to extract clean text because the embedded fonts use non-standard glyph mapping (e.g. "LPSOHPHQWLQJ" instead of "Implementing" — a glyph remap that renders visually correct but stores wrong Unicode codepoints).

OCR via tesseract on the rendered page images recovers clean text (242–364 common-word matches). The OCR output is saved in `ocr_recovered/{key}.txt`; **Stage 0 must use this file as the text source for these four papers** instead of pymupdf output.

| Key | Title (recovered) | OCR result |
|---|---|---|
| rayyan-472535622 | Boreiko et al. (2017) RTUCON — Implementing Energy Efficiency in Glasswork Company | 17 130 chars, 242 common words |
| rayyan-472535635 | Szajdzicki (2017) EEEIC — Metering for Energy Management | 18 753 chars, 258 common words |
| rayyan-472535679 | Anisimova (2016) PICMET — Energy Management System Formation | 25 834 chars, 364 common words |
| rayyan-472536601 | Ramli & Hamid (2017) CENCON — Two systems in municipal sewage TP | 20 511 chars, 248 common words |

### 2.3 Hash-identical duplicates — Rayyan dedup failures (n = 3 secondary keys) — excluded

These pairs of records refer to the **same underlying work** published in two venues (a conference paper followed by a journal article, or a journal paper followed by a book chapter). The Rayyan deduplication did not catch them at the earlier screening levels. The hash-identical PDFs confirm they refer to one work.

The primary (journal version, more citable) is kept; the secondary is added to `excluded_duplicates.json` and **skipped by the pipeline**. PRISMA flow diagram should record three duplicates removed at full-text screening.

| Primary kept | Secondary excluded | Note |
|---|---|---|
| rayyan-472536713 (T&F journal 2012) | rayyan-472536731 (WEEC 2010 conference) | Jolly & Atoulikian "Turning vision into reality" |
| rayyan-472535793 (Energy journal 2012) | rayyan-472535803 (ECOS 2011 conference) | Ates & Durakbasa "Corporate EM Turkey" |
| rayyan-472535662 (Mgmt & Mktg journal 2016) | rayyan-472535876 (book chapter 2016) | Păunescu & Blid "Effective energy planning" |

**Universe after dedup: 596 papers** (was 599; three secondaries removed).

### 2.4 Truncated / preview-only (n = 2) — flag, no quarantine

Both papers have only the abstract / first-page preview as PDF, totalling ~1 200 chars each. Not wrong content; partial download. **Kept in `pdfs/` with `truncated_or_preview` flag** — Stage 1 LLM will likely return inconclusive eligibility, in which case they go to `needs_review.md` for the reviewer's manual decision. Full PDFs may be re-downloaded later.

| Key | Total chars | Title (from preview) |
|---|---|---|
| rayyan-472535535 | 1 323 | Gomez Dorta et al. "Energy efficiency indexes for coffee sector in Honduras" |
| rayyan-472535758 | 1 146 | Anisimova "Energy-economic analysis of corporate activities" (WASJ 2013) |

### 2.5 False positives of the scan — corrected, kept in pipeline

Two papers were flagged by the heuristic but verified as **correct PDFs** during manual review:

| Key | Why flagged | Reality |
|---|---|---|
| rayyan-472535371 | `wrong_pdf_likely` initially considered — page 1 starts with references from preceding article | Journal layout: pages 2-6 are the correct Deryabin (2025) *Eurasian Mining* paper. Verified by full-text inspection. |
| rayyan-472535678 | (Not flagged by scan; was raised by external review) | Text extracts cleanly; standard Elsevier paper. No issue. |

Two other scan flags were also false positives on the garbled-bytes heuristic:

| Key | Flagged as | Reality |
|---|---|---|
| rayyan-472535370 | `garbled_bytes` (ASCII frac 0.28) | Correct PDF (Penev et al. 2025 IOP "Green transition in Orlandovtsi"). Low ASCII fraction is from heavy figure content, not garbled text. Common-word matches were 69 — well above threshold. |
| rayyan-472535542 | `garbled_bytes` (ASCII frac 0.445) | Correct PDF (Menghi et al. 2019 J Cleaner Production review). Same explanation. Common-word matches 125. |

This is a known limitation of the composite heuristic: `ascii_letter_fraction` triggers on PDFs with heavy graphical content even when text extraction is fine. The composite rule (`garbled_bytes` only fires when ALSO `common_word_matches < 8`) was added after these false positives were identified, but the legacy flag remained in `preflight_scan.csv`. Stage 0 in the pipeline now uses the strict composite rule and will not quarantine these.

---

## 3. Disposition summary

| Category | Count | Disposition |
|---|---|---|
| Wrong PDF | 9 | `pdfs_quarantine/wrong_pdf/` + `redownload_queue.json` |
| Garbled, OCR-recovered | 4 | OCR text in `ocr_recovered/`; Stage 0 prefers this source |
| Rayyan duplicates (secondary) | 3 | `excluded_duplicates.json`; skipped by Stage 0 |
| Truncated/preview | 2 | Flagged; Stage 1 likely → `needs_review.md` |
| Scan false positives | 4 | Verified correct; pass through normally |
| **Clean (no flags)** | **351** | Normal pipeline |

**Effective corpus entering the LLM pipeline:** 351 + 4 (OCR) + 2 (truncated) = **357 PDFs**.

**Net universe reduction:** 599 - 3 (duplicates) = 596 papers in PRISMA universe.

**Pending re-download (when IP issue resolves):** 226 (already missing) + 9 (wrong-PDF re-download queue) = **235 PDFs** to recover.

---

## 4. For the thesis methodological annex

Suggested text for the methodological note:

> *"Before AI-assisted extraction commenced, a pre-flight data-quality audit was performed on the 373 PDFs available at the time of the pilot. Three issues were detected systematically: nine PDFs contained the wrong paper (file-name/content mismatch from the download pipeline); four PDFs contained the correct paper but with corrupted text extraction due to non-standard glyph encoding, recovered via OCR; and three pairs of Rayyan-screening duplicates (same work in two venues) were identified by MD5 hash. The wrong-PDF files were quarantined for re-download; OCR-recovered text was used in place of native extraction for the four affected papers; and the three duplicate pairs reduced the universe to 596 unique papers, with the removals recorded in the PRISMA flow diagram. Two preview-only PDFs were flagged for the reviewer's manual handling. The full audit, including the `preflight_scan.py` source, is preserved in the extraction repository for reproducibility."*

---

## 5. Manual recovery batch — June 2026

A second batch of 61 PDFs was added by the reviewer through manual download via b-on (papers initially in `redownload_queue` and `missing_papers`). The same preflight checks were applied; results below.

### 5.1 Matching pipeline

Files arrived with heterogeneous filenames (ScienceDirect PII, AIP DOI fragments, free-form titles, opaque hashes). Matching against `articles.csv` used:

1. **DOI extraction** from filename (PII for Elsevier, AIP pattern) AND from first 2 PDF pages via regex.
2. **Title fuzzy match** (`rapidfuzz.fuzz.token_set_ratio`) over two query sources: (a) cleaned filename, (b) PDF first-2-pages text. Titles shorter than 30 characters in the CSV were excluded to avoid generic-title contamination (an earlier run with `partial_ratio` against all titles incorrectly mapped four different papers to the 3-word generic title "Energy management system" — `rayyan-472536661`. The token_set_ratio + min-length filter eliminates this class of error).

### 5.2 Results

| Category | Count | Disposition |
|---|---|---|
| DOI exact match | 7 | Renamed and copied |
| Title fuzzy match ≥99 | 48 | Renamed and copied |
| Title fuzzy match ≥87 (verified manually) | 2 | One **corrected** before applying (see 5.3); other accepted |
| Manually corrected (wrong-key in matcher) | 2 | See 5.3 |
| Eliminated (out of scope) | 2 | Moved to `novos/_eliminated/`, not deleted |

### 5.3 Manual corrections to the matcher's output

- **`20140948a.pdf`**: matcher proposed `rayyan-472535677` (Scheihing 2016 WEEC "The value of superior energy performance® and ISO 50001"). Inspection of the PDF first page revealed it is *Scheihing 2014 CEP magazine* "Save Energy through the Superior Energy Performance Program". The correct CSV key is `rayyan-472535723` (Scheihing 2014). Applied as override.
- **`machine+learning.pdf`**: matcher proposed `rayyan-472535365` (Moghadasi 2025 *Energy Sources Part A* "Applying machine learning techniques..."). Inspection of the PDF revealed it is *Santolamazza, Cesarotti, Introna 2018* "Evaluation of Machine Learning techniques to enact energy consumption control of Compressed Air Generation in production plants" (Summer School Francesco Turco). The correct CSV key is `rayyan-472536579`. Applied as override.

### 5.4 Eliminations

- **`bulletin_tpu-2015-326-8-05.pdf`** — Bulletin of Tomsk Polytechnic University 2015. PDF text is predominantly Russian (24 863 Cyrillic characters vs 1 276 English-word tokens). Violates the OSF protocol §3 language criterion (English only). No corresponding CSV key. Moved to `novos/_eliminated/`.
- **`c6b062b5c119d163242782adb027a3ec.pdf`** — 90 KB, 104 characters total, contains only "Reproduced with permission of the copyright owner. Further reproduction prohibited without permission." (ProQuest placeholder; download failed). No retrievable content. Moved to `novos/_eliminated/`.

### 5.5 OCR-recovered (additional)

- **`rayyan-472535520`** (Aized et al. 2020 *Pak. J. Engg. Appl. Sci.* "Implementation of ISO 50001:2001 framework in a textile unit of Pakistan"): PDF is image-only (12 pages, 0 chars extractable via pymupdf or pdfplumber). OCR via tesseract recovered the text cleanly (3 183 chars per page in the page-1 sample), saved to `ocr_recovered/rayyan-472535520.txt`. Total `ocr_recovered/` entries: now **5** (was 4).

### 5.6 Post-recovery preflight scan

Preflight scan re-run on the resulting 423 PDFs. Of the 59 newly added: **58 pass all checks cleanly**; 1 (`rayyan-472535520`) flagged `image_only` + `truncated_or_preview` but has OCR-recovered text. **0 wrong-PDFs** introduced (matcher acted conservatively after the manual corrections in 5.3).

### 5.7 Updated corpus state (after 1st recovery batch)

| Metric | Pre-recovery | After 1st batch |
|---|---|---|
| PDFs available | 364 | **423** |
| Effective corpus (after dedup, quarantine, etc.) | 357 | **416** |
| Universe remaining without PDF | 232 (226 missing + 6 wrong-quarantined still pending) | **173** |
| Coverage of 596 PRISMA universe | 60.9% | **70.6%** |

## 5b. Manual recovery batch — 2nd round (June 2026)

A second manual batch of 22 PDFs was processed using the same pipeline (`match_novos.py` → manual review → `apply_moves.py`).

### 5b.1 Results

| Category | Count | Disposition |
|---|---|---|
| DOI exact match | 5 | Renamed and copied |
| Title fuzzy match ≥97 | 13 | Renamed and copied |
| Title fuzzy 80–96 — manually verified, accepted | 2 | One via override (Raether ambiguous) |
| Manually corrected (wrong-key in matcher) | 2 | Two wrong-PDF dups — see 5b.2 |
| Eliminated (out of scope) | 2 | Moved to `novos/_eliminated/` |

### 5b.2 Manual corrections to the matcher's output

- **`An_integrated_energy_management_strategy_for_the_deep-level_gold_mining_industry.pdf`**: matcher proposed `rayyan-472535493` (Bovkun 2021 ICOECS "Energy management using the ISO 50001 standard"). Inspection of the PDF revealed it is *Bredenkamp, Mathews, Vosloo 2016* — exactly that title. The correct CSV key is `rayyan-472535660`. Applied as override.
- **`paper5.pdf`**: matcher proposed `rayyan-472535724` (Brown & Desai 2014 "The ISO 50001 energy management standard"). Inspection of the PDF revealed it is *Brogan, Galata 2015* "The VERYSchool Project: Valuable EneRgY for a smart School - Intelligent ISO 50001 Energy Management Decision Making in School Buildings". The correct CSV key is `rayyan-472535710`. Applied as override.
- **`86_Raether_A_Joint_Effort_for_Energy_and_Cost_Efficient_Heat_Traetments_2015_cfi.pdf`**: matcher labelled as ambiguous (title fuzzy 84). Manual inspection confirmed it is *Raether 2015 CFI* "EnerTHERM-a Joint effort for energy and cost efficient heat treatments" = `rayyan-472535695`. The score was low because the CSV title carries the "EnerTHERM" research-project prefix that the filename lacks. Applied as override.

### 5b.3 Eliminations

- **`Towards Model-based Integration of Management Systems.pdf`** — Rößler & Schlieter 2015 *Wirtschaftsinformatik Proceedings 2015*. The matcher pointed at `rayyan-472535736` ("Towards model-based energy management", Rößler 2014 MKWI 2014) but the two papers are *not the same*: this 2015 paper is about model-based integration of management systems generically (not specifically energy management). Not in CSV. Out of scope for the EnPI/EnB review.
- **`42663-Texto del artículo-86675-1-10-20240905.pdf`** — Universidad del Zulia, *Revista de la Facultad de Ciencias Económicas y Sociales* Vol XXX No 3, 2024. Spanish-language journal. Violates the OSF protocol §3 language criterion (English only). No corresponding CSV key.

### 5b.4 Preflight scan after 2nd batch

Preflight scan re-run on the resulting 443 PDFs. Of the 20 newly added: **all 20 pass all checks cleanly**. **Zero new issues introduced**. Total flag frequencies unchanged from after the 1st batch (the 4 wrong-PDF flags, 3 garbled, etc., are all pre-existing).

### 5b.5 Cumulative corpus state

| Metric | Original | After 1st batch | After 2nd batch |
|---|---|---|---|
| PDFs available | 364 | 423 | **443** |
| Effective corpus | 357 | 416 | **436** |
| Universe remaining without PDF | 232 | 173 | **153** |
| Coverage of 596 PRISMA universe | 60.9% | 70.6% | **74.3%** |
| OCR-recovered texts | 4 | 5 | 5 |
| Wrong-PDF quarantined (re-download queue) | 9 | 9 | 9 |
| Rayyan duplicates excluded | 3 | 3 | 3 |

### 5.8 Updated suggested text for thesis methodological annex (replaces §4 wording)

> *"Before AI-assisted extraction commenced, a pre-flight data-quality audit was performed on each batch of PDFs delivered to the pipeline. Across two acquisition phases (database+OA search, completed May 2026; manual b-on retrieval, completed June 2026), 423 PDFs were collected against the 596 unique Level 3 papers. Issues detected by the audit and resolved before LLM extraction: nine PDFs contained the wrong paper (file/content mismatch from the download pipeline), all quarantined for re-download; five PDFs contained the correct paper but with corrupted text extraction due to non-standard glyph encoding, recovered via OCR; three pairs of Rayyan-screening duplicates (same work in two venues) were identified by MD5 hash and the secondary records excluded. The wrong-PDF files were tracked in a redownload queue; OCR-recovered text was used in place of native extraction for the five affected papers; and the three duplicate pairs reduced the PRISMA universe to 596 unique papers. Two papers acquired manually were eliminated: one violated the English-only language criterion (Russian text); the other consisted only of a copyright placeholder. Two manual corrections to the automatic file/key matcher were applied where the matcher had assigned the wrong key (one due to year confusion within a multi-paper author corpus, one due to a generic filename matching a CSV entry with a more specific title). The full audit, including the `preflight_scan.py` source and the `apply_log.md` for the June recovery batch, is preserved in the extraction repository for reproducibility."*

---

## 6. Files referenced

| File | Purpose |
|---|---|
| `preflight_scan.py` | The audit script. Re-run after new PDFs arrive. |
| `preflight_scan.csv` | Per-paper audit results. |
| `pdfs_quarantine/wrong_pdf/` | The 9 quarantined PDFs from May 2026 batch (kept for audit, not deleted). |
| `redownload_queue.json` | Tracking file for the 9 wrong-content keys to redownload. |
| `ocr_recovered/{key}.txt` | OCR-recovered text for the 5 PDFs with corrupt/image-only text extraction. |
| `excluded_duplicates.json` | The 3 Rayyan duplicates to skip. |
| `data_quality_report.md` | This document. |
| `../../novos/_processed/` | The 59 successfully recovered PDFs from June 2026 batch (originals preserved with original filenames). |
| `../../novos/_eliminated/` | The 2 eliminated PDFs from June 2026 batch (Russian + placeholder). |
| `../../novos/apply_log.md` | Per-file decision log for the June 2026 manual recovery batch. |
| `../../novos/matching_report.{csv,md}` | Automated matching results before manual corrections. |
