# Start here

1. Read `AGENTS.md` (or `CLAUDE.md`), `ORCHESTRATOR_PROTOCOL.md`, and
   `ARTICLE_AGENT_PROTOCOL.md` completely.
2. Run `python3 scripts/pack_verifier.py --workspace .`.
3. If `run_metadata.json` is not initialized, run
   `python3 scripts/run_initializer.py --help` and record the run ID, executor,
   displayed application version, and displayed model label atomically.
4. Run `python3 scripts/batch_controller.py --workspace . status`.
5. If an interrupted batch exists, run `recover` and report it before doing
   anything else.
6. Otherwise run `propose` (default size 5), display the exact proposal, and
   stop for explicit approval.

If `PACK_LOCK.json` says `queue_scope=development_subset`, this is the real
seven-paper interactive re-pilot. After explicit approval, use `--repilot` on
`approve` and `finalize`. Never use `--fixture` in a real application session.
For a full production pack, use neither flag; the OSF/sign-off gate must pass.

Do not infer state from chat history. A paper is complete only when its raw
attempt is preserved, its validated output exists, and the controller records
the same terminal state.
