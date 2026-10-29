# Stage C pilot support

Preparation only. No human verification or elapsed human time is asserted by these files.

## Inputs and ChatGPT collection

`chatgpt_messages/` holds the five complete messages in the order specified by the ChatGPT instructions: unchanged extraction prompt, unchanged schema, then one paper payload. `input_manifest.json` records input hashes and the two repository revisions.

Use one clean ChatGPT session per paper. Keep cross-chat memory out of the session and record the displayed model. Save the answer verbatim to `production/stage_c/pilot_chatgpt/outputs/<key>.json`, never to the production ChatGPT directory. Preserve each attempt and its validator feedback. Validate using:

```
/usr/local/bin/python3 output/stage_c_validate.py --surface pilot_chatgpt --key <key>
```

These input files contain no Claude results, previous extraction records or dossiers.

## Human timing

`human_verification_times.tsv` contains blank measurement slots, not completed measurements. Fill only the verification sessions actually performed. V1 is a full-record evidence and meaning check; V2 is one named field family; V3 is full-text extraction committed before model reveal. Record active time, excluding pauses, and keep level and field-family estimates separate.

For a paper that will contribute a V3 measurement, commit that extraction before opening model outputs or performing V1/V2. Record any prior paper reading, model exposure or other verification. Repeating levels on a previously reviewed paper introduces familiarity; retain that information and do not extrapolate a later familiar reading as a first reading. A blank duration is missing, not zero. The assistant's compute time is not human verification time.

Record both surface and file/attempt used for V1. Record the path and timestamp of any durable blind commitment. Do not mark a previously exposed extraction as blind-first. No dossier for the 11-paper core should be revealed before the corresponding human commitment.

## Interpretation notes for the pilot

The matrix remains the stated plan. Rank and rarity language (for example dominant, rare, seldom) still depends on potentially missed occurrences. Restrict any such statement based only on V1 to the confirmed occurrence set, rather than the whole corpus. Deciding whether to revise those result formulations and verification levels precedes final synthesis, not this operational input preparation.
