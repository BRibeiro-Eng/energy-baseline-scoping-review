# PRISMA-ScR checklist (Tricco et al. 2018) — working copy

Submitted as non-published material. This copy carries, per item, **what this review actually
did** and **where it is reported**, so the page numbers can be filled in once the chapter is
paginated. Items marked ⚠ need a decision or a number from the reviewer before submission.

| # | Item | What this review does | Reported in | Page |
|---|---|---|---|---|
| **TITLE** |
| 1 | Title | Identifies the report as a scoping review. | Title | |
| **ABSTRACT** |
| 2 | Structured summary | Background, objectives, eligibility, sources, charting method, results, conclusions. State AI-assisted charting and single-reviewer screening in the abstract, not only in the methods. | Abstract | |
| **INTRODUCTION** |
| 3 | Rationale | Energy performance models (EnPI/EnB) under ISO 50001/50006 are specified for stable relationships; continuous process industry is where that assumption is least safe. Rationale is the structural gap, evidenced by Corpus B's share of Corpus A. | §1 | |
| 4 | Objectives | Review question and the four sub-questions, stated against the PCC (Population/Concept/Context). ⚠ **SQ4 was withdrawn 2026-09-16** — restate the objectives as SQ1–SQ3 and say in §5 that SQ4 was registered and withdrawn, with the reason. | §1 | |
| **METHODS** |
| 5 | Protocol and registration | Protocol registered on the Open Science Framework, **DOI 10.17605/OSF.IO/TDW6C**, before charting commenced. **Amendment deposited 2026-09-13** declaring three deviations (single extraction surface; 11 + 31 coverage instead of 40 + 2; no inter-model agreement statistic). Give the DOI, the registration date, the amendment date, and state that the amendment is public. | §2.1 | |
| 6 | Eligibility criteria | Presents, proposes, evaluates or critiques an EnPI and/or EnB model with sufficient detail to identify and characterise it; English; 1996 onward for database-sourced records (IPMVP/NEMVP milestone); article, conference paper or review. Validation is a charted variable, never a gate. Sector context never excludes. | §2.2 | |
| 7 | Information sources | Scopus (Elsevier) and Web of Science Core Collection (Clarivate), via b-on (NOVA). Searched **February 2026**. Grey literature from reference organisations only via backward snowballing. | §2.3 | |
| 8 | Search | Full Scopus syntax for Strings A and B, with the WoS translation, reproduced verbatim in an appendix. Report the calibration of five configurations and the five-anchor sensitivity check (4/5 captured; Karcher 2015 out of concept, enters by snowballing). | §2.3 + Appendix A | |
| 9 | Selection of sources of evidence | Three sequential levels in Rayyan: title, abstract, full text. **Single reviewer (B. Ribeiro)** — declared, not softened. ⚠ Levels 1 and 2 are reported **combined**: the export does not preserve which pass excluded a record (see flow, Gap 1). | §2.4 | |
| 10 | Data charting process | **This is the item that carries the AI declaration; do not bury it.** A pre-specified charting form (JSON Schema, frozen, sha256 `d855254b…e883ff`) was completed by a single large-language-model surface (Claude Code CLI, prompt tag v2.3.0-C, one clean session per report, tools disabled) operating as an instrument of the single reviewer, never as a second reviewer. Every charted value carries a verbatim evidence quote and a page locator; **every quote was checked mechanically against the physical page it cites** (41 records, 3 111 quotes: 3 097 exact, 4 with the page locator mechanically corrected and flagged, 10 routed for human reading). Records that failed validation were re-charted up to three times and otherwise quarantined; one report is quarantined and named. State plainly that **no independent human re-reading of the charted values was performed** and that results are reported as what the charting found, with the quote and page as checkable evidence. | §2.5 | |
| 11 | Data items | The charted variables, by level: Level A over Corpus A (year, country, sector, organisation type, model type, normative context, source string); Level B over Corpus B (C1–C13 model descriptors, mechanisms on two axes with a claim status, adaptations with normative framing and status, implementation barriers, reproducibility). Give the frozen schema as supplementary material. | §2.6 + Supplement | |
| 12 | Critical appraisal of individual sources of evidence | **Not performed** — consistent with scoping review methodology (Arksey & O'Malley 2005; Levac 2010; Tricco 2018; JBI ch. 11). Say so explicitly; an empty item reads as an omission. | §2.7 | |
| 13 | Synthesis of results | Descriptive bibliometric distribution for SQ1 over Corpus A; narrative synthesis for SQ2–SQ3 over Corpus B, organised by sub-question. No meta-analysis. ⚠ **Denominator claims over Corpus B are not made** under the executed coverage — results are existential or rank-ordered, and where a proportion is given, the denominator and the level at which it was verified are stated in the same sentence. | §2.8 | |
| **RESULTS** |
| 14 | Selection of sources of evidence | The flow diagram in the main text, with the numbers of `prisma/PRISMA_FLOW_2026-09-16.md` and exclusion reasons at full text. ⚠ Needs the snowballing yield S (flow, Gap 2). | §3.1 + Figure 1 | |
| 15 | Characteristics of sources of evidence | Year, country, sector, organisation type, model family, normative context over Corpus A; sector composition of Corpus B (cement 11, steel 10, petrochemicals 7, multiple 6, refining 5, pulp & paper 3, glass 3, continuous chemicals 2, industrial gases 1, off-list 1, over 49 applications). | §3.2 + Table 1 | |
| 16 | Critical appraisal within sources of evidence | Not applicable — see item 12. | §2.7 | |
| 17 | Results of individual sources of evidence | Per-report charting available as supplementary material: 41 extraction forms and 41 reading dossiers, each quote page-anchored. | Supplement | |
| 18 | Synthesis of results | SQ1 distribution; SQ2 mechanisms by effect on the model, separated by claim status; SQ3 adaptations and their normative anchoring; reproducibility. | §3.3–3.6 | |
| **DISCUSSION** |
| 19 | Summary of evidence | Main findings against each sub-question, and against the registered expectations — including the two the corpus reversed (R7, R8) and the one it redirected (R4). A review that reports where its registered expectation failed is stronger than one that only confirms. | §4.1 | |
| 20 | Limitations | Single reviewer for screening and charting. Non-retrieval of 137 reports, measurably non-random, with the missingness table. Charting by a single AI surface with no independent human re-reading; verification level declared. English-only. Grey literature partial. Corpus-B membership closed by a registered sector list, so the 13 exploratory cases sit outside every count. **SQ4 registered and withdrawn for time, with the consequence that the review makes no literature-based transferability claim for refining.** | §4.2 | |
| 21 | Conclusions | Interpretation against the objectives, and what the gap implies for measurement practice in continuous process industry. | §4.3 | |
| **FUNDING** |
| 22 | Funding | ⚠ State the funding of the review and the role of the funders, and the internship relationship with Galp. Declare any competing interest arising from the case site. | §5 | |

---

## The four ⚠ before submission

1. **Snowballing yield S** — the one number the flow still needs (item 14).
2. **Objectives restated without SQ4**, with the withdrawal reported in the methods (items 4, 20).
3. **Funding and competing interests**, including the Galp internship (item 22).
4. **How proportions are phrased** (item 13): every proportion carries its denominator and its
   verification level in the same sentence, or it is not written.

## Two statements the journal asks for explicitly

**PRISMA adherence.** *"This scoping review was conducted and is reported in accordance with the
PRISMA extension for Scoping Reviews (PRISMA-ScR; Tricco et al., 2018). The completed PRISMA-ScR
checklist is provided as supplementary material."*

**Registration.** *"The review protocol was registered on the Open Science Framework
(DOI: 10.17605/OSF.IO/TDW6C) prior to the commencement of data charting. An amendment declaring
three deviations from the registered charting design was deposited on 13 September 2026 and is
publicly available at the same registration."*
