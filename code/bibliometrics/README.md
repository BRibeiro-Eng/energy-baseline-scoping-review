> Translated from Portuguese for this release. Original: `README.pt.md` (same folder), SHA-256 `a638d6489d56b8c52b296f25479d065b90341e8c9737469ac7df0c9009cceded`. The original is the record; this translation is for reading.

# Corpus A — bibliometrics, evidence mapping and PRISMA

*Release note: the run released in `results/corpus-a/` is the registered view (`--population a`, folder `corpus_a_registado`). The cache (`cache/`, including `input_snapshot.json` and the OpenAlex/Crossref responses) is not released, because it holds abstracts and the full export; without it the script cannot be rerun from this package. Paths below are those of the working directory of the review. The B∖A inconsistency described below was resolved on 2026-09-17 (`docs/corpus-decisions/B_SUBSET_A_2026-09-17.md`).*

The script `run_analysis.py` generates an HTML gallery, a PDF atlas, individual figures in PNG/PDF/SVG and CSV tables. The notebook `corpus_a.ipynb` runs the same script, shows data coverage and allows browsing figures and tables. No network access is needed to reproduce the run from the delivered cache.

## Run

```bash
cd /Users/bernardoribeiro/LocalResearch/Screening/level3_extraction/bibliometrics
.venv/bin/python run_analysis.py
```

The main output goes to `results/union_inclusiva/`. Open `index.html` to browse; `figures/atlas.pdf` holds all the figures and `figures/` the individual files.

To run only over the registered list of A:

```bash
.venv/bin/python run_analysis.py --population a
```

That output goes to `results/corpus_a_registado/`. The option `--output PATH` chooses another folder. `--enrich` queries only metadata not yet in the cache; existing responses are not replaced. Queries use the exact DOI, keep the provider and the date, and isolate title discrepancies for review.

In another environment, create a virtualenv and install `requirements.txt`. The versions actually used are written to `package_versions.json` in each output.

## Membership inconsistency found during implementation

The closure document declares A=331 and B=42, but the identifiers do not form nested sets. `corpus_profile.rosters()` produces:

| Set | Publications |
|---|---:|
| A registered | 331 |
| B registered | 42 |
| A ∩ B | 40 |
| A \ B | 291 |
| B \ A | 2 |
| A ∪ B | 333 |

Records `rayyan-472535628` and `rayyan-472535750` have both `methodological_eligibility=false` and `level_3b=true` in the source forms. The B list closed on 12/09/2026 also contains them.

The main view is therefore **exploratory A∪B (333)**: it includes all 42 records of B, once each, without modifying the eligibility decisions. The other view keeps the 331 of A and contains 40 records of B. This is not a protocol change nor an adjudication: it is a sensitivity analysis while the inconsistency is resolved. The definitive correction of the numbers needs that decision.

## Status of the content values

At this point there is no fully adjudicated Level A table. The implementation keeps every cell of the two extraction surfaces and uses in the main view only concordant values, marked as provisional. Divergences, single-surface extractions and missing cells remain unresolved. Agreement between models **is neither human validation nor a reliability estimate**.

`tables/model_surface_sensitivity.csv` keeps the separate distributions of the two surfaces. Gaps are not filled by automatically choosing a model. `config/verified_level_a.csv` allows values verified by a reviewer to be entered:

```csv
paper_id,field,value_json,verified,reviewer,evidence
```

`value_json` must hold a valid JSON value. Only rows with `verified=true`, a reviewer and evidence replace the provisional cell. The accepted fields are in `biblio/data.py`. The original extraction files are only read and never changed.

## Analyses implemented

