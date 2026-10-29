# Detector (c) — counter-anchored recall pass

Validation Protocol C-2.3 §3-Step-4, detector (c). One paper per call.

You are scanning for **signals**, not making a classification. Read this carefully,
because the two halves pull in opposite directions and both are deliberate:

- **Classification framing is conservative.** Assume the paper is NOT Corpus B
  unless the text gives explicit evidence. Do not infer, extrapolate, or reason
  from what a sector "usually" does.
- **Signal listing is over-inclusive.** List *any* continuous-process signal you
  find, even when you are confident the paper is not Corpus B. The detector fires
  on the presence of a signal, never on your final classification. A signal you
  suppress because "the paper obviously isn't refining" is the exact failure this
  pass exists to prevent.

If those conflict, the signal list wins. Over-listing costs a human two minutes;
under-listing loses a paper from the corpus permanently.

## Corpus B (PROTOCOL.md §5.3) — the registered sector list

Petroleum refining · petrochemicals (organic chemistry, polymers, olefins) ·
cement, lime, clinker · pulp & paper · steel and other primary-metals continuous
production · continuous chemical production (sulfuric acid, ammonia, methanol,
fertilizers, chlor-alkali) · industrial gases (air separation, hydrogen,
nitrogen) · glass (continuous melting, float lines).

Membership is decided **solely by production mode**: continuous-flow, 24/7,
non-discrete, non-batch industrial production. Out of scope: discrete
manufacturing, batch chemical production, services and offices, residential and
commercial buildings, agriculture, mining unless processing is continuous.

The paper must **apply, validate, or empirically demonstrate** something in that
context. "Could be applied to" is not application.

## What to return

Return ONLY this JSON object. No prose before or after.

```json
{
  "key": "<paper key exactly as given>",
  "listed_sector_signals": [
    {"signal": "<what you found, in your words>",
     "quote": "<verbatim from the paper>",
     "page": <positive integer>,
     "sector": "<which of the eight listed sectors>"}
  ],
  "other_continuous_flow_signals": [
    {"signal": "<what you found>", "quote": "<verbatim>", "page": <int>,
     "sector": "<name it: LNG, aluminium, cogeneration, desalination, ceramics, ...>"}
  ],
  "application_strength": "applied | validated | demonstrated | mentioned_only | none",
  "conservative_classification": true,
  "one_line": "<one sentence: what the paper's application context actually is>"
}
```

Field notes:

- `listed_sector_signals` — only the eight registered sectors above.
- `other_continuous_flow_signals` — any continuous-flow context outside that list.
  Record these even though they are not currently Corpus B; the census is the place
  where the corpus boundary can be revisited with evidence, and an unrecorded signal
  cannot be revisited at all.
- Every signal needs a **verbatim quote and a positive physical page**. No quote,
  no signal — do not paraphrase and do not invent a page.
- `conservative_classification` — your Corpus-B call under the conservative framing.
  This field is recorded but **does not drive the detector**; the signal lists do.
- Both signal lists empty is a valid and common answer. Say so plainly rather than
  reaching for something.
- `one_line` is for the human triage queue. Describe the context, do not argue a verdict.

## Input

You will be given the paper key and its Stage-0 bundle path. Read the bundle's
`pdf.pages[].text`. Use the `page` values from the bundle as physical pages.
