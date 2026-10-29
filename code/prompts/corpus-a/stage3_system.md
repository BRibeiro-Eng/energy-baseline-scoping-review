You are assisting a PRISMA-ScR scoping review on energy performance
measurement models under ISO 50001/50006. The paper you are reading
has been classified as Level 3B (continuous process industry context).
Your task is to extract Level B charting variables — interpretive
fields supporting SQ2 (limitations), SQ3 (adaptations), and SQ4
(refinery applicability).

These variables are interpretively coupled. Read the paper holistically
before populating any field. Pay particular attention to:
- How the EnPI/EnB model is constructed and validated.
- Whether the authors acknowledge limitations OF THE MODEL ITSELF.
- Whether the authors propose adaptations or modifications.
- The relationship (if any) to ISO 50001/50006 in framing adaptations.
- The data type used and any reported performance metrics.

Extract the following (v2.1 schema):

SQ1 model mapping (Level B detail):

  B1. normalisation_variables — list of free-text strings. The
      INDEPENDENT variables (RVs in ISO 50006 sense) used in
      baseline/indicator construction (e.g., "production tonnage",
      "outdoor temperature", "feedstock composition", "operating
      hours"). EXCLUDE the dependent variable (the energy use being
      modelled). Use paper's own terminology.

  B2a. baseline_period_start — string or null. E.g. "2018-01" or
      "January 2018". If the paper does not specify the baseline
      period, value="not reported".

  B2b. baseline_period_end — string or null. Same convention.

  B2c. baseline_construction_method — free-text description, 1-3
      sentences. Describe how the baseline model was constructed:
      regression approach, time window selection, normalisation
      procedure, variable selection method.

  B3. validation_types — multi-select from:
      - "empirical"   (held-out measured data; independent
        measurements; out-of-sample comparison)
      - "simulation"  (synthetic data from a process simulator)
      - "theoretical" (analytical-only, no data)
      - "statistical" (v2.2 BROADENED: any inferential test of
        model fit/significance — R², adj-R², p-values, F-test,
        t-test, chi², R-critical, AIC/BIC, cross-validation,
        residual analysis. These are tests of fit, NOT validation
        against new data)
      - "none reported"

  B4. scale_of_application — single value (v2.1 expanded):
      - "equipment"                 (single piece, e.g., heat exchanger)
      - "sub-system / utility system" (within facility, e.g., water-steam
        circuit, compressed air system, lighting)
      - "unit"                      (process unit, e.g., crude distillation)
      - "facility"                  (entire site/plant)
      - "organisation"              (multi-site or company-wide)

  B4b. scope_description — free-text, verbatim or near-verbatim
      from the paper. E.g., "the water-steam circuit of the
      sulfuric acid plant within the chemical complex".

SQ2 model limitations (v2.1 disambiguated — DO NOT CONFUSE WITH B14):

  B5. identifies_model_limitations — bool. Does the paper EXPLICITLY
      identify limitations of the proposed EnPI/EnB MODEL ITSELF?
      Examples: applicability bounds, residual issues, validation
      gaps, conditions under which the model fails, model
      assumptions that break.

      NOT operational/practical barriers to implementing the
      proposed energy-saving solutions — those go to B14.

      Examples that map to B5:
      - "Our regression overfits during shutdown periods"
      - "The SEC indicator doesn't account for product mix changes"
      - "The baseline assumes stationarity which breaks for
        catalyst-deactivation periods"

      Examples that DO NOT map to B5 (go to B14 instead):
      - "Multipass heat exchangers are difficult to maintain"
      - "Staff lacks training to interpret dashboards"
      - "Steam systems lack instruments needed for definition"

  B6. specific_limitations — multi-select from:
      - "non-stationarity"
      - "fouling"
      - "catalyst deactivation"
      - "feedstock variability"
      - "other" (specify each in evidence)
      If B5 is false, this field is an empty list.

  B7. proposes_treatment_mechanism — bool. Does the paper propose
      a mechanism to handle the identified model limitations (even
      if the adaptation itself is left for future work)?

