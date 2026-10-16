# Integration Checkpoint V1.31 — X02 V04 Real Failure Baseline

Status: V04 FAILURE BASELINE FROZEN; V04.1 IMPLEMENTATION NOT YET CLAIMED; NOT PRODUCTION

Date: 2026-09-02

Supersedes: no accepted historical result. This checkpoint records the first real V04 run and the exact pre-V04.1 working-tree baseline. V1.25, V1.27, V1.29, and V1.30 remain authoritative for their frozen scopes.

## 1. Why this checkpoint exists

The V04 Storyline implementation and its first real run exist only in the current uncommitted research working tree. The Git `HEAD` alone cannot reproduce them. Before implementing V04.1 stop-loss changes, this checkpoint freezes the input, run evidence, implementation fingerprints, visible output, failure diagnosis, and exclusions so later work cannot silently rewrite the baseline.

## 2. Repository and scope boundary

- Algorithm repository: `nexleap-tech/nexleap-diary-one`.
- Algorithm branch: `codex/validation-v01-v02-20260829`.
- Algorithm `HEAD`: `aa9917ad2948550d4ce891d0cc3ca7b8acd1e9db`.
- Web local repository `HEAD`: `4336bc80d56777158dd00c58b5be6e8caac6a2e9`.
- Algorithm identity: `DIARY_ONE_X02_STAGED_PREVIEW_V04` / `X02_STAGED_REAL_MEDIA_PREVIEW_V04`.
- Evaluation pack: read-only Person 1 folder `OWNER_CONTROLLED_TEST_PACK_1/`.

This checkpoint covers only the Algorithm repository and local Web research-preview client. It does not authorize or modify Firmware/SDK, the formal App, shared project-state files, source media, cloud deployment, or S13 HQ export.

## 3. Immutable real-run evidence

- Session ID: `776e2afb-abb1-4259-8aed-5a20e4dd5394`.
- Run ID: `58465e4b-743c-49af-85a3-93531dcb9b4d`.
- Evaluation mode: `FRESH_FULL_RUN`.
- Cross-run semantic cache: `false`.
- Input: 20 videos, 74 Evidence frames.
- Model calls: 7.
- Model usage: 114,196 input Tokens and 13,581 output Tokens.
- Service/model latency: 209.383 seconds.
- Client Evidence preparation: 114.882 seconds.
- User-visible total wait: 324.510 seconds.
- Configured API estimate: USD 0.00520846; infrastructure, storage, network, and future HQ costs excluded.

Evidence fingerprints:

| Artifact | SHA-256 |
|---|---|
| `var/x02_runs/776e2afb-abb1-4259-8aed-5a20e4dd5394/runs/58465e4b-743c-49af-85a3-93531dcb9b4d.run_audit.json` | `083d683f005beb4158bbe9138668cac47ba6c7a27cf4cf9db60ee60bd1d36a3a` |
| `var/x02_runs/776e2afb-abb1-4259-8aed-5a20e4dd5394/client_trace.json` | `64ca7fc7020557ce05e78589d713c1cdb1c430171caf7ab040c5da635452d193` |
| `var/x02_runs/776e2afb-abb1-4259-8aed-5a20e4dd5394/human_review.json` | `3c2e2ea8984f51169871e000c78cfa37f18ed0467d44f7d9d5c040abf5b99f6e` |
| `docs/THIRD_PARTY_END_TO_END_ALGORITHM_AUDIT_AND_REAL_DATA_LEARNING_PLAN_V0_1.md` | `fe9e5d8f22be3ec9d11b41109cbd836dd5136e646ea642fdb642f05cc3dd41a7` |

The local `var/` evidence remains ignored and must not be committed. The Human Review is `DRAFT / UNREVIEWED` with zero completed reviews, so it is not human acceptance evidence.

## 4. Visible V04 result

- Chapters: 2.
- Ahas: 0.
- Three grounded Aha candidates were selected before Writer and all three were removed after both Writer attempts exceeded the 20-visible-character contract.
- Five eligible Aha candidates existed; selection took earlier candidates rather than ranking the complete set for independent value, evidence strength, novelty, or redundancy.
- One Chapter combined route/scenery, dog walking, riverside, forest, old-town, and architecture material.
- The other Chapter chained a broad local-commerce thread across widely separated source positions.
- All three model Storyline proposals were rejected by current deterministic gates.

This output is a failure baseline. It is not quality acceptance and must not be described as a successful Gate 2 or Gate 3 result.

## 5. Frozen causal diagnosis for V04.1

V04.1 may address the following demonstrated stop-loss defects without claiming the V05 structural redesign:

1. Writer formatting failure can erase an already selected grounded Memory.
2. Aha selection is source-order biased and lacks set-level redundancy control.
3. Same-Focus gap chaining can create an over-broad Storyline across many interruptions.
4. The One Story Gate does not yet provide an independent whole-versus-split challenge.
5. Invalid quality degrades to `0.35`, while the role gate rejects only values below `0.35`.
6. Motif normalization can erase non-ASCII text.
7. One batch/provider error can affect the complete Day Run, and current batching is fixed by asset count rather than frame/byte/Token budget.
8. Web source order is synthetic chronology and cannot be treated as verified clock time.
9. Result state must distinguish grounded content with copy fallback, partial item failures, semantic no-memory, and engineering failure.

V04.1 must not claim to have implemented Window-level Content Units, complete multi-facet Storyline reasoning, full S08, Production S13, wearable-data validation, or general user satisfaction.

## 6. Exact pre-V04.1 implementation fingerprints

### Algorithm

| Artifact | SHA-256 |
|---|---|
| `src/diary_one_ci/x02.py` | `7cecdc412def23a9ad7dde21b0c495dabc1fa269937789aa23c8a562d1636e9f` |
| `contracts/x02_staged_preview_v04.schema.json` | `41c13a97a312318f0882bb411abce21b7c8ce5f89edb38584a250f42a548bb52` |
| `src/diary_one_ci/contracts/x02_storyline_v01.json` | `dddb03b4a5a35e4d7d83c0fee7dbb02dc4e8f30cabba074ebe84c5a229616e8b` |
| `tests/test_x02.py` | `5bde5638a110837f396f5d13b8c9884da2843e46543420147202688cc46f0733` |

The X01 server and Human Evaluation files have separate in-progress changes in the same working tree. They are preserved but are not part of the V04 semantic baseline above.

### Web research client

| Artifact | SHA-256 |
|---|---|
| `app/lib/contracts.ts` | `86cc9c4fdf81c6390eda5c30130f327a0a61b8f4c42455b2d31475eebd3db2f4` |
| `app/lib/media-evidence.ts` | `b5e86b568206cdba6ad5ccea523c7299aa6203001a747da96e4a25a76d0d25ce` |
| `app/page.tsx` | `a68c16ccb2ecc522bc5862ae3533c01f39cf7f1561ab03dcc5142b2c9a1682ed` |
| `tests/rendered-html.test.mjs` | `1ec8e6bc595a8e7ef2eef0a9079fcf35456340b2612f3aa6950261f5cca24dfb` |

## 7. V04.1 acceptance boundary

Implementation acceptance requires deterministic tests for every changed contract, schema validation, Web compatibility checks, and a fresh full-run comparison against this exact Person 1 baseline. Fixed-Evidence replay remains useful diagnostic evidence but cannot replace that full run. People 2 and 3 remain separate cross-pack tests; no threshold derived from Person 1 alone may be called universal.
