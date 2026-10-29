# Article-agent protocol

You are responsible for exactly one assigned paper. Do not inspect any other
paper, model workspace, reviewer data, aggregate state, or prior batch output.
Do not spawn agents.

1. Read the assigned Stage-0 bundle and its page-preserving text.
2. Apply `prompts/stage1_system.md` and record Stage 1.
3. If `methodological_eligibility.value` is true, apply Stage 2; otherwise set
   `stage2` and `stage3` to null.
4. If the paper is eligible and `level_3b.value` is true, apply Stage 3;
   otherwise set `stage3` to null.
5. Write one JSON object conforming to `schemas/article_output.schema.json`.

Every extracted field uses the full evidence envelope:
`value`, `evidence_quote`, `page`, `non_contiguous_evidence`, `confidence`.
Quotes must be literal source substrings and pages are physical 1-based indices
into the Stage-0 `pdf.pages` array. Never guess or cite raster-only content.

The combined initial-output shape is:

```json
{
  "record_type": "initial_extraction",
  "paper_key": "rayyan-000000000",
  "schema_version": "2.2.1",
  "validation_protocol": "C-2.3",
  "prompt_tag": "v2.3.1-operational",
  "attempt": 1,
  "completed_at": "ISO-8601 timestamp",
  "stage1": {},
  "stage2": null,
  "stage3": null
}
```

Return no prose around the JSON. An invalid first attempt may receive one
targeted repair request limited to the deterministic validation errors.
