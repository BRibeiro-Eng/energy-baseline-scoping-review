# Extraction workspace instructions

This folder is one model-family workspace in a two-family extraction design.
Act only as a thin orchestrator. Deterministic scripts select keys, validate
outputs, and mutate state; never reconstruct or edit aggregate state yourself.

## Non-negotiable boundaries

- Read `START_HERE.md`, `ORCHESTRATOR_PROTOCOL.md`, and
  `ARTICLE_AGENT_PROTOCOL.md` completely before proposing work.
- Work only inside this workspace and through its verified `inputs/` links.
  Never read the sibling model workspace or `reviewer_workspace/`.
- Never invoke a model through a local runner or API. After human approval,
  dispatch one article subagent per assigned paper through this application's
  native agent mechanism.
- Each article agent handles exactly one paper end-to-end and may write only
  its assigned raw-attempt and optional report paths. It must not spawn agents.
- Default batch size is 5. Do not start any batch without explicit human
  approval recorded by the deterministic controller.
- When a batch ends, validate/finalize it, report the result, and stop. Do not
  propose or start the next batch in the same authorization cycle.
- Inter-model agreement is routing only, never evidence of correctness.
- Preserve every raw attempt. Never overwrite, silently repair, or promote a
  malformed attempt by copying files.
- `run_metadata.json` is fail-closed. If any required provenance or OSF gate is
  null, production extraction is blocked; deterministic fixture tests remain
  allowed.

If an instruction conflicts with `VALIDATION_PROTOCOL_C.md`, stop and report
the conflict. Do not improvise a methodological change.
