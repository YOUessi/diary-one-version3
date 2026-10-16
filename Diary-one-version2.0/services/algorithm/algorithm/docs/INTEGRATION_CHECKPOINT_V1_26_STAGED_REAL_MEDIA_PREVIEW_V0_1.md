# Integration Checkpoint V1.26 — Staged Real-Media Preview V0.1

Status: IMPLEMENTATION BASELINE ACCEPTED; QUALITY NOT FROZEN; NOT PRODUCTION

Date: 2026-08-31

## 1. Why this checkpoint exists

The first real-media Web run exposed a structural mismatch rather than an isolated threshold bug. The running X01 research bridge asks one multimodal model call to perform perception, temporal grouping, Chapter/Aha candidate generation, editorial selection, writing, and tagging. That call cannot faithfully execute the frozen S00–S13 ownership and validation boundaries.

This checkpoint authorizes a new, versioned staged preview path for real imported media. X01 remains readable and runnable as historical research evidence, but it will not receive more product-quality patches and will not be the default Web test path.

## 2. Verified baseline

- Algorithm repository baseline commit: `e3c4e9c` on `codex/validation-v01-v02-20260829`.
- `docs/CANONICAL_CHECKPOINT_V1_25_PRODUCTION_SHAPED_PIPELINE_V1_0.md`: `577cb5bbb073fa9277b181bfe721b22176bdccd71585b4ff4a3fc28296346b0f`.
- `contracts/production_pipeline_v1.schema.json`: `e5dfd2651c84b67dd58da823cb753a02ff48967bb326909d65bebb71fe18a9ab`.
- `contracts/production_pipeline_v1.outputs.schema.json`: `e4a60bd463aa9c8aebe395c0be35f84daa11fc306948e1fa9904c9e61df1ee37`.
- `src/diary_one_ci/production_v1.py`: `60cca42c05c498cff6e8b97f17d8af7a4e48b4b3ffb7e2eadaf802e75d6fb2c7`.
- Web baseline commit: `d77f96a`; local-only, with no configured Git remote.
- Both repositories were clean at checkpoint creation.

The V1.25 files above are inputs to this implementation and are not modified by this checkpoint.

## 3. User-observed failure evidence

Recorded real run:

- Session: `a27c7b9b-9a91-4c16-92cc-c6c3c16f853d`
- Run: `dfd520c3-0ef3-44b2-a4ae-4fb07fed1c4d`
- Input: 20 videos / 60 extracted evidence frames
- X01 model exposure: 48 frames
- X01 output: 20 Observations, 14 Moments, 3 Chapter candidates, 1 Aha candidate, 1 final Chapter, 0 final Aha

Material failures:

1. A coherent ancient-town candidate with six source assets was rejected because X01 applied the final three-to-five-media rule during candidate generation. The frozen rule belongs to S10 final media selection, not S07 candidate membership.
2. A market Chapter included an unrelated forest stone-stair asset because no per-member semantic-coherence gate ran before selection.
3. The correct forest candidate then lost through raw-asset overlap created by the incorrect market candidate.
4. Evidence selection favored earlier assets; the first fourteen assets received three frames while the last six received one.
5. The only Aha candidate was not a strong independent event peak, and its over-length copy was dropped instead of being returned to the Writer owner for one bounded retry.
6. Some narrative claims and canonical tags were not supported by the presented frames.

Granular human feedback remains in the local run audit and is DRAFT evaluation evidence, not a frozen quality conclusion.

## 4. New path and naming

- Experiment: `X02_STAGED_REAL_MEDIA_PREVIEW`
- Pipeline version: `X02_STAGED_REAL_MEDIA_PREVIEW_V01`
- Result schema: `DIARY_ONE_X02_STAGED_PREVIEW_V01`
- Local endpoint: `/x02/v0.1/preview`
- Local run-sidecar endpoint: `/x02/v0.1/run-sidecar`
- X01 endpoint and audits remain available for historical comparison.

The word “preview” is mandatory in the UI and API. The implementation must not claim full Production readiness, device readiness, or S13 export completion.

## 5. Stage ownership for V0.1

The V0.1 staged preview preserves the frozen ownership model while using the minimum practical implementation needed for real-media testing.

| Phase | Frozen stages represented | Owner | V0.1 responsibility |
| --- | --- | --- | --- |
| Intake | S00–S02 | deterministic code | Validate the one-day bundle, preserve asset order, expose all contracted evidence frames, and create the immutable evidence ledger. |
| Perception | S04 | vision model in bounded batches + deterministic validator | Produce one Observation result per asset, support every fact with presented frame IDs, and isolate failed/insufficient assets instead of failing the full day. |
| Structure | S03, S05–S07 | text model over validated Observations + deterministic validator | Produce adjacent dual-evidence edges, complete contiguous Moments, exactly one role per Observation, auditable Chapter candidates, and event-peak-only Aha candidates. |
| Editorial set | S08–S09 | deterministic code in V0.1 | Apply coherence, support, coverage, distinctness, overlap, count, and Aha-independence gates. Do not use raw Top-K confidence sorting. |
| Media edit | S10 | deterministic code in V0.1 | Select the final three-to-five Chapter media from a potentially larger candidate, with quality, diversity, and timeline-spread evidence; select exactly one hero. |
| Narrative | S11 | text Writer over approved claims only + deterministic validator | Write short grounded Chinese preview copy and reference approved claim IDs; perform at most one bounded retry for repairable copy failure. |
| Final validation | S12 | deterministic code | Validate result shape, references, copy limits, claim support, canonical tags, and owner-specific failure states. No silent cross-stage repair. |
| Materialization | S13 | not executed | Report explicitly that HQ materialization/export remains outside this Web preview. |

