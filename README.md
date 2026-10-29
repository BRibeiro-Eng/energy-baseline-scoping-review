# Energy baseline validity in continuous process industries — scoping review package

This repository holds the records, instruments, code and derived results of the scoping review

> Ribeiro, B.; Miranda, N.; Eusébio, M. *Energy Baseline Validity in Continuous Process Industries: A Scoping Review and Implications for Emission-Reduction Claims*. Submitted to *Advances in Carbon Neutrality* (MDPI), 2026.

The protocol was registered on the Open Science Framework on 24 February 2026 (DOI [10.17605/OSF.IO/TDW6C](https://doi.org/10.17605/OSF.IO/TDW6C)). The registration and its amendments stay on OSF; this package holds what was produced while executing them. `docs/registration.md` lists every registered file with its OSF identifier and SHA-256.

**Not included:** the full texts of the publications reviewed, and any file that holds their page text (model inputs, reading aids, the September verifier bundle). Records identify publications by DOI or bibliographic reference. Publisher abstracts are also removed. `provenance/EXCLUDED.md` lists each excluded item and why.

## Where each result in the article comes from

| Article | What | File(s) |
|---|---|---|
| §3.2, Fig. 1 | 1478 records (Scopus 954, Web of Science 524); 925 after deduplication | `docs/prisma/PRISMA_FLOW_2026-09-17.md`, `data/01-search/` |
| §4.1, Fig. 1 | 925 screened, 326 excluded at title/abstract | `data/02-screening/records_screened.csv` (`screening_decision`) |
| §3.3–3.4 | 82 blind adjudications of divergent eligibility/membership decisions | `data/03-eligibility/tier1-adjudications/records/` |
| §3.3, §4.1 | Corpus A = 331, Corpus B = 40 (39 charted), 13 exploratory cases | `data/03-eligibility/corpora.csv`; `docs/corpus-decisions/CORPUS_CLOSURE_2026-09-12.md` |
| §3.4 (D6) | Corpus B false-negative control | `data/03-eligibility/false-negative-census/` |
| §4.2 (SQ1) | Corpus A distributions (e.g. ISO 50001 family, M&V protocols, model families) | `results/corpus-a/tables/*.csv`, figures in `results/corpus-a/figures/` |
| §3.4, D15 | Agreement rule between the two model extractions; which cells enter the analysis | `data/04-extraction-corpus-a/reconciliation/cell_provenance.csv`; extractions in `data/04-extraction-corpus-a/{claude,chatgpt}/validated/` |
| §4.3–4.7 | Corpus B: 46 applications, 140 models, 163 measurement entries, 130 mechanism and 88 adaptation occurrences | `data/05-extraction-corpus-b/records/`; aggregated in `results/corpus-b/tabelas_cap3_2026-09-18.json` by `code/corpus-b-tables/tabelas_cap3.py` |
| §3.4 (D7) | Model re-reading of 368 quoted cells: 234 confirmed, 111 corrected, 18 removed, 5 retained | `data/05-extraction-corpus-b/model-reread-2026-09/verifier/decisoes_2026-09-17.json` |
| §3.5, §4.8, Tables 7–8 | Checks added after the first analysis (D13, D11, D7-A/B/C, D10) | `data/06-late-verification/` (`resultados.json`, `RESULTS.md`, decision logs in `responses/`) |
| §4.4, §4.7 | Corrections applied after the census of absences (e.g. out-of-sample results, data availability 4 + 4) | `data/06-late-verification/responses/d7a.jsonl` (decision `c_missed`) |
| Figures | TikZ sources of the manuscript figures | `results/manuscript-figures/` |
| §4.7–4.8, Fig. 3, Table A4 | Values adopted from the reading of the 13 refinery reports | `data/06-late-verification/d7c_adoption.json` |
| Table A2 | Deviations D1–D17 | `docs/deviations.md` |

The counts in `results/corpus-b/tabelas_cap3_2026-09-18.json` are those of the dissertation (before the late verification). The article applies to them the corrections recorded in `data/06-late-verification/`; `docs/deviations.md` and `RESULTS.md` say which numbers changed.

## Layout

```
README.md  REPRODUCE.md  CITATION.cff  LICENSE  LICENSE-DATA
docs/          registration, protocol, amendments (as filed), corpus decisions, PRISMA, deviations, data dictionary
data/
  01-search/                 search strings and counts
  02-screening/              925 screened records (bibliographic fields + decision)
  03-eligibility/            Tier-1 adjudications, false-negative census, corpus membership
  04-extraction-corpus-a/    two independent model extractions (448 records each) and the reconciliation
  05-extraction-corpus-b/    39 Corpus B records, run metadata, quarantine log, September model re-reading
  06-late-verification/      tasks, frozen references, append-only decision logs and results (Oct 2026)
code/
  pipeline/                  extraction, validation, reconciliation, grounding and census code as executed
  prompts/                   frozen prompts, instructions and schemas (Corpus A and Corpus B)
  bibliometrics/             Corpus A analysis package
  corpus-b-tables/           Corpus B aggregation and evidence-map scripts
  late-verification/         task builder, local review bench, report generator
results/       Corpus A tables and figures, Corpus B tables, manuscript figure sources
provenance/    source map with SHA-256 of every source file, source commits, checksums, exclusions
```

Each folder has a short README.

## Language

The review was carried out in Portugal. Documentation is in English. Three kinds of material stay in Portuguese, because they are evidence and their hashes are cited elsewhere:

1. free-text notes and justifications written by the reviewer in decision records;
2. comments, docstrings and interface text of the code as executed;
3. a few working documents that were themselves registered or hashed.

Where a document was translated, the English file carries a header naming the original and its SHA-256, and the original sits next to it with the suffix `.pt.md`. Derived result tables use English labels; the Portuguese labels of the registered run are listed in `docs/data-dictionary.md`. Figure files in `results/corpus-a/figures/` keep the Portuguese labels of the registered run; `results/corpus-a/catalog.en.json` gives each figure's English title and caption.

## Integrity

- `provenance/checksums.sha256`: SHA-256 of every file in the package (`sha256sum -c provenance/checksums.sha256`).
- `provenance/source-map.tsv`: for each file, the source path in the working directory of the review and the source file's SHA-256 (different from the package file only where a transform was applied; transforms are listed in `provenance/build-report.json`).
- The amendment of 16 October 2026 (`docs/amendments/`) and its term list match the files deposited on OSF (`2zgx8`, `yn2mh`); `data/06-late-verification/tasks/MANIFEST.json` records the SHA-256 of every task file, the seed and the amendment hash.

## Use of language models

Pre-extraction, extraction and the September re-reading were done with Claude Code (Anthropic) and Codex CLI (OpenAI), as described in §3.4 of the article. Model identifiers, application versions and dates are in `provenance/run_metadata.json` and in each record. In the October 2026 checks, no model made or pre-filled a decision in modules d13, d11, d11x, d7a and d7b. In d10 (Corpus A audit) and d7c (refinery reports), the reviewer used ChatGPT (model reported as gpt-6.1-sol, high reasoning) to summarise the reports, locate passages and draft the recorded evidence and justifications, also after the reference values were revealed; the decisions were his (deviation D17, `docs/deviations.md`).

## Licences

Code: MIT (`LICENSE`). Data, documentation and figures: CC BY 4.0 (`LICENSE-DATA`). Bibliographic metadata of third-party publications are factual descriptors; quotations in the records are short excerpts kept as evidence for the coded values.

## Citation

See `CITATION.cff`. Please cite both the article and this archive (DOI on the Zenodo record).
