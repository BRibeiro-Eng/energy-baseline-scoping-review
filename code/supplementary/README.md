# Supplementary tables

```bash
python3 code/supplementary/make_supplementary.py            # writes results/supplementary/
```

Python 3.10+ (standard library); `openpyxl` for the workbook (CSV files are written without it).

- `corpus_b_state.py` builds the analysed state of the Corpus B records: records → September 2026 verification decisions (`code/verification_v1/overlay.py`) → corrections of the later checks that the article applies. It returns a log of every later correction (Table S2f).
- `make_supplementary.py` checks 27 counts of the article against that state and against `results/corpus-a/tables/analysis_dataset.csv`, then writes Tables S1–S3.
