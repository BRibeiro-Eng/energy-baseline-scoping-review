> Translated from Portuguese for this release. Original: `README.pt.md` (same folder), SHA-256 `6ad11c8d1a364dfcabd57a9842031d201a51bbf0f06edc042e2f5c14dbfac13e`. The original is the record; this translation is for reading.

# Triage of the false-negative census — C-2.3 §3-Step-4

177 candidates: **125 Tier-hit-A** (full reading, ~10–12 min) and **52 Tier-hit-B** (2-minute skim). They are papers that **both models classified `level_3b=false`** and that a detector flagged. Your job is to empty the list: each candidate leaves with a verdict and a justification. Nothing is discarded without a decision.

The union does **not** yet include detector (c) — when that pass closes, new candidates come in. Do not wait for it: these 177 have to be triaged anyway, and afterwards you deal only with the delta.

*Note added for the release: this was the original instruction. It was superseded the same day by the sampling amendment and then by the risk-stratified design (`docs/protocol/AMENDMENT_FN_CENSUS_SAMPLING_2026-09-10.md`); the closure is in `docs/corpus-decisions/CORPUS_CLOSURE_2026-09-12.md`.*

## The question

A single one, from §5.3: **does this paper apply, validate or empirically demonstrate something in a continuous-production sector of the registered list?**

Refining · petrochemicals (organic chemicals, polymers, olefins) · cement, lime, clinker · pulp and paper · steel and other primary metals in continuous production · continuous chemicals (sulphuric acid, ammonia, methanol, fertilisers, chlor-alkali) · industrial gases (air separation, hydrogen, nitrogen) · glass (continuous melting, float).

Membership is decided **only by the mode of production**: continuous flow, 24/7, not discrete, not batch. Out: discrete manufacturing, batch chemicals, services, buildings, agriculture, mining except continuous processing.

**"Can be applied to" is not an application.** A background mention, a list of energy-intensive sectors in the introduction, or a citation of another study are not an application — which is exactly why most of these 177 will leave as `not_fn`.

Continuous sector but **outside** the list: `--sector continuous-unlisted`, and the justification names the sector. It is not Corpus B, but it is recorded as an exploratory case.

## Flow

```bash
python3 verdict.py --next B          # next skim; --next A for full reading
cat contexts/rayyan-XXXXXXXXX.md     # excerpts already extracted, with page
```

The excerpts in `contexts/` show you **where** each term appears, with the page. For a Tier-B this is usually enough: if the term only appears in a list of sectors in the introduction, you decide without opening the PDF. If the excerpt is ambiguous, open the paper.

```bash
# the exclusion is correct — the signal was noise
python3 verdict.py rayyan-XXXXXXXXX not_fn "«steel» only in the list of energy-intensive sectors in the introduction; the case is a components factory"

# it is a false negative — the paper is Corpus B and was missed
python3 verdict.py rayyan-XXXXXXXXX confirmed_fn --sector cement/lime/clinker \
    --page 4 --quote "the plant operates two rotary kilns" \
    "measured application in a cement plant, with consumption data per line"

# Tier-B in doubt — do not decide, promote
python3 verdict.py rayyan-XXXXXXXXX --promote "the case may be a refinery, the excerpt is not enough"
```

(The justifications in the examples above were written in Portuguese in the original and are translated here.)

The quotation of a `confirmed_fn` is checked against the paper's own Stage-0 text before saving. If it does not match, nothing is written — you correct the page or the transcription.

`python3 progress.py` gives the status and tells you what each result triggers.

## What the results require (§6a, already registered)

Any confirmed FN requires expanding the lexicon with that paper's sector vocabulary, re-running detector (b) and triaging the new candidates. **The closure rule is zero new candidates in a complete pass** — not "I finished the list". Three or more confirmed FNs require discussing a sector re-screen of the corpus with the supervisor before locking the roster.

## Queue order

Sorted by signal specificity, descending: unambiguous terms (`refinery`, `clinker`, `blast furnace`, `ammonia`, `paper mill`…) weigh more than ambiguous ones (`steel`, `cement`, `petroleum`, which appear in any introduction), and a model flag (⚑) adds. If you stop half way, you stopped at the least bad place.

`FILA_A.md` and `FILA_B.md` are the readable lists; `QUEUE_A.json` / `QUEUE_B.json` what the tools read.

## What this is not

It is not adjudication of Corpus B membership by any model. The detectors produce **signal**; the verdict is yours, and it is the only one that counts.

*`contexts/` is not released (it reproduces excerpts of the full texts); see `provenance/EXCLUDED.md`.*
