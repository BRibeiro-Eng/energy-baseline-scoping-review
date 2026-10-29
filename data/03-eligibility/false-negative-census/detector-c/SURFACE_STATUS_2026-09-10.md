> Translated from Portuguese for this release. Original: `SURFACE_STATUS_2026-09-10.pt.md` (same folder), SHA-256 `259a720314ef7788285a819ac9b90007dec1c06292c75d0ebc7e94f34a128dbf`. The original is the record; this translation is for reading.

# Detector (c) — status of the surfaces, 2026-09-10

**Surface of record: Claude.** Launched 2026-09-10 ~12:35 with `work/detector_claude/run.py --workers 2`, full queue of 394, writes to `responses_claude/`.

## ChatGPT/Codex attempt — stopped by quota, status to be decided

`responses_chatgpt/` has **30 valid responses out of 394** (5 from 2026-09-09 + 25 from 2026-09-10). Both runs stopped with `You've hit your usage limit` on the ChatGPT Plus account: the 09-09 run at 5 papers with 3 workers, the 09-10 run at ~25 with 1 worker, with a reset announced for 16:51.

Measured: **the account yields ~25–30 papers per window of ~5 h** with this call profile (full Stage-0 text per paper, `gpt-6-astra`, reasoning `xhigh`). 394 papers would need ~14 windows — about three days of supervised execution. That is why the surface was changed, not methodological preference.

**These 30 responses are not in the union and do not enter it without an explicit decision by the reviewer.** `collect.py` runs per directory: nothing here is aggregated by accident.

Two possible outcomes, both defensible, at the reviewer's choice:

1. **Discard** — the union keeps a single machine pass, which is what §3-Step-4 specifies. The 30 stay as a record of the attempt. Simple to declare.
2. **Merge** — `collect.py --responses responses_chatgpt --out recall_flags.json` in addition to Claude. Strictly more recall, but asymmetric coverage (30/394 on one side, 394/394 on the other), which must be said that way in the report: it is not a second pass, it is a partial pass over 7.6 % of the frame. Each extra hit is one more full reading added to the triage queue.

Recommendation recorded in this note: option 1, because of the asymmetry and the triage cost. The decision is the reviewer's.

## Provenance note

The Claude-side runner records `models_returned` per call. The first responses carry `["claude-haiku-4-5-20251001", "claude-opus-4-8[1m]"]` — the CLI uses haiku for auxiliary tasks besides the pinned model. The field is recorded per response; the census report must say so instead of declaring a single model.

The Codex side ran `gpt-6-astra` / reasoning `xhigh` / codex-cli 0.153.4 — a different model from the extraction twin (`gpt-5.6-sol`), which is acceptable for an independent detector but must be stated if option 2 is chosen.

## Change to the runner's quotation checker — 2026-09-10 12:30

**Authorised by the reviewer on this date.** The run blocked at 11:51 with 69 valid responses, on `rayyan-472535487`, with four `quote is not verbatim` errors.

Diagnosis: the four quotations are real and are on the stated page. The paper is a manuscript in submission format, with printed line numbers that the extractor picked up interleaved with the running text — p. 38 reads `most large steelmakers in china 1490 have deployed similar information technologies (…) over the 1491 past decade`. The model transcribed the sentence without the line numbers. There was no fabrication: the defect was in the checker.

The runner used its own check (`norm()` + exact substring) instead of `grounding.py`, which is the checker registered in the protocol (§6.3, 8 rules v2.2.1, fuzzy alignment with a length-dependent threshold). The canonical checker validates the four quotations with scores 92.7 · 96.3 · 93.2 and `page_unverified: false`.

**Change applied:** `work/detector_claude/run.py` now validates with `ground_quote()`. Backup of the original in `run.py.bak_20260910T1230`.

- It fails (and rejects the response) when `grounded` is false.
- When the quotation is grounded but the page is not confirmed, it records the warning in `_grounding_warnings` in the response itself and does **not** block — blocking on a page number when the quotation is real reintroduces the defect this fixes.
- A check for a page that does not exist in the bundle remains an error.

**This does not relax the criterion:** it replaces an ad hoc checker with the stricter checker already registered in the pipeline. The 69 earlier responses passed the strict test and remain valid — the canonical checker is strictly more permissive, so nothing that passed stops passing. There is no need to reprocess what is already done.

**Extent of the problem:** 18 of the 459 papers in the corpus have line numbering in the extracted text. Without this correction the run would block once for each of them that appeared in the queue.

Run relaunched at 12:32; `rayyan-472535487` validated (3 signals of a listed sector, 1 other, 1 page warning recorded).
