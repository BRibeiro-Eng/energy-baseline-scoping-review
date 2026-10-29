> Translated from Portuguese for this release. Original: `TIER1_CLOSURE_2026-09-09.pt.md` (same folder), SHA-256 `5206264f81516aa6c204fab15982cab21d5551683914b3d48f7981cf185fbcb6`. The original is the record; this translation is for reading.

# Closure of the Tier-1 census — 2026-09-09

Reviewer's decision (B. Ribeiro, 2026-09-09): **confirm the blind decisions as final, without adopting any revealed value**, and revert the edits produced by an AI session. Mandatory record: `production/` is not versioned in git; this file and `revert_confirm_20260909T173542.json` are the only trace.

## What was reverted

Between 17:52 and 17:56 on 2026-09-09, a Codex/ChatGPT session opened five papers in the form and saved to them. Four were saved without a change of value. One was changed:

| paper | field | blind | changed to | status now |
|---|---|---|---|---|
| `rayyan-472536742` | `eligibility.level_3b` | `false` | `true` | **reverted to `false`** |

The justification written by the AI session declared itself "pending human adjudication" and relied on the quotation on p. 6 (testimony from the California Portland Cement Company). The reviewer's blind decision had already examined and rejected that same passage, classifying it as partner testimony attributed to personal communication (note 13), with no variables, functional form, data or cement result anywhere, and identifying the two sectors actually demonstrated as automotive assembly (discrete) and wet corn milling (continuous, unlisted) — which triggers the CRITICAL clause of §5.3. The reversion restores the value and the evidence from the immutable blind snapshot `rayyan-472536742.blind.json`.

The log `rayyan-472536742.reveal_changes.jsonl` was voided to `rayyan-472536742.reveal_changes.jsonl.voided_20260909T173542` (content preserved, outside the calculation). Reason: the anchoring-exposure figure of §3-Step-3 measures changes by the human reviewer after seeing the twin. Three lines written by an AI session are not observations of that instrument; counting them would overstate the reviewer's anchoring with an event that is not his. The event is reported here as an incident, not as data.

## Final state

82/82 papers, 90/90 cells, all `finalised` with the blind value. No cell adopted the twin's value. Checked programmatically: zero divergences between each `{key}.json` and its `{key}.blind.json`.

## How this must be reported (do not use the output of progress.py as it comes out)

`progress.py` prints "0 reveal-changes over 82 revealed papers". The denominator is wrong for reporting purposes: it counts `revealed + finalised`. The actual exposure breaks down as follows:

| class | n | what can be stated |
|---|--:|---|
| Finalised without any exposure to model output | 73 | blind decision taken as final; there was never a reveal |
| Revealed on 2026-09-01, worked on by the reviewer, finalised today in a block | 3 | `rayyan-472535377`, `-472535386`, `-472535481`; real exposure, individual adjudication not completed |
| Revealed by an AI session on 2026-09-09, finalised at the blind value | 5 | `rayyan-472535511`, `-472535541`, `-472536054`, `-472536742`, `-472535739`; blindness used up without human adjudication |
| Revealed and fully adjudicated by the reviewer | 1 | `rayyan-472535360` (2026-09-01) |

**Wording for the report and for the declared limitation:** the reveal planned in §3-Step-5 was executed in full for 1 paper and partly for 3; for 5 the exposure to the twin occurred through an automated session and is not human adjudication; for the remaining 73 the reveal was not executed and the blind decision was taken as final by the reviewer's decision, taken under time constraints. The anchoring-exposure figure of §3-Step-3 is therefore **1/1 adjudicated papers with 0 changes** — not 0/82. Any number above 1 in the denominator overstates how much independent reading took place.

What this **does not** compromise: no membership decision was taken with the twin in view, and the direction of the residual error is known — the decisions are the reviewer's, blind, uncontaminated. What it **costs**: the second independent reading of 81 of the 82 papers is lost, and with it the ability to estimate how much that second reading would have changed.
