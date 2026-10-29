# Clean-session start prompt

Act as the extraction orchestrator for this workspace only.

Read `AGENTS.md` (or `CLAUDE.md`), `START_HERE.md`,
`ORCHESTRATOR_PROTOCOL.md`, and `ARTICLE_AGENT_PROTOCOL.md` completely. Treat
the filesystem and deterministic controllers as authoritative; do not infer
state from this chat and do not inspect sibling workspaces.

Then:

1. verify this pack;
2. initialize `run_metadata.json` through `scripts/run_initializer.py` if its
   run/surface provenance is still null;
3. inspect controller state and recover an interrupted batch if one exists;
4. otherwise propose the next batch using the default size 5;
5. show me the proposal ID and ordered paper keys;
6. stop and wait for my explicit approval before activating the batch or
   dispatching article agents.

After approval, dispatch exactly one native subagent per paper, finalize the
batch through the controller, report completed/repair/failed counts, and stop.
Never auto-propose the following batch.

If this pack is the explicit development re-pilot subset, use the controller's
`--repilot` flag after approval. Never use `--fixture` in this live session.
