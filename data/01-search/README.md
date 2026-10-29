# 01 — Search

Scopus and the Web of Science Core Collection, searched in February 2026, after which the protocol was registered (24 February 2026). The search strategy was therefore not prospectively registered.

| Database | String A (normative) | String B (methodological) | Total |
|---|---:|---:|---:|
| Scopus | 468 | 486 | 954 |
| Web of Science Core Collection | 263 | 261 | 524 |
| **Total** | 731 | 747 | **1478** |

After deduplication in Rayyan, 925 unique records were screened (`data/02-screening/`). The flow, with the source of each number, is in `docs/prisma/PRISMA_FLOW_2026-09-17.md`.

## Strings (Scopus syntax)

**A (normative)**

```
TITLE-ABS-KEY("ISO 50001" OR "ISO 50006") AND PUBYEAR > 1995 AND DOCTYPE(ar OR cp OR re)
```

**B (methodological)**

```
TITLE-ABS-KEY(("energy performance indicator*" OR "EnPI" OR "energy baseline*" OR "EnB"
  OR "energy performance measurement" OR "energy performance monitoring")
  AND ("industrial" OR "industry" OR "manufacturing" OR "facility" OR "organization"
  OR "management system" OR "energy management" OR "ISO 50001" OR "continuous process" OR "refin*"))
  AND PUBYEAR > 1995 AND DOCTYPE(ar OR cp OR re)
```

In the Web of Science, `TITLE-ABS-KEY` was replaced by `TS`, `PUBYEAR > 1995` by `PY=(1996-2026)`, and the document types by `DT=(Article OR Proceedings Paper OR Review)`.

The per-record origin (which string and database retrieved each record) was not kept in the analytical file, so a yield analysis by string was not possible (deviation D14).
