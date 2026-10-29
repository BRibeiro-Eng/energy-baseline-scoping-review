# 04 — Corpus A extraction (two model families)

`claude/` (Claude Code) and `chatgpt/` (Codex CLI) are two independent pre-extractions of the same 448 full texts with the same frozen prompts (`code/prompts/corpus-a/`). `reconciliation/cell_provenance.csv` says, cell by cell, whether the two agree after normalisation; only agreed values enter the Corpus A counts. Agreement is a routing rule, not a measure of reliability. The accuracy of agreed values was audited later on 40 random publications (deviation D10; `data/06-late-verification/`, module d10).