- Annual/cumulative production, temporal composition by study type, sources, concentration, descriptive Bradford zones and author productivity distribution.
- Document/study types, multi-site studies, case countries, sectors, organisations, models, standards, M&V protocols and regulatory drivers.
- Cross-tabulations, comparison of the disjoint groups B / rest of the set, UpSet intersections, co-occurrence of models/standards and a fractional alluvial diagram.
- Co-authorship, country and institution networks; international and education–industry collaboration; funding sources and open access.
- Normalised keywords, co-occurrence network, exploratory clusters, temporal evolution, themes × content, title and abstract terms, NMF topics.
- OpenAlex, Crossref and historical export citation counts kept separate; distribution, citations by age, FWCI as provided by OpenAlex, local citations, identifiable local self-citations, direct network, bibliographic coupling, co-citation of references/authors/sources, most-cited references and age of references.
- Coverage, cell provenance, normalisation queues and identity discrepancies.
- PRISMA with documented counts, checked equations and explicit gaps.
- Adapters for new content fields and external metrics, which generate the analyses automatically when verified data become available.

The HTML catalogue and `tables/analyses_pending.csv` distinguish what was generated from what still depends on data. The code does not fabricate charts of missing metrics.

## Counting and interpretation conventions

1. The primary unit is the **publication**, not an independent study nor an installation.
2. Multiple-response fields: each publication counts once per category/cell; sums can exceed 100%. In comparisons, the denominators are the sizes of the disjoint groups; missing data are made explicit.
3. The alluvial diagram spreads a total weight of 1 per publication over all its combinations. Widths are not full counts. UpSet shows exact combinations.
4. The countries of A7 are the locations of the cases; the OpenAlex countries are the authors' affiliations.
5. The sector grouping by regular expressions is exploratory and checkable in `normalization_sector_mapping.csv`; it does not change A8 nor determine membership of B.
6. Networks use thresholds documented in the captions. The GEXF files allow inspection in other tools. Centrality and clusters do not demonstrate quality or causality.
7. Co-citation by author/source is restricted to the 80 most frequent references whose metadata resolution was attempted. The coverage achieved is stated.
8. Missing metadata is not zero. Citations by age are not field normalisation; FWCI is an external measure that depends on the provider's definition and coverage.
9. Exported names are not fully disambiguated. Do not read the rankings as an assessment of researchers or as the complete output of institutions.
10. The language English is the classification in the export. Translated or divergent titles at the providers are sent for review, not used to change eligibility.

## Fields still needed

- `source_strings.csv`: origin A/B/both and evidence from the search log. A12 is empty; null does not mean snowballing. Do not confuse strings A/B with Corpus A/B.
- `extended_content.csv`: new fields, extracted comparably and verified: variables, scale, data, duration, sampling, validation, updating, residuals, uncertainty, limits and reproducibility. Fields of B are not generalised to A.
- `external_metrics.csv`: attention in patents/policy or other metrics, always with provider, date and source. No career index is computed from this corpus.
- `prisma_pending.json`: initial totals per database, duplicates before screening and snowballing records. Null means **to be confirmed**, never zero.

## PRISMA and provenance

The flow uses the current export, the non-retrieval/exclusion records and the closure note. The historical file `Primeiro assisted screening/prisma_stats.txt` holds preliminary AI decisions (667 excluded) and **does not replace** the 326 exclusions of the current export.

Checked equations: 925=326+599; 599=3+596; 596=137+459; 459=11+448; 448=117+331. The full-text exclusions therefore sum to 128: 10 for language, 1 retraction, 117 for methodological eligibility. The reasons for these 117 need validated disaggregation. The inconsistency of the two B/A records is shown in the draft, without silently correcting the totals.

Methodological references and providers:

- [PRISMA 2020 — flow diagram templates, CC BY 4.0](https://www.prisma-statement.org/prisma-2020-flow-diagram)
- [VOSviewer — networks and techniques](https://www.vosviewer.com/features)
- [Bibliometrix/Biblioshiny — families of analysis](https://www.bibliometrix.org/biblioshiny/)
- [OpenAlex — API](https://help.openalex.org/api/)
- [Crossref — API access](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/)

`cache/input_snapshot.json` freezes the records used and the hashes of the source files. `run_manifest.json` records hashes of the code, configurations and metadata. Changing the corpus requires reviewing the inconsistency, saving the decision and explicitly updating the snapshot; a normal re-run does not change the composition.

## Check

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests check record conservation in PRISMA, inclusion of B without duplicates, per-publication counts, co-occurrence semantics, author parsing and the absence of automatic precedence for divergent cells. The notebook was prepared to run from top to bottom and keep compact outputs.
