# Changelog

## 1.0.1 (30 October 2026)

- Two links from adaptations to mechanisms pointed to mechanisms that the September 2026 model verification had removed: Hashim et al. (2019), adaptation D1 → K2, and Moghadasi et al. (2025), adaptation D1 → K1. Both links are now cleared when the analysed state is built (`code/supplementary/corpus_b_state.py`), and the change is listed in Table S2f.
- Consequence: adaptations explicitly linked to a mechanism go from 43 to 41 of 88 (Table 6 of the article: `Other` 16 → 15, `Outlier exclusion` 4 → 3). `make_supplementary.py` now also checks that every remaining link resolves to a mechanism in Table S2d.
- Tables S2e and S2f, `columns.csv` and the workbook regenerated. No other value changed.

## 1.0.0 (30 October 2026)

First release, deposited with the submission of the article.
