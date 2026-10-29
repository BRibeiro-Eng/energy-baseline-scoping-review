# Orchestrator protocol

## Startup and proposal

The filesystem is authoritative. Verify the pack and inspect controller state
before proposing work. `propose` may create only a proposal; it is not an
authorization. Show the proposal identifier, ordered keys, size, and gate
status to the user. Wait for explicit approval.

## Approved batch

After approval, record it with `batch_controller.py approve`. Dispatch one
article agent per assigned key. Give each agent only:

- the paper key;
- `inputs/stage0/{key}.json` and `inputs/pdfs/{key}.pdf`;
- the immutable prompt/protocol/schema files;
- `outputs/raw/{key}.attempt-01.json` and
  `outputs/agent_reports/{key}.attempt-01.md` as its only writable paths.

Wait for every agent to terminate. Run `finalize`; the controller validates
each raw output and promotes only valid attempts. It permits one explicit
repair attempt at `attempt-02`; a second invalid result is quarantined.

Report completed, repaired, failed, and remaining counts. Stop. A new batch
requires a new proposal and a new user authorization.

For the explicit seven-paper development subset only, pass `--repilot` to
both `approve` and `finalize`. This bypass does not work on a full queue and
still requires complete surface provenance. `--fixture` is reserved for
stored automated tests and is forbidden in real ChatGPT/Claude sessions.

## Stage-3 supplements

Supplements are a separate controller mode created only from a versioned human
Corpus-B roster receipt. They run Stage 3 only and never revise the frozen
initial Stage-1/2 output. If `|B| > 60`, all Level-B work is blocked until the
required amendment/supervisor decision is recorded. A failed supplement after
one repair routes to blind-first review with the missing model comparison
reported.