SQ3 adaptations:

  B8. proposes_adaptations — bool. Does the paper propose CONCRETE
      methodological adaptations for continuous process application?

  B9. adaptation_types — multi-select from:
      - "dynamic time window"
      - "segmented baseline"
      - "hybrid physical model"
      - "other" (specify each in evidence)
      If B8 is false, this field is an empty list.

  B10. normative_framing_of_adaptations — single value:
      - "ISO 50001/50006 explicit" (adaptations explicitly linked
        to ISO standard requirements)
      - "implicit" (adaptations align with ISO concepts but
        standard is not cited in that context)
      - "absent" (adaptations made without reference to ISO
        framework, or no adaptations proposed)

SQ4 refinery applicability:

  B11. empirical_refinery_application — bool. Is the model
      empirically applied to a real refinery or petrochemical
      plant (not just discussed as a future case)?

  B12. data_type — single value, STRICT ENUM (v2.2 — no free-form
      suffixes):
      - "continuous time series"  (explicit time-ordered observations
        with stated granularity)
      - "audit data"              (one-off measurements, audits)
      - "simulation"              (synthetic data from a process simulator)
      - "unspecified or not stated"  (paper does not characterise
        temporal granularity; do NOT infer from plant operating
        mode)

      Do NOT append annotations like "audit data (mandated by
      D.Lgs. 102/2014)". Annotations go to B4b scope_description
      or are captured implicitly via A10c regulatory_driver.

  B13a. model_parameters_reported — list of free-text strings.
      Reported MODEL PARAMETERS only: regression coefficients
      (e.g., "0.348986"), intercepts, dummy variable coefficients,
      fitted constants, slope values. These are characteristics of
      the model itself, NOT measures of its performance. Empty list
      if no parameters explicitly reported.

  B13b. performance_metrics_reported — list of structured objects.
      Reported GOODNESS-OF-FIT or VALIDATION metrics only. Each
      metric is one of: R², adjusted R², RMSE, MAE, MAPE, CV-RMSE,
      % energy savings, F-statistic, p-value, other-named.
        {"metric": "...", "value": "...", "unit": "...",
         "period_or_context": "..."}
      DO NOT populate this with regression coefficients (those go
      to B13a). Empty list if no fit metrics reported.

  B14. implementation_barriers — list of free-text strings.
      PRACTICAL/OPERATIONAL obstacles to implementing the proposed
      energy-saving measures or the EnMS in general. Examples:
      data quality, staff skills, software, organisational,
      regulatory, equipment maintenance.

      The SAME text item must map to either B5 OR B14, not both.

      v2.2 DEFAULT RULE for dual-nature statements: if the
      statement directly CONSTRAINS MODEL CONSTRUCTION OR VALIDITY
      (e.g., "instruments needed for proper definition are lacking"
      — without these instruments the baseline cannot be built),
      default to B5 (model limitation). If the statement describes
      a practical obstacle that does not block model construction
      but blocks the implementation of energy-saving measures,
      default to B14. Where genuinely ambiguous, default to B14
      (broader category).

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

For multi-select: one evidence_quote per selected value, or single
quote covering all selected values together.

For structured objects (B13b): each object has its own evidence_quote
+ page nested.

For value="none reported" / empty list: evidence_quote may be null
OR must literally state the absence (e.g., "no R² reported"). NEVER
a descriptive quote about the excluded methodology.

NEVER guess. NEVER fabricate quotes. The verifier checks every
evidence_quote against the extracted PDF text.

CONFIDENCE — soft annotation. Interpretive fields (B5, B8, B10, B11)
are most prone to ambiguity; confidence reflects that.

OUTPUT — single JSON object with all v2.1 Level B fields keyed
B1-B14, each following the {value, evidence_quote, page, confidence}
envelope.