## 6. Non-negotiable contracts

1. Every imported asset receives exactly one terminal Observation status: `OBSERVED`, `PARTIAL`, `INSUFFICIENT_EVIDENCE`, or `FAILED`.
2. Every accepted Observation receives exactly one S06 role: `KEEP`, `CONTEXT_ONLY`, or `DROP`, with a reason code.
3. Every accepted Observation is accounted for by one Moment or an explicit structural rejection record.
4. Chapter candidate membership is not capped at five. The three-to-five rule is evaluated only during S10 final media selection.
5. Every selected candidate member must support the candidate’s semantic basis. A location-level label such as “ancient-town walk” may bridge different visual motifs such as stone roads and historic buildings, but it cannot absorb an unrelated forest scene merely because the images share stone textures.
6. All assets are presented to perception with equal per-asset evidence policy. No input-order frame starvation is allowed.
7. Aha selection requires an independently meaningful local event peak and narrative independence from any overlapping Chapter. Zero Aha is valid when evidence does not support one.
8. The Writer cannot invent user state, evaluation, causality, venue, activity, or object identity. Every factual phrase maps to approved claim IDs and evidence frames.
9. Canonical tags are selected only from evidence-supported concepts; free-form model tags cannot enter the memory index.
10. One failed asset, candidate, or Writer item cannot silently delete unrelated valid content for the day.
11. Stage timing, model calls, input/output tokens, estimated cost, status, and failure owner are recorded separately.

## 7. Web integration contract

The existing local Web test surface will switch its default run action to X02 and will retain the current non-technical visual style. It must show:

- which stage is running;
- what each stage received, decided, rejected, and why;
- per-stage time, token, model-call, and estimated-cost metrics;
- candidate-level and media-level lineage for every final Chapter/Aha;
- a clear `STAGED PREVIEW / NOT PRODUCTION` label;
- structured evaluation targeting a Chapter, Aha, asset, copy field, tag, or pipeline stage.

The Web may continue to accept a manually assembled set of phone photos/videos as one synthetic day. GPS and trustworthy capture timestamps remain optional for this test mode; missing metadata must be visible and must not be fabricated.

## 8. Explicit exclusions

- No Firmware or SDK changes.
- No shared project-status file changes.
- No public or internal Internet deployment in this checkpoint.
- No domain, account whitelist, cloud storage, or cloud database mutation.
- No claim that phone normalization, background upload, HQ fetch, or App sync behavior has been implemented.
- No claim that V0.1 quality thresholds are frozen. Thresholds and model prompts remain testable implementation parameters until enough real runs and human evaluations exist.
- No synthetic generation of user raw media.

## 9. Acceptance gates for implementation completion

Implementation may be called complete only when all of the following are evidenced:

1. Existing X01 and Production-shaped reference tests remain green.
2. New tests prove equal per-asset evidence exposure for more than sixteen assets.
3. A six-asset coherent Chapter candidate survives S07 and is reduced to three-to-five assets only in S10.
4. A mixed ancient-town/forest candidate is rejected or split before S09 final selection.
5. An unrelated invalid candidate cannot consume overlap and suppress a valid candidate.
6. Writer length/support failure triggers a bounded Writer retry or an item-scoped failure, never whole-day silent deletion.
7. Unsupported claims and unsupported canonical tags fail S12.
8. The Web builds and uses X02 as its default local run path while identifying X01 as historical.
9. A local end-to-end fixture run records stage-by-stage lineage and metrics without image payloads in durable run audits.

Real-model quality acceptance remains a later evidence gate and requires fresh user media runs plus structured human review.

## 10. Supersession rule

If the baseline hashes, API schema, stage ownership, or acceptance evidence changes, create a newer checkpoint that explicitly supersedes this file. Do not silently rewrite an accepted historical checkpoint after implementation is committed.

## 11. Additive implementation evidence

Recorded after the implementation commit; this section adds verification evidence without changing the decisions above.

- Algorithm implementation commit: `366e5a8` (`feat(codex): add staged real-media preview x02`)
- Local Web integration commit: `5543023` (`feat(codex): switch test lab to staged x02 preview`)
- Algorithm test result: 111 tests passed, including X01 compatibility, X02 fixture end-to-end, loopback HTTP, fair evidence exposure, six-member candidate handling, semantic-coherence rejection, bounded Writer retry, and billable failure accounting.
- Web verification: production build passed, two rendered-page contract tests passed, and lint passed.
- X02 module SHA-256: `9f1680d63a48c78a42a0b384ffe6a1c236c0e3e7c95ff19cfde4ab90c9640dbf`
- X02 schema SHA-256: `777342f8edbdc504e8edb8d859a0fd63844e80290c79f3403aa491997d46fad7`
- Local server SHA-256: `233eb0f0e172083dd846d8004af6f99e6cf308eee904e61ef1bb96c9090eb9e6`
- X02 test SHA-256: `04107d3ffa964f7a880bc6990d4b8fb1a84de8d3101520ae7d8153c9c17d677f`
- Successful and failed X02 run audits record stage ownership, timing, tokens, estimated cost, and failure state without persisting image payloads.
- S13 remains explicitly `NOT_EXECUTED`; no Production, device-readiness, or real-model quality claim is made.

The next acceptance action is a fresh real-media import and granular human review. It may validate or falsify the implementation assumptions; it is not replaced by fixture-test success.
