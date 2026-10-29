# Documentation

- `registration.md`: OSF registration, amendments with their OSF identifiers and SHA-256, filing records.
- `amendments/`: byte-identical copies of the deposited amendments and the term list, plus the filing records.
- `protocol/`: operational protocols under which the extraction and validation ran (AI-assisted extraction protocol, Validation Protocol C-2.3, Stage C specification, result → field → verification matrix, false-negative census design and sampling amendment).
- `corpus-decisions/`: dated decisions on corpus membership (Tier-1 closure, reveal digest, corpus closure of 12 September 2026, Corpus B ⊂ Corpus A, the comparator retained outside the pipeline).
- `prisma/`: PRISMA-ScR flow with provenance of each number, checklist, the snowballing note (deviation D9).
- `late-verification/`: the manual of the October 2026 checks.
- `deviations.md`: D1–D17.
- `data-dictionary.md`: fields, vocabularies, Portuguese terms in the records.

Documents translated from Portuguese carry a header with the original file name and SHA-256; the original is kept beside them as `<name>.pt.md`.

## Terms in the article and in these files

The files keep the working names used while the review was carried out; the article uses plain descriptions. The correspondence is:

| Article | Files |
|---|---|
| Corpus B extraction with the instrument finalised on 13 September 2026 | Stage C; instrument frozen 13 September 2026 |
| values; coded values | cells |
| values used in the results (frame of 350) | result-bearing cells |
| separate model verification of the 368 quoted values (September 2026) | model re-reading; `model-reread-2026-09/` |
| full-text search for omissions; omission search (check c) | census of absences; lexicon census; module `d7a` |
| report–term-family pair | report–family unit |
| random sample of 80 values (check d) | module `d7b` |
| reading of the 13 refinery and petrochemical reports (check f) | module `d7c` |
| repeat decision; changed decision | re-decision; flip (modules `d11`, `d11x`) |
| Corpus A audit (check e) | module `d10` |
| title/abstract exclusion audit (check a) | module `d13` |
| check of publications wrongly left out of Corpus B | false-negative census / control |
| Corpus B membership | `level_3b` |
