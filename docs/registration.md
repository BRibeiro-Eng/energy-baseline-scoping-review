# Registration and amendments

The protocol and its amendments are held on the Open Science Framework (OSF) and are not moved here: a registration cannot be changed, and the copies in `docs/amendments/` are byte-identical to what was filed (check them against the SHA-256 below).

- Registration: **TDW6C**, DOI [10.17605/OSF.IO/TDW6C](https://doi.org/10.17605/OSF.IO/TDW6C), registered 24 February 2026, after the database searches and before title/abstract screening.
- OSF project: [osf.io/wh62r](https://osf.io/wh62r).

| Date | Document | OSF file | SHA-256 | Copy here |
|---|---|---|---|---|
| 24 Feb 2026 | Registered protocol: *Energy Performance Measurement Models in Continuous Process Industries under ISO 50001/50006: A Scoping Review Protocol* | `pjvu8` | — | not copied (see OSF) |
| Apr 2026 | Amendment 1: clarification of the two-corpus structure (Corpus A, Corpus B) | **[to be confirmed]** | — | — |
| 23 Jul 2026 | Amendment 2: Validation Protocol C-2.3 for model-assisted extraction | `u3wkb` | `15c140cdcc18f1f9d9c1dd7520d9ad96741cccafd654ad8b39fac64412ec2650` | `docs/amendments/OSF_Amendment_TDW6C_C-2.3_submission.pdf` |
| 13 Sep 2026 | Amendment 3: Stage C extraction instrument for Corpus B (schema v2.3.0-C) | `s8eh5` | `094fd01a8fe3c5c223a8072fa8acaaa216fb9e9a6779c7492288561c59b9e701` | `docs/amendments/OSF_AMENDMENT_STAGE_C_DRAFT.md` |
| 16 Oct 2026 | Amendment 4: late execution of registered checks and replacement human verification of Corpus B | `2zgx8` | `5a1b9428f2cf5c6674e0263aa3153ab848d7ceb9be1106dec996eb6d56f722a1` | `docs/amendments/OSF_Amendment_TDW6C_A3_late-validation_2026-10-14.pdf` |
| 16 Oct 2026 | Term list of Amendment 4 (census of absences, layer A) | `yn2mh` | `9f5c4f830a7acc173fe7adc20f4f49f59dc599495f9c9180ebdb68368f1df777` | `docs/amendments/lexico_camada_A.json` |

The file name and internal label of the amendment of 16 October 2026 ("A3", "Emenda 3") number it third among the amendments filed as documents; counting the April clarification, the article calls it the fourth.

## Filing records (interlocks)

Two stages refused to run until a filing record existed:

- `docs/amendments/stage-c-filing-record/AMENDMENT_FILED.txt`: filing of Amendment 3 (Stage C). `code/pipeline/stage_c_run.py` checked this file before any Corpus B extraction.
- `docs/amendments/late-verification-filing-record/AMENDMENT_FILED.txt`: filing of Amendment 4. `code/late-verification/build_tasks.py` drew no sample until the `osf_file` and `sha256` in this file matched a local copy of the deposited PDF. The task manifest (`data/06-late-verification/tasks/MANIFEST.json`) repeats the hash, the seed (44) and the generation time.

The Stage C record is in English; the Amendment 4 record has Portuguese comments. Both are kept as written.

## Other registered parameters used by the code

- Corpus B schema v2.3.0-C, frozen 13 September 2026: SHA-256 `d855254b73a8640b4e13255876a3021ae9da699e1bf04bb4db3d5b2444e883ff` (`code/prompts/corpus-b/schema.json`, `SCHEMA_SHA256.txt`).
- Corpus A prompts: the prompts repository carries the tags `v2.1-schema-rework`, `v2.2-refined`, `v2.2.1-frozen`, `v2.3-eligibility-registered` and `v2.3.1-operational`; the released files are those at `v2.3.1-operational` (commit in `provenance/source-commits.md`), and each extraction record states the `prompt_tag` it was produced with.
