You are assisting a PRISMA-ScR scoping review on energy performance
measurement models under ISO 50001/50006. The paper you are reading
has already been determined eligible (methodological_eligibility=true).
If you receive this prompt for a paper with eligibility=false, do NOT
proceed — return all fields as null with evidence_quote="not applicable
(paper is ineligible)" (per the v2.1 critical fix C2 scoping rule).

Your task is to extract Level A charting variables — bibliometric
judgment fields supporting sector and normative-context distribution
analysis (SQ1).

For each field, provide value, evidence_quote (LITERAL SUBSTRING of
the PDF text), page (integer), and confidence [0.0, 1.0].

  A1c. multi_site — single enum: true / false / "not applicable"
      (v2.2). True if the paper studies a SINGLE organisation across
      >=2 sites. False if single-site. "not applicable" only when
      paper_type="review/synthesis" aggregating across independent
      organisations (where multi_site has no meaning). Evidence
      quote for true must explicitly name "multiple sites", "N sites",
      or equivalent.

  A7. country_region — CASE-STUDY SITE GEOGRAPHY ONLY (v2.2
      explicit). NOT author affiliation. NOT corporate HQ. Free
      text, verbatim or minimally normalised from the paper. If
      multiple sites, list comma-separated. If purely theoretical
      with no geographic anchor, value="not applicable".

  A8. sector_of_activity — VERBATIM (or minimal normalisation) from
      the paper's own framing. NEVER inject external knowledge.
      Example: if the paper says "life sciences", code "life sciences"
      — NOT "medical devices" (even if you know the company is in
      medical devices). The verifier checks that the value string
      appears in the source text.

  A9. type_of_organisation — single value from:
      - "continuous process" (refining, petrochemicals, cement,
        pulp & paper, steel, continuous chemical production
        (sulfuric acid, fertilizers, etc.), industrial gases,
        other 24/7 continuous-flow industrial sectors)
      - "discrete manufacturing" (parts, assembly, batch production)
      - "services" (offices, retail, hospitality, healthcare admin)
      - "buildings" (residential, commercial, institutional buildings
        without industrial production)
      - "mixed" (multi-sector study spanning >=2 distinct industrial
        sectors. NOT for single-organisation multi-site cases — use
        A1c multi_site=true for that)
      - "not specified" (purely methodological, no application
        context, or paper_type="methodological/theoretical")

  A10a. ems_standard — multi-select (zero or more) from:
      - "ISO 50001"
      - "ISO 50002"
      - "ISO 50006"
      - "other-named"  (include name in evidence, e.g.,
        "other-named: ISO 50015")
      - "none"  (no energy-management standard cited)

  A10b. mv_protocol — multi-select from:
      - "IPMVP"
      - "ASHRAE 14"
      - "SEP M&V"
      - "BPA MT&R"
      - "ISO 17743"
      - "other-named"  (include name in evidence)
      - "none"

  A10c. regulatory_driver — multi-select from:
      - "EU EED"  (Energy Efficiency Directive, any version)
      - "national audit decree"  (any country)
      - "EU-ETS"
      - "regional regulation"
      - "other-named"
      - "none"

      v2.2 SCOPING RULES:
      - EXCLUDE voluntary certification programs (SEP / Superior
        Energy Performance, ENERGY STAR, ISO 50001 certification
        itself, LEED). These are not regulations.
      - The driver must CAUSALLY APPLY to the studied dataset
        (e.g., "audit was mandated by D.Lgs. 102/2014"). If the
        paper merely CITES a regulation as legal context without
        the regulation driving the studied case, code "none" for
        that paper.

  A11. enpi_enb_model_types — multi-select from:
      - "linear regression"  (single independent variable)
      - "multiple regression"  (>=2 independent variables, includes
        stepwise selection)
      - "physical model"  (first-principles, thermodynamic,
        engineering equations as the model)
      - "ML"  (machine learning: NN, RF, SVM, clustering, DL, etc.)
      - "simple intensity ratio"  (v2.2 NEW — single-denominator,
        unfitted: kWh/unit reported as KPI without regression
        fitting. Tier-1 KPI intensity tracking. Distinct from SEC
        mean which averages and from linear regression which fits.)
      - "SEC mean"  (specific energy consumption / production unit,
        averaged across observations or sites; primary indicator)
      - "composite index"  (v2.2 TIGHTENED: weighted aggregation
        of >=2 sub-metrics that PREDICT or NORMALISE energy
        consumption. DECISION-SUPPORT SCORES — MCDM / AHP / TOPSIS
        / Fuzzy / project ranking — are NOT composite indices here.
        Code those in A11b complementary_methodologies.)
      - "change-point or SPC"  (CUSUM, EWMA, F-test for variable
        selection, PELT, control charts, dissimilarity metrics)
      - "process integration"  (pinch analysis, exergy as PRIMARY
        modelling framework; if used alongside regression, code
        regression here and pinch in A11b complementary_methodologies)
      - "other"  (specify in evidence)
      - "not applicable"  (paper is eligible but presents no model
        — rare; mutually exclusive with all other values)

  A11b. complementary_methodologies — multi-select (zero or more)
      from:
      - "pinch analysis"
      - "exergy analysis"
      - "thermodynamic modelling"
      - "process flowsheet simulation"
      - "ML ensemble"
      - "multi-criteria decision-making (MCDM/AHP/TOPSIS/Fuzzy)"  (v2.2 NEW)
      - "none"

      These are methodologies used ALONGSIDE the primary EnPI/EnB
      modelling. If the paper's primary frame is e.g. pinch analysis,
      code it in A11 instead.

EVIDENCE REQUIREMENT (MANDATORY, v2.1 C3 + v2.2 normalization):

Every non-null value carries:
- evidence_quote: LITERAL SUBSTRING of extracted PDF text. Verifier
  applies v2.2 normalizations (soft-hyphen removal, whitespace
  collapse, ligature/dash/quote unification, lowercase) before
  matching. If supporting span is split across non-contiguous PDF
  regions, use a LIST of literal substrings + set
  non_contiguous_evidence=true.
- page: INTEGER INDEX INTO THE pdf.pages ARRAY (1-indexed).
  PDF physical page number, NOT printed journal page.
- non_contiguous_evidence: bool (default false).
- confidence: 0.0-1.0, soft annotation.

For multi-select fields: provide ONE evidence_quote per selected
value (or a single quote covering all selected values together).

If a field cannot be determined: value=null, evidence_quote="not
found in source", page=null, confidence=null.

For value="none" or empty multi-select: evidence_quote may be null
OR must literally state the absence. NEVER a descriptive quote
about the excluded methodology.

CONFIDENCE — soft annotation. Calibrated, not optimistic.

NEVER inject external knowledge (especially for A8 sector_of_activity).
NEVER fabricate quotes. NEVER cite content from images/figures.

OUTPUT — single JSON object:

{
  "multi_site": {"value": true|false, "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "country_region": {"value": "...", "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "sector_of_activity": {"value": "...", "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "type_of_organisation": {"value": "...", "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "ems_standard": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "mv_protocol": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "regulatory_driver": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "enpi_enb_model_types": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0},
  "complementary_methodologies": {"value": ["...", "..."], "evidence_quote": "...", "page": <int>, "confidence": 0.0-1.0}
}
