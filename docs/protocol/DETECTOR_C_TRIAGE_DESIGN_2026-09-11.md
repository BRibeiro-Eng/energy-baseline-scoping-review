# Detector (c) triage design — §3-Step-4 closure

**Date:** 2026-09-11 · **Status:** design fixed before any verdict was recorded
**Pass:** detector (c), counter-anchored recall, Claude surface, 394/394 responses
**Rebuild:** `python3 work/detector_claude/build_triage_c.py`

## 1. Why the raw detector output cannot be the human queue

Detector (c) is deliberately over-inclusive: its prompt instructs the model to
list *any* continuous-process signal even when confident the paper is not
Corpus B, because "a signal you suppress because the paper obviously isn't
refining is the exact failure this pass exists to prevent". It fired on **186
of 394** papers. That is the instrument working as designed, not a defect — but
it means the raw flag list is not a work queue.

`conservative_classification` is unusable as a discriminator: models returned
`true` on papers that are plainly out of scope (e.g. a cross-country Probit
study of firm turnover), having read the field as "I applied the conservative
framing" rather than as a membership call. This is consistent with the prompt's
own statement that the field "is recorded but **does not drive the detector**;
the signal lists do". It is ignored here.

## 2. The partition, and what authorises each cut

Every cut below comes from a criterion already registered in `PROTOCOL.md`
§5.3, not from effort management.

| Partition | Rule | N |
|---|---|---|
| **Out of Corpus A** | Corpus B ⊂ Corpus A. A paper that failed methodological eligibility cannot enter Corpus B; reopening it is a Tier-1 action, not a census action. | 50 |
| **Already in Corpus B** | no action | — |
| **Stratum I** | eligible · outside B · signal names a **§5.3 registered sector** · `application_strength ∈ {applied, validated, demonstrated}` | **2** |
| **Exploratory** | same, but the continuous-flow sector is **not** on the §5.3 list | **12** |
| **Stratum II** | eligible · outside B · signal present · `application_strength ∈ {mentioned_only, none}` | **122** |

**Stratum II is excluded by the registered criterion, not by convenience.**
§5.3: *"the paper must **apply, validate, or empirically demonstrate** the model
in one of these sectors. Implicit, theoretical-only, or 'could be applied to' is
**not** sufficient."* `mentioned_only` is, in the overwhelming majority of these
papers, a bibliography entry — a citation to somebody else's cement or pulp-and-
paper study. A citation is not an application. The sample in §4 bounds the rate
at which that reading is wrong.

## 3. Exploratory cases — the §5.3 mechanism, not a discretionary call

§5.3 already legislates the unlisted-sector case: *"Unlisted sector that appears
continuous-flow? Do NOT self-classify"*, and such a paper is reported as an
**exploratory case outside the main Corpus B** unless a **dated, documented
corpus decision** adds the sector to the main list **before** its papers are
counted in Corpus-B analyses.

The 12 exploratory papers sit in: combined-cycle thermal power · ceramics (tile,
brick, sanitary ware) · municipal sewage treatment · sugar · upstream oil & gas
(gathering centres, offshore platforms) · non-metallic minerals (gypsum
calcination) · continuous-production food.

They are enumerated in `EXPLORATORY_CASES.md` so that no signal is lost, and
none enters Corpus B without a dated decision. Expanding the list after seeing
which papers would enter is selection on the outcome, and the v2.3 circularity
fix exists precisely to stop membership being decided by the phenomenon under
study; the same logic applies to deciding it by the papers available.

## 4. Stratum II verified sample

Risk-sub-stratified, because a false negative can only matter where a
**registered** sector is named:

| Sub-stratum | Definition | N | n | seed | one-sided 95% upper bound if 0/n |
|---|---|---|---|---|---|
| **IIa** | signal names a §5.3 registered sector | 81 | 25 | 46 | **11.3 %** |
| **IIb** | only unlisted continuous-flow signals | 41 | 8 | 47 | 31.2 % |

IIb's bound is deliberately loose and that is not a weakness of the design: a
false negative in IIb cannot be a Corpus-B paper at all, because no registered
sector is named — at most it would be another exploratory case. IIb is a sanity
check on the partition itself, IIa is the instrument that bounds the Corpus-B
membership claim.

Per sampled paper the reviewer answers one question: **is the signal this
paper's own application, or a citation / passing mention?** Outcomes are
reported as `x/n` per sub-stratum, never pooled.

## 5. Closure and escalation

§3-Step-4's closure rule is a full pass yielding zero new candidates. This pass
produced candidates, so closure is not automatic:

- **Any confirmed false negative** (Stratum I read, or an IIa sample paper whose
  signal is its own application in a registered sector) triggers **§6a**:
  lexicon expansion plus a re-run of detector (b). ≥3 confirmed → supervisor
  discussion.
- **Zero confirmed** → the candidate union is exhausted on this surface, the
  roster locks at the current |B|, and the §3-Step-5 size branch is selected
  from the locked value.

## 6. Declared limitations

1. **Single surface.** Detector (c) ran on the Claude surface only; the ChatGPT
   partial coverage (30 responses) is recorded separately and is not merged into
   this union. §3-Step-4 specifies one machine pass, so this is per protocol,
   but the pass inherits one model family's blind spots.
2. **`models_returned` is mixed.** Responses carry `claude-haiku-4-5` alongside
   the pinned `claude-opus-4-8`; the surface is "Claude Code CLI", not a single
   pinned model.
3. **One paper needed repair.** `rayyan-472536601` failed the grounding check on
   three consecutive attempts (two-column extraction interleaves the columns, so
   verbatim quotes score 66–79) and was quarantined; it produced a valid
   response on a later attempt. No paper is missing a response.
4. **Quota interruptions are not validation failures.** 144 run interruptions
   from session-limit resets are recorded in `availability_interruptions.jsonl`,
   separate from the quarantine, so the quarantine count is not inflated by
   availability.
