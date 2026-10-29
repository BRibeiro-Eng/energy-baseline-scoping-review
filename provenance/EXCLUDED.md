# Material not released

Paths are relative to the working directory of the review (`level3_extraction/`). Each line states why the material is not in the package.

| Material | Reason |
|---|---|
| `data/pdfs/, data/pdfs_incoming/, data/pdfs_quarantine/, stage_c/verification_v1/pdfs/` | Full texts of copyrighted publications. |
| `output/stage0/, stage_c/payloads/, production/*/inputs/` | Page-by-page full text extracted from the PDFs (model input). |
| `data/ocr_recovered/` | Full text recovered by OCR. |
| `stage_c/verification_v1/_bundle_verificacao_modelo_2026-09-17.json.gz` | Contains the page text given to the September verifier (24 706 strings, up to 10 kB each). |
| `production/reviewer_workspace/evidence_packets/` | Reading aids for Tier-1 adjudication; each holds the abstract and verbatim excerpts of the PDF (median 5.5 kB). The decisions themselves are released in data/03-eligibility/tier1-adjudications/records/. Regenerable from the PDFs with code/pipeline/reviewer_workspace/review_evidence.py. |
| `output/fn_census/triage/contexts/` | Keyword-in-context excerpts of the PDFs shown during false-negative triage. Verdicts are released; contexts are regenerable from the PDFs. |
| `verificacao_2026-10/dados/abstracts_openalex_excluded.json; abstract fields in all released tables` | Publisher abstracts are not redistributed. Records keep the DOI; abstracts can be re-fetched from OpenAlex. |
| `data/articles.csv field `notes`` | Database export notes with author correspondence addresses and e-mails (527). Only the screening decision is extracted. |
| `output/dossiers/, production/stage_c/review_pack/, production/stage_c/blind_first_worksheets/, output/forms/` | Working material for the thesis and reviewer worksheets superseded by the released records; contain excerpts of full texts. |
| `output/*backup*, output/_stage0_stale_pre_v22_backup/, output/reopen_backup_*, output/security_quarantine_*, production/archive/, production/*/tmp/, production/claude/outputs/quarantine/` | Superseded copies and backups. |
| `bibliometrics/_backup_2026-09-21/, bibliometrics/results/corpus_a_2026-09-17/, bibliometrics/results/union_inclusiva/, figures in PNG/SVG` | Earlier or non-registered runs; only the registered run (corpus_a_registado) is released, figures as PDF. |
| `bibliometrics/.venv/, caches, __pycache__, .DS_Store, *.log, .claude/` | Environments, caches and local logs. |
| `../LOTE_A_setor/, ../LOTE_B_ambos/, ../LOTE_C_elegibilidade/` | Temporary working copies; contain PDFs. |
| `production/stage_c/claude/work/*.raw.json, *.stderr.txt` | Raw model transcripts of each Corpus B run attempt (up to 100 kB each). The validated records and the per-attempt metadata (model, timing, tokens, hashes) are released. |
| `Desktop/Screening/_archive_download_campaign/` | Full-text retrieval tooling; contains a messaging-app session file and a browser profile with cookies. Never released. |
