# Snowballing not performed — what the omission costs, measured

Decision 2026-09-16, for time. The registered protocol (§16) specifies backward and forward
snowballing on the included corpus, with a supplementation trigger routed by cause. It was not
executed. **S = 0 by omission, not by yield.** A null yield would have been evidence about the
search's recall; an omission is not, and the report must not let the two read alike.

This note is the evidence for the limitation paragraph, so the cut is declared with a measurement
behind it instead of an assurance.

## Method

Every reference list of the 42 Corpus B reports was parsed from the frozen page payloads, split
into entries, and reduced to (first surname, year). Each was checked against the **whole** Rayyan
library — all 925 deduplicated records, whatever their screening decision, not just the 331
included. A surname absent from all 925 was never retrieved by either string at any level.

Coarse by construction: surname+year collides, corporate authors ("European", "National") are
noise, and a parser is not a librarian. It is a screen for recurrence, not a census. Every
conclusion below is drawn from names cited by **three or more** of the 42 reports.

## Finding 1 — the anchor the protocol expected to need snowballing is already in

`scoping_review_protocol_v2.docx` §4.4 records that four of five sensitivity-check anchors were
captured and that the fifth, **Karcher (2015)**, was not, and "enters formally through backward
snowballing". It is in the corpus: `rayyan-472535693`, screened as *Maybe*, retrieved, and passed
into full-text eligibility assessment. The protocol's note is stale. On the review's own
pre-registered recall test, snowballing had nothing left to recover.

## Finding 2 — a body of benchmarking literature is invisible to both strings

Cited by three or more of the 42 Corpus B reports and absent from all 925 records:

| cited by | surname | what it is |
|---|---|---|
| **10 of 42** | **Worrell** | industrial energy efficiency and benchmarking; much of it LBNL reports |
| 7 | Phylipsen | cross-country benchmarking of industrial energy efficiency |
| 6 | Bunse | energy efficiency in production management, gap analysis |
| 5 | Hasanbeigi | sector energy benchmarking (cement, steel, textiles) |
| 4 | Schulze | systematic review of industrial energy management |
| 3 | Azadeh · Abdelaziz · Festel · Gielen | efficiency modelling, energy management, sector outlooks |
| 5 · 4 · 3 · 3 | IEA · UNIDO · Eurostat · "Global…" | institutional and statistical sources |
| 3 | Jaffe (1994) | pre-1996 |

Three classes, and only one is a search gap:

1. **Institutional and statistical sources** (IEA, UNIDO, Eurostat, ISO, European Commission) are
   outside an article search by construction. The protocol routes them through the grey-literature
   channel, which is itself fed by backward snowballing — so cutting snowballing closes that
   channel too. Declare it.
2. **Pre-1996** (Jaffe 1994) is excluded by the registered temporal limit. Not a miss.
3. **Worrell, Phylipsen, Bunse, Hasanbeigi, Schulze** are the real signal. This is industrial
   energy **benchmarking and energy-management** literature that does not use the EnPI/EnB
   vocabulary String B is anchored on, and is often not ISO-50001-framed, so neither string
   reaches it. Worrell alone is cited by 10 of the 42 and appears nowhere in 925 records.

## What this means, stated at the right strength

Under the registered trigger (§16: `M_string ≥ 2` → expand the strings and re-run), this evidence
**would have fired supplementation**. That is the honest headline: the cut is not risk-free and
is not being reported as if it were.

What it is *not*: these are not reports that the eligibility criterion would have admitted as
EnPI/EnB **model** papers. They are the framing and benchmarking literature the included papers
build on — several of them reports rather than indexed articles. So the likely effect is on the
review's coverage of its own background, not on the SQ1–SQ3 charting. **Likely** is the correct
word; it was not tested, and the limitation says so rather than claiming no impact.

## Text for the limitations section

> Backward and forward snowballing, specified in the registered protocol, was not performed.
> A reference-list screen of the 42 analytical-corpus reports against the full deduplicated
> library found that the one sensitivity-check anchor the protocol expected to recover by
> snowballing was already retrieved by the database search, but also that a recurrent body of
> industrial energy benchmarking and energy-management literature — most visibly Worrell, cited
> by 10 of the 42 reports, and Phylipsen, Bunse, Hasanbeigi and Schulze — is absent from all 925
> screened records, because it does not use the EnPI/EnB terminology on which the methodological
> search string is anchored. Under the registered supplementation trigger this would have
> prompted an expansion of the search strings. The omission therefore bounds the review's
> coverage of the benchmarking literature that the included reports build on, and closes the
> backward-snowballing channel through which institutional grey literature was to be captured.
> Its effect on the charted results is expected to be limited, since the absent works are
> framing and benchmarking sources rather than reports presenting, proposing, evaluating or
> critiquing an EnPI/EnB model, but this expectation was not tested.
