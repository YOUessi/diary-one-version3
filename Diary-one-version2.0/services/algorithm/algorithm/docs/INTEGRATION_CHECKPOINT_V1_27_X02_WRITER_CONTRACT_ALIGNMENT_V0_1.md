# Integration Checkpoint V1.27 — X02 Writer Contract Alignment V0.1

Status: IMPLEMENTATION VERIFIED LOCALLY; REAL-MODEL RECHECK PENDING; NOT PRODUCTION

Date: 2026-09-01

Supersedes: V1.26 only for X02 Writer contract delivery, Writer audit detail, and blocked-day result semantics. V1.26 stage ownership, Evidence policy, exclusions, and other acceptance evidence remain inherited.

## 1. Why this checkpoint exists

The latest 20-video real-media run selected four Chapter candidates and three Aha candidates, but both bounded Writer attempts rejected every item. The Web therefore showed zero Chapter, zero Aha, and `EMPTY_DAY`, even though upstream selection had produced seven Memory candidates.

Recorded evidence:

- Session: `4c1ed154-5d18-4fa5-9bca-fed6a4e04944`
- Run: `21d64336-fe8c-4f34-90e6-a4f43d797b4d`
- Input: 20 videos / 60 Evidence frames
- Selected before Writer: 4 Chapter / 3 Aha
- Visible after Writer: 0 Chapter / 0 Aha
- Writer attempts: 2
- Writer usage: 24,412 input tokens / 5,905 output tokens
- Writer latency: about 76 seconds

This was an implementation-contract failure, not evidence that the day was empty and not yet evidence that the selected candidates were qualitatively correct.

## 2. Verified baseline and authority

- Algorithm baseline commit before this change: `7676262d92791124f132548ec218124d1607342f`.
- Web baseline commit before this change: `5543023`.
- Accepted predecessor: `INTEGRATION_CHECKPOINT_V1_26_STAGED_REAL_MEDIA_PREVIEW_V0_1.md`, SHA-256 `71fb10a563f2eb2e34c56fc1cf3e4183e6a94687963f8f07136bce17aaf56529`.
- Frozen S11 authority: `CANONICAL_CHECKPOINT_V1_22_GROUNDED_NARRATIVE_AND_MEMORY_INDEX.md`, SHA-256 `5e1575002dc1677a3ec672f4b230808275547893d813144724ad66973ff98322`.

The V1.22 authority freezes Chapter Story as one sentence by default and at most two sentences. It does not freeze a 48-character Chapter hard limit. It freezes the current Chinese Aha Moment Line at one peak-centered sentence and no more than 20 visible characters.

## 3. Root cause

1. The X02 Writer prompt told the model that Chapter Story should be one or two sentences, but the validator later rejected Story over 48 visible characters.
2. The 48-character rejection gate had no frozen product authority and silently narrowed V1.22.
3. The Aha 20-character rule was present in the prompt, but Qwen was called in JSON Object mode; the attached schema described `text` only as a string and did not enforce its length.
4. The first validator applied a generic 160-character parsing bound before the type-specific gates. It emitted `writer.text length is invalid` without the draft, actual visible-character count, sentence count, or exact target.
5. The bounded retry therefore received a generic failure and could repeat the same mistake.
6. When all selected items were Writer-blocked, result assembly inferred `EMPTY_DAY` from the empty visible arrays, conflating operational failure with semantic emptiness.

## 4. Aligned implementation contract

### 4.1 Chapter

- Hard product gates remain: Title 2–10 visible Chinese characters, justified extension to 11–12; Story one sentence by default and at most two.
- `48` remains only an X02 concise-writing target and produces `CHAPTER_STORY_OVER_PREVIEW_WRITING_TARGET` audit evidence when exceeded.
- Exceeding 48 cannot delete an otherwise grounded one- or two-sentence Chapter.
- No substring truncation is allowed.

### 4.2 Aha

