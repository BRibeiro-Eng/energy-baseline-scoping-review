# Detector (c) — how to run the recall pass

Validation Protocol C-2.3 §3-Step-4. **394 papers**, the concordant-excluded frame
(both models classified `level_3b=false`). One JSON per paper.

This frame is disjoint from the 82 papers in the blind Tier-1 queue, so running it
raises no blinding question — nothing here touches a decision you have not yet made.

## Session prompt

Open a clean session with `cwd = /Users/bernardoribeiro/LocalResearch/Screening/level3_extraction`
and paste:

```
Act as the detector-(c) recall pass for Validation Protocol C-2.3 §3-Step-4.

Read output/fn_census/detector_c/PROMPT.md completely and follow it exactly.
The queue is output/fn_census/detector_c/QUEUE.json (394 keys). Paper text is in
output/stage0/<key>.json under pdf.pages[].text; use those page numbers as
physical pages.

Work in batches of 20 keys in queue order. For each paper write exactly one file
output/fn_census/detector_c/responses/<key>.json matching
output/fn_census/detector_c/response.schema.json. Do not write anything else and
do not modify any other file.

Report per batch: keys done, how many fired a listed-sector signal, how many fired
only an other-continuous-flow signal. Then stop and wait for me before the next
batch.

Two reminders that decide whether this pass is worth running at all:
- list every continuous-process signal you find even when you are sure the paper
  is not Corpus B — the detector fires on signals, never on your classification;
- every signal needs a verbatim quote and a real page, checked by the collector
  against the paper's own text. Unverifiable quotes are dropped and logged.
```

## Running it on both surfaces

§3-Step-4 specifies "one extra machine pass". Running it on Claude **and** ChatGPT
is a strict enlargement of the union — more recall, in the direction the census is
deliberately biased. It is not a protocol violation, but be explicit about two
things: record in `run_metadata.json` that detector (c) ran on two surfaces rather
than one, and expect the Tier-hit-A triage load to grow, since every extra firing
is a paper you must read.

If you run both, collect into separate files and union them:

```bash
python3 output/fn_census/detector_c/collect.py \
  --responses output/fn_census/detector_c/responses_claude \
  --out output/fn_census/recall_flags_claude.json
```

## Collect and rebuild the census

```bash
python3 output/fn_census/detector_c/collect.py
```

Validates every response against the schema, verifies each quote against the
paper's own Stage-0 text under §6.3 normalisation, and writes
`output/fn_census/recall_flags.json`. A response with no verifiable signal does
not fire the detector; a paper missing a response leaves the census **incomplete**,
and the closure rule cannot be satisfied while it is.

Then rebuild the union:

```bash
python3 output/fn_census_build.py --recall-flags output/fn_census/recall_flags.json
```

## Closure loop (§3-Step-4)

Every confirmed false negative adds that paper's sector vocabulary to the lexicon,
detector (b) re-runs, and the new candidates enter the census. The census closes
only when a full pass yields **zero** new candidates.

```bash
python3 output/fn_census_build.py \
  --recall-flags output/fn_census/recall_flags.json \
  --extra-terms output/fn_census/lexicon_expansions.json
```

Escalation thresholds are already registered (§6a): any confirmed FN triggers the
lexicon expansion and a re-run; **≥3 confirmed FNs total** triggers a supervisor
discussion of a corpus-wide sector re-screen before the roster is locked.

## Current state without detector (c)

| detector | candidates |
|---|--:|
| (a) model flags | 18 |
| (b) lexicon | 169 |
| (c) recall pass | **not run** |
| **union** | **177** — Tier-hit-A 125 · Tier-hit-B 52 |

The union is incomplete until (c) runs. Tier-hit-A is a full read (~10–12 min),
Tier-hit-B a 2-minute skim with a one-line logged justification; any doubt promotes
B to A, and nothing is dropped from either tier.
