# Integration Checkpoint V1.28 — X02 Observation Semantic Contract V0.2

Status: ALGORITHM IMPLEMENTATION VERIFIED LOCALLY; APP HANDSHAKE PENDING; PAID LIVE RECHECK BLOCKED; NOT PRODUCTION

Date: 2026-09-01

Supersedes: V1.27 only for new X02 S04 Setting/Activity/Event-to-Episode compatibility behavior, result/audit identities, and live endpoints. V1.27 Writer behavior and earlier immutable evidence remain inherited.

## 1. Why this checkpoint exists

A recorded six-photo run rejected every S04 candidate because V01 independently exposed Setting, Activity and Episode enums to the provider but later required Episode to be a one-to-one function of Setting. The failure audit retained only the generic conflict message, not the exact structured tuple. `APP-ALG-013` proved this as a systemic preview-contract mismatch; `APP-ALG-018` authorized the minimum V02 repair.

This checkpoint changes no canonical S04/S05 stage ownership. The larger benchmark that may move Episode interpretation out of S04 remains separate.

## 2. Verified parent

- Algorithm branch: `codex/validation-v01-v02-20260829`.
- Parent commit: `38a5affed3317707b1d1e8d7393ebf0ab0ae18a8`.
- Parent source: `src/diary_one_ci/x02.py`, SHA-256 `1a69c1c71d8c72f31713c894176683a26b89641de5abd5e236868c85df91c758`.
- Parent tests: `tests/test_x02.py`, SHA-256 `e05eeab595f9409a05c117bb7e72d5a225201f451ae0fcc98a4923e7ceef638b`.
- Parent result schema: `contracts/x02_staged_preview_v01.schema.json`, SHA-256 `865fcb2f1766fec5940dbfe7dceef9a85184bb40734180550bc97b26241da6bc`.
- Parent regression: 115 passed; one loopback-socket test skipped because the sandbox disables local sockets.

The existing untracked `var/` research tree was treated as read-only evidence and was not staged, normalized, rewritten or deleted.

## 3. V02 compatibility contract

The former `SETTING_TO_EPISODE` function is removed from new behavior. One packaged versioned data source now owns the relationship:

```text
DIARY_ONE_X02_OBSERVATION_COMPATIBILITY_V02
  -> generated S04 prompt guidance
  -> deterministic compatibility validator
  -> exhaustive positive/negative fixtures
  -> this contract documentation
```

The runtime canonical digest is `75f898d7b6fccbe1d3f831f97f772c27eeb74dd474b031c5fa660f782079635e`.

Every specific Episode contains one or more clauses. All Setting, Activity, or Event dimensions present in one clause must match; an omitted dimension is unconstrained. `OTHER` and `UNKNOWN` remain generic explicit model outputs, but the system never coerces a rejected specific tuple to either value.

Examples proven by fixtures:

- `CRAFT_SESSION + CRAFT` is valid at `HOME`, `WORKPLACE`, and `INDOOR_PUBLIC`;
- `MEAL + EATING_DRINKING` can span several visible indoor contexts;
- `WORK + WORKING` can be visible at a workplace, home, or another justified indoor setting;
- `BIRTHDAY_GATHERING` requires `GATHERING` plus visible `CEREMONY` evidence;
- every specific Episode has at least one positive clause fixture and at least one closed-vocabulary negative tuple.

## 4. Privacy-minimized rejection evidence

A per-Asset structured candidate that fails deterministic validation still becomes a terminal failed Observation. Its decision ledger now adds:

- validation rule ID and JSON field path;
- semantic-contract version and canonical digest;
- candidate status;
- bounded closed-vocabulary Setting, Activity, Episode, Subject, Event kind and Event salience fields;
- SHA-256 of the exact canonical structured candidate.

The rejection snapshot does not include original media, base64 payloads, fact text, motifs, limitations, hidden reasoning, or provider chain-of-thought. Invalid out-of-vocabulary values are represented by a fixed sentinel while the canonical hash preserves exact-evidence identity without storing the value.

Fail-closed isolation remains intact: one rejected Asset cannot erase unrelated valid Observations or valid downstream content.

## 5. New identities and endpoints

| Surface | V02 identity |
|---|---|
| Result schema | `DIARY_ONE_X02_STAGED_PREVIEW_V02` |
| Pipeline | `X02_STAGED_REAL_MEDIA_PREVIEW_V02` |
| Observation semantic contract | `DIARY_ONE_X02_OBSERVATION_COMPATIBILITY_V02` |
| Run audit | `DIARY_ONE_X02_RUN_AUDIT_V02` |
| Failed-run audit | `DIARY_ONE_X02_FAILED_RUN_AUDIT_V02` |
| Preview endpoint | `/x02/v0.2/preview` |
| Sidecar endpoint | `/x02/v0.2/run-sidecar` |

`GET /health` publishes every new identity plus the semantic-contract SHA-256. A V01 route is not aliased to V02 behavior. Existing V01 result schemas, run evidence, and App archives remain immutable historical inputs.

## 6. Deterministic verification

- 119 tests passed.
- One loopback-socket integration test was skipped only because the sandbox disables local sockets.
- New coverage proves:
  - every specific Episode rule has positive and negative coverage;
  - craft across three indoor settings;
  - visible-event requirements for event-shaped Episodes;
  - Prompt generation from the same versioned data read by the validator;
  - exact rule/path diagnostics and structured-candidate hash;
  - no free-form fact or motif leakage into the rejection snapshot or persisted run audit;
  - one invalid Asset does not erase the five unrelated accepted Observations or their Chapter;
  - V02 result and audit identities;
  - prior X01, Writer, Production-reference, Evidence and validation regressions remain green.

## 7. Implementation hashes before atomic commit

| Artifact | SHA-256 |
|---|---|
| Packaged compatibility JSON | `9a4495045765cd930add7555eb25962e285b01cc6a4f86de67f87ed6a39b0edd` |
| `src/diary_one_ci/x02.py` | `94de9117d2b112ef5785439feedfab1cbff8f5d4a867f429c8229228f7321ebc` |
| `src/diary_one_ci/x01_server.py` | `f23641388337fcfbd505759ae437e8f458e6a236973542d668e71f33826b1b80` |
| V02 result schema | `d21340d167deb8085292d6a2f4b3c3ce21d43fb853892507787ec8f886cfc1e6` |
| X02 tests | `ff1b591190432d091d8f21d3a56d99736cd9b7064026050528462efffe4c020e` |
| Server/X01 tests | `529bbce343c9ad0e5ed04f0eee526f69774397d945803363855382c6c9fc9c29` |
| Packaging config | `8a8cb50eddef9d8cb1357c9d760a03ce5cc3391f384f20e506c2b948d029c44a` |
| README | `e477d8983b29ac18f4cfe92e4d202fe151d602bc1d99f4fd94625f8c015d6623` |

The exact atomic implementation commit is recorded by the cross-repository `APP-ALG-018` acceptance checkpoint after commit creation.

## 8. Remaining gates and exclusions

- Formal App V02 health/result admission is not proven by this Algorithm checkpoint.
- Formal App V01 archive decode is not proven by this Algorithm checkpoint.
- No remote push was performed.
- No paid model call was performed.
- No Consumer UI, Figma, Cloud, Device, Firmware/SDK, S13, or shared Project Control change was made.
- Real-model semantic quality and naturalness remain unaccepted.
- Production readiness is not claimed.

## 9. Rollback

Revert the single additive V02 implementation commit to return new-run behavior to parent `38a5aff`. V01 schema and recorded `var/` evidence do not require migration or restoration because they were not modified.