- Moment Line remains exactly one sentence and at most 20 visible characters.
- The prompt explains the counting rule and instructs the Writer to count and rewrite before returning.
- The deterministic validator remains authoritative.
- No automatic truncation is allowed because truncation can remove the event, actor, relation, or punctuation needed for a complete sentence.

### 4.3 Audit and bounded retry

Every Writer item now records, when available:

- attempt number;
- bounded draft Title and text;
- measured visible-character counts;
- sentence count;
- applicable minimum/maximum or X02 writing target;
- exact reason codes and non-blocking quality flags.

Attempt 2 receives only failed Memory items and their exact attempt-1 diagnostics. Valid attempt-1 items remain retained and are not regenerated.

### 4.4 Day-state semantics

If upstream selected Memory candidates exist but all visible results are blocked by Writer or final validation, X02 returns `PIPELINE_BLOCKED`, not `EMPTY_DAY`.

`EMPTY_DAY` remains reserved for a genuine semantic result with no selected/publishable Chapter or Aha and no blocked selected Memory.

The Web displays `生成受阻` and explicitly states that candidates still exist; it does not describe the result as a legitimate content-empty day.

## 5. Interface changes

- `contracts/x02_staged_preview_v01.schema.json` adds the additive `PIPELINE_BLOCKED` value to `output_mode`.
- Existing `CHAPTER_DAY`, `HIGHLIGHT_DAY`, and `EMPTY_DAY` meanings remain unchanged.
- Writer decision-trace items add diagnostic fields. Existing consumers that read only the original fields remain compatible.
- The Web TypeScript contract and result copy accept and explain `PIPELINE_BLOCKED`.

## 6. Explicit exclusions

- No Firmware/SDK or shared-status changes.
- No change to S04 perception, S05–S10 selection, S13, cloud deployment, storage, or account systems.
- No Writer model switch in this checkpoint.
- No claim that Qwen real-model copy quality is now accepted.
- No strict JSON Schema transport change while the current shared Qwen VL model remains in use.
- No English or other locale length contract.

Writer-specific model routing, strict JSON Schema transport, and the Qwen3.7-Plus versus Qwen3.8-Flash comparison remain the next isolated experiment. They must reuse saved Writer context and must not rerun visual perception unnecessarily.

## 7. Verification evidence

Algorithm verification:

- 115 tests passed; one loopback-socket test skipped because the sandbox disables local sockets.
- New tests prove:
  - Chapter Story over 48 is audited but not blocked;
  - Aha over 20 records its exact draft, count, sentence count, and target;
  - retry context contains only the failed item and its exact diagnostics;
  - a repaired Aha passes on attempt 2;
  - Writer-blocked selected candidates yield `PIPELINE_BLOCKED`, not `EMPTY_DAY`.

Web verification:

- production build passed;
- two rendered-page contract tests passed;
- lint passed.

Implementation hashes before commit:

- `src/diary_one_ci/x02.py`: `1a69c1c71d8c72f31713c894176683a26b89641de5abd5e236868c85df91c758`
- `contracts/x02_staged_preview_v01.schema.json`: `865fcb2f1766fec5940dbfe7dceef9a85184bb40734180550bc97b26241da6bc`
- `tests/test_x02.py`: `e05eeab595f9409a05c117bb7e72d5a225201f451ae0fcc98a4923e7ceef638b`
- Web `app/lib/contracts.ts`: `2ab2b27babd76d3ff1625242bea1cd1c8b5e3bf8b42ea9ac980955a1030099dd`
- Web `app/page.tsx`: `d207d5b9e2272e2f285c2286b540ac14b15acfb2080527e51416eb1a5aba3012`

## 8. Acceptance boundary

This checkpoint proves implementation alignment and deterministic regression behavior only. A fresh real-media Writer run is still required to measure first-pass pass rate, retry rate, naturalness, unsupported-claim rate, latency, and cost. Until that evidence exists, the fix must not be described as real-model quality acceptance or Production readiness.

