# Reproducing the results

What can be recomputed from this package alone, and what cannot.

## 1. Check integrity

```bash
sha256sum -c provenance/checksums.sha256        # every file of the package
sha256sum docs/amendments/*.pdf docs/amendments/lexico_camada_A.json   # compare with docs/registration.md
```

## 2. Late verification (October 2026) — fully reproducible

Python ≥ 3.10, standard library only.

```bash
bash code/late-verification/reproduce.sh
```

The script rebuilds `resultados.json` from `data/06-late-verification/tasks/` and `responses/` and compares it with the released file. The samples themselves can be redrawn with `code/late-verification/build_tasks.py` (seed 44, simple random sampling over sorted frames), but this needs the working directory of the review, including the full texts, which are not released; `tasks/MANIFEST.json` gives the hash of every task file so that a redraw can be checked.

The review bench (`code/late-verification/bancada.py`) is the local interface the reviewer used (stdlib HTTP server on 127.0.0.1). It is released for inspection: it shows how blind modules withheld the reference values (`tasks/_ref/`) until a write-once commit. It needs the PDFs to run.

## 3. Corpus A analysis — outputs released, rerun needs the working layout

`code/bibliometrics/run_analysis.py` (Python 3.13; `code/bibliometrics/requirements.txt`; versions in `results/corpus-a/package_versions.json`) produced `results/corpus-a/`. It reads the two model extractions and the screening export from the working layout of the review and enriches metadata from OpenAlex and Crossref; the enrichment cache and the abstracts are not released. The agreement rule (deviation D15) is in `code/bibliometrics/biblio/data.py`; its cell-level output is `data/04-extraction-corpus-a/reconciliation/cell_provenance.csv`, from which every Corpus A count of the article can be recomputed by filtering `status == "model agreement; no full human validation"`.

## 4. Corpus B tables — outputs released, rerun needs the working layout

`code/corpus-b-tables/tabelas_cap3.py` aggregates the 39 records in `data/05-extraction-corpus-b/records/` into `results/corpus-b/tabelas_cap3_2026-09-18.json`. It expects the records at `production/stage_c/claude/outputs/` relative to the review root; `provenance/source-map.tsv` gives the original location of every file.

## 5. Model-assisted extraction — not reproducible by rerunning

The extractions were produced by subscription applications (Claude Code, Codex CLI) whose model versions are not pinned. Rerunning the prompts in `code/prompts/` with later versions will not necessarily give the same values. The released records are the frozen outputs; every aggregate in the article is computed from them.
