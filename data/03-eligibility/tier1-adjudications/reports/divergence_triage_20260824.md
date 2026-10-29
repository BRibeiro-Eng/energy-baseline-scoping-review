# Divergence triage — 2026-08-24

**Planning instrument only.** Validation Protocol C-2.3 §3-Step-2 forbids automatic
collapsing of any mismatch beyond the registered structural-ineligibility rule:
*"No other mismatch is automatically collapsed. In particular, any Tier-3 difference
on an eligible paper remains unresolved until anchored human adjudication."*
Every cell classified below still owes its adjudication. This document says where the
hours will go, not what the answers are.

Generated from `state/reconciled/` (448 papers), classifying the **1909 divergent
cells that survive `reconcile.py`'s normalisation** (case/whitespace, string-booleans,
one-sided parenthetical elaboration, list order, country token sets, B13b evidence
stripping). Note `a`=chatgpt, `b`=claude in the reconciled records.

## Summary

| bucket | T1_memb | T1_rem | T2 | T3 | T2_pend | total | share |
|---|--:|--:|--:|--:|--:|--:|--:|
| 1 · derived from a Tier-1 call | 0 | 0 | 0 | 586 | 356 | **942** | 49.3% |
| 2 · formatting / synonym | 0 | 0 | 2 | 13 | 56 | 71 | 3.7% |
| 3 · granularity | 0 | 0 | 4 | 96 | 0 | 100 | 5.2% |
| 4 · recall asymmetry (factual) | 0 | 0 | 26 | 91 | 0 | 117 | 6.1% |
| 5 · substantive disagreement | 90 | 113 | 205 | 271 | 0 | **679** | 35.6% |
| **total** | 90 | 113 | 237 | 1057 | 412 | **1909** | |

## Bucket 1 — derived from a Tier-1 call (942 cells, 49.3%)

Half the apparent workload is not independent work. These are cells where one twin
ran no Stage 2/3 at all for that paper, because it had classified the paper
ineligible or not-3B. Every one of them is downstream of a single Tier-1 membership
decision already queued in `tier1_membership`.

Once those 90 conflicts are adjudicated, each of these cells resolves without being
looked at: either §3-Step-2a forces the Level-A fields to `null` with provenance
`structural_not_applicable`, or the twin that skipped the stage owes a Stage-3-only
supplement. **Do not budget human minutes against them.**

## Bucket 2 — formatting / synonym (71 cells, 3.7%)

Same content, different characters. Includes PDF glyph artefacts (`"ofﬁce area"`
with an *fi* ligature vs `"office area"`) and null-vs-registered-absence-label.

| field | claude | chatgpt |
|---|---|---|
| `sector_of_activity` | "non-metallic mineral sector" | "Non-Metallic Minerals sector" |
| `sector_of_activity` | "office area" | "ofﬁce area" |
| `country_region` | "not applicable" | null |
| `country_region` | "not applicable" | null |

`reconcile.py` could absorb most of this class: Unicode NFKD folding, punctuation
stripping, and treating a registered absence label as equivalent to `null`. That is a
**protocol amendment**, not a code tweak — the normalisation rules are registered.

## Bucket 3 — granularity (100 cells, 5.2%)

Not identical, but not disagreement either: one twin is more specific than the other.
Concentrated in `sector_of_activity` (56) and `country_region` (40), and balanced
between twins (44 claude / 40 chatgpt more specific) — so it is a convention gap, not
a quality gap.

| field | claude | chatgpt |
|---|---|---|
| `country_region` | "Latin America (Brazil, Ecuador, Mexico, Colombia, Argenti | "Latin America" |
| `country_region` | "Tula, Mexico" | "Tula" |
| `sector_of_activity` | "automotive sector" | "automotive manufacturing sector" |
| `sector_of_activity` | "mechanical engineering" | "mechanical engineering sector" |

**One registered rule — "the more specific value wins, provided the less specific one
is not contradicted" — decides all 100 at once.** That rule has to be filed as a dated
amendment before it is applied, and each cell still gets its logged decision; but it is
one decision applied 100 times, not 100 decisions.

## Bucket 4 — recall asymmetry (117 cells, 6.1%)

**This is the bucket I initially mis-filed as trivial. It is not.** One twin lists an
enum member the other omits — `enpi_enb_model_types` (67), `ems_standard` (17). Whether
a paper does or does not use a simple intensity ratio alongside a physical model is a
factual question about the paper, and it feeds SQ2–4 directly.

| field | claude | chatgpt |
|---|---|---|
| `enpi_enb_model_types` | ["physical model", "ML", "simple intensity ratio"] | ["physical model", "ML"] |
| `enpi_enb_model_types` | ["physical model"] | ["physical model", "simple intensity ratio"] |
| `enpi_enb_model_types` | ["physical model", "simple intensity ratio"] | ["physical model"] |
| `enpi_enb_model_types` | ["SEC mean", "multiple regression", "other"] | ["SEC mean", "multiple regression"] |

Direction is balanced (57 claude superset / 42 chatgpt) — unlike the eligibility
asymmetry, neither model is systematically the more inclusive reader here. Budget these
at full adjudication cost.

## Bucket 5 — substantive (679 cells, 35.6%)

All 203 Tier-1 conflicts, plus 205 Tier-2 and 271 Tier-3 cells where the twins assert
different things. This is the irreducible core.

## Tier-3 after the derived block collapses

The `tier3` queue reads 1057. **471 cells over 237 papers is the real figure** — 586
are bucket 1.

| field | fmt | gran | recall | subst | total |
|---|--:|--:|--:|--:|--:|
| `sector_of_activity` | 3 | 56 | 0 | 75 | 134 |
| `enpi_enb_model_types` | 0 | 0 | 67 | 51 | 118 |
| `country_region` | 10 | 40 | 0 | 55 | 105 |
| `type_of_organisation` | 0 | 0 | 0 | 42 | 42 |
| `ems_standard` | 0 | 0 | 17 | 5 | 22 |
| `regulatory_driver` | 0 | 0 | 1 | 14 | 15 |
| `complementary_methodologies` | 0 | 0 | 3 | 11 | 14 |
| `multi_site` | 0 | 0 | 0 | 12 | 12 |
| `mv_protocol` | 0 | 0 | 3 | 6 | 9 |

## What this changes about the plan

1. **Adjudicate `tier1_membership` first and the queue shrinks by half.** 942 cells
   are waiting on 90 decisions. The B-first execution order of §7 already puts these
   first; this quantifies why.
2. **Appendix A's ~7 h for Tier-3 was budgeted against 500–1,200 conflicts.** The
   honest denominator is 471, not 1057 — but ~271 of them are substantive, and
   `sector_of_activity` / `country_region` / `enpi_enb_model_types` carry 78% of the
   remaining load.
3. **Two registered amendments would retire ~171 cells** (buckets 2 and 3) as
   rule-driven rather than case-by-case: an extended normalisation rule and a
   granularity precedence rule. Both must be filed before use, and both still log
   per-cell decisions.
