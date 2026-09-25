# Integration Checkpoint V1.32 — X02 V04.1 Stop-Loss

> Historical candidate snapshot. The example-specific semantic rules in this draft are superseded by [codex V1.33](codex_INTEGRATION_CHECKPOINT_V1_33_EXAMPLE_RULE_CLEANUP.md), including the culture-only compact exception and extractive/closed-title/CAT-DOG Writer policy. Preserve this text as history, not as instructions to restore those rules.

Status: DRAFT CHECKPOINT; V04.1 IMPLEMENTATION UNDER FINAL VERIFICATION; FINAL REAL RUN PENDING; NOT QUALITY ACCEPTED; NOT PRODUCTION

Date: 2026-09-02

Parent baseline commit: `8b79fb7faa4981cf352551e4f15dff24c92a3a7e` (`codex(x02): freeze v04 real failure baseline`).

Supersedes: no accepted historical quality result. This draft records the V04.1 stop-loss implementation boundary built from the frozen V1.31 failure baseline. V1.25, V1.27, V1.29, V1.30, and V1.31 remain authoritative for their frozen scopes. V1.32 must not be marked accepted until its final test results, artifact hashes, implementation commits, and fresh full-run evidence replace every placeholder below.

> **FINAL_REAL_RUN_EVIDENCE_PENDING**
>
> No fresh V04.1 raw-media full run has been recorded in this checkpoint. Deterministic tests and fixture runs cannot prove Chapter/Aha quality, user satisfaction, latency, Token cost, or generalization. Do not describe V04.1 as a real-quality fix until this section is replaced with traceable fresh-run evidence.

## 1. Why this checkpoint exists

The first real V04 run proved that grounded inputs could still produce an unusable visible result: broad Chapter grouping, source-order-biased Aha selection, and Writer-format failures that erased three already selected Ahas. V04.1 is a bounded stop-loss release intended to prevent those demonstrated failure modes without claiming the deeper V05 Content Unit and multi-facet redesign.

This checkpoint separates four different claims:

1. implementation exists;
2. deterministic contracts are verified;
3. fresh real-model quality is observed;
4. Production readiness is accepted.

At draft time, the first claim exists as an uncommitted candidate and the second claim is being rerun against the final candidate diff. The third and fourth claims are explicitly false. Intermediate test counts are not final evidence and are superseded whenever source, schema, tests, or documentation changes.

## 2. Repository and scope boundary

- Algorithm repository: `nexleap-tech/nexleap-diary-one`.
- Algorithm branch: `codex/validation-v01-v02-20260829`.
- Parent baseline commit: `8b79fb7faa4981cf352551e4f15dff24c92a3a7e`.
- V04.1 implementation commit: `V04_1_ALGORITHM_COMMIT_PENDING`.
- Web research-client parent commit: `4336bc80d56777158dd00c58b5be6e8caac6a2e9`.
- Web research-client implementation commit: `V04_1_WEB_COMMIT_PENDING`.
- Evaluation inputs reserved for later fresh runs: the three read-only phone-media packs under `OWNER_HOME/Desktop/测试照片:录像/{1,2,3}/`.

This checkpoint covers only the Algorithm repository and the local Web research-preview client. It does not authorize or modify Firmware/SDK, the formal App, App Sync, source media, shared project-state files, public cloud deployment, S13 HQ export, or Production infrastructure.

## 3. V04.1 identity and immutable route boundary

V04.1 has a new additive identity rather than silently changing the meaning of V04:

- response schema: `DIARY_ONE_X02_STAGED_PREVIEW_V04_1`;
- pipeline identity: `X02_STAGED_REAL_MEDIA_PREVIEW_V04_1`;
- Storyline contract: `DIARY_ONE_X02_STORYLINE_V02`;
- Writer surface policy: `DIARY_ONE_X02_WRITER_SURFACE_V01`;
- preview route: `/x02/v0.4.1/preview`;
- run-sidecar route: `/x02/v0.4.1/run-sidecar`.

Historical boundaries are explicit:

- `/x02/v0.3/preview` and `/x02/v0.3/run-sidecar` remain the V03 historical compatibility surface;
- V03 retains its historical semantics and must not inherit V04.1 Storyline, Aha, Writer-fallback, result-state, or batching behavior by alias;
- the mutable `/x02/v0.4/preview` route is not allowed to masquerade as V04.1; the frozen V04 result remains reproducible from the V1.31 parent baseline;
- a V04.1 Web client must reject a V03/V04 response rather than rendering it as a current result.

## 4. Storyline V02 stop-loss

### 4.1 Candidate meaning

Storyline V02 treats a shared broad Episode such as `HISTORIC_TOWN_WALK` as context, not automatic proof that every historic-town asset belongs in one Chapter. Candidate generation may examine grounded focus, motif, beat, episode partitions, interruptions, and source order to form smaller story duties below the day-level Episode.

For example, one historic-town visit may legitimately yield separate candidates for a strolling/scenery experience, cultural or architectural discoveries, and local market life. They are not required to collapse merely because they occurred in the same old town.

### 4.2 One Story Gate and split challenge

Each selected Chapter candidate must pass an independently recorded One Story Gate. Its audit includes span, interruption evidence, temporal segments, competing Episode partitions, checks, reason codes, and a whole-versus-split challenge.

- A broad group with long span, repeated interruptions, multiple semantic partitions, or competing story duties must be challenged against bounded source-order partitions.
- The broad candidate is rejected when a partition provides a more coherent grounded story without padding.
- A two-item compact culture/architecture Chapter may pass only when each item has at least one `STRONG` or `MODERATE` fact and each member contributes at least one grounded, normalized motif that the other member does not have. Free-text fact restatements are not a distinctness facet because this deterministic gate cannot reliably resolve synonymy. Beat labels and source-order distance cannot prove content distinctness by themselves.
- The public Chapter remains bounded to grounded selected members and requires its own media selection; the gate cannot add unrelated items to satisfy a quota.

This is a V04.1 stop-loss, not the final semantic architecture. Source-order partitioning is provisional and does not equal the planned V05 Window-level Content Unit and multi-facet reasoning design.

### 4.3 Value-first Chapter selection

S09 selects Chapters by marginal Storyline value rather than maximizing Chapter count or raw asset coverage first. Later candidates must add enough coherent story value to survive. The target of roughly three to four Chapters remains a product preference, not a fabrication quota: the system may return fewer when the evidence does not support more.

## 5. Aha value-first set selection

V04.1 evaluates the complete eligible Aha set before final selection instead of taking the earliest candidates in source order.

The ranking order is grounded and lexicographic:

1. independence from a selected Chapter's story duty;
2. event or discovery salience;
3. fact support;
4. specificity;
5. novelty;
6. source quality;
7. input/import sequence only as a stable tie-breaker; it is not chronology.

Pairwise selection records `EXACT_DUPLICATE`, `UNRESOLVED_POTENTIAL_CONFLICT`, or `NO_CONFLICT_EVIDENCE`. The last value means only that the implemented same-peak checks found no conflict evidence; it is not positive proof that two candidates are distinct memories. The selector may co-select that pair, while a potential conflict is limited to at most one and an exact duplicate is forbidden. The same Observation/source is an exact duplicate; high-overlap discoveries or the same local event signature within an import-sequence gap of at most two are potential conflicts. A shared CAT/DOG subject alone no longer equates pets across a whole day.

Membership selection is value-ranked. After membership is fixed, public Aha order is deterministically sorted by input-array/import sequence (Bundle V03's validated `sequence_index`), then candidate ID. That order is an import-sequence presentation order, not capture chronology. Distinct small stories inside a longer route or trip may still become independent Ahas when their story duty is genuinely different from the Chapter.

V04.1 permits up to three grounded Ahas when Chapters exist. If no Chapter is grounded but an eligible Aha exists, exactly one may form a `HIGHLIGHT_DAY`. This is a search and selection rule, not permission to invent an Aha from weak evidence.

## 6. Writer same-candidate grounded fallback

Writer failure must not silently erase a grounded Memory merely because model copy violates a presentation contract.

The V04.1 sequence is:

1. generate Writer copy for the already selected candidate;
2. retry only invalid Writer items with the measured validation feedback;
3. if model copy remains invalid or the Writer provider fails, construct a deterministic grounded fallback from that same candidate's approved facts and closed structural fields;
4. validate the fallback through the same S11 output validator;
5. publish only if that validation passes; otherwise mark the item `COPY_BLOCKED`.

V04.1 intentionally uses an extractive Writer gate rather than attempting to prove arbitrary Chinese paraphrase entailment. A Chapter body must preserve one or two complete approved fact texts in supplied order. An Aha body must preserve exactly one event-linked approved fact and remain within 20 visible characters. Only whitespace, Unicode-width/case normalization for comparison, a fixed evidence-carrier prefix, and terminal punctuation may be normalized; substring extraction and semantic truncation are forbidden. Every model title must exactly equal the candidate's deterministic allowed title derived from the closed Storyline-focus or Event-kind table.

The deterministic fallback chooses a complete approved fact and applies the same validator. Its only non-extractive emotional-language exception is a closed `PLAYFUL_ANIMAL` CAT/DOG template: the same cited event fact must contain both the recognized pet subject and a movement/action token. Stone-path wording additionally requires the same fact and the normalized motif to support the path. If those checks fail, or an Aha fact cannot fit without deleting words, the item becomes `COPY_BLOCKED`; the fallback may not guess, truncate, change selected membership, replace the candidate, backfill another candidate, or let S12 repair generation. Surface provenance is explicit: `MODEL_WRITER` or `DETERMINISTIC_GROUNDED_FALLBACK`.

This preserves the frozen boundary that S11 writes only for S09-selected Memories, S10 chooses only their media, and S12 remains read-only validation.

## 7. Perception failure isolation and coverage truth

V04.1 makes S04 failures local and auditable rather than allowing one failed provider batch to be mislabeled as an empty day. The active behavior is deliberately classified; it is not a generic recursive-retry policy.

- The planner bounds every root perception request by 3 assets, 18 frames, and 4 MiB of normalized Evidence file bytes. The limit is not a claim about the larger multipart/base64 transport body.
- If one asset alone exceeds 4 MiB, it is rejected before a provider call as `EVIDENCE_BUDGET_EXCEEDED` and becomes terminally unresolved.
- HTTP `400/401/403/404/422/429` is neither retried nor split. Other non-transient HTTP errors likewise terminate the affected batch.
- A timeout or HTTP `5xx` may retry the original root batch exactly once, unchanged. It is never split merely because the transient retry failed.
- HTTP `413` may bisect a multi-asset batch recursively; a `413` singleton terminates. With a three-asset root, this branch has a five-call worst case: root, one singleton child, one two-asset child, and that child's two singleton children.
- Only an explicit `PERCEPTION_ASSET_LOCAL_*` contract/output error may use the same multi-asset bisection. A root singleton on that path may retry once; split children receive no extra retry budget.
- When a structurally valid batch contains item-level `FAILED` outputs, only each failed item is retried as a singleton once; already valid items are retained.
- A non-timeout transport failure, a response that is not JSON, or a response with no usable structured output is not retried or split by S04.
- Later planned root batches continue even when an earlier batch remains unresolved.

The attempt ledger distinguishes four model-call states:

| `call_status` | Exact meaning |
|---|---|
| `COMPLETED` | The gateway returned a parseable structured object; downstream deterministic item/contract gates may still reject it. |
| `HTTP_FAILED` | A non-2xx HTTP response was received. |
| `FAILED_BEFORE_RESPONSE` | Transport failed before any HTTP response. |
| `RESPONSE_INVALID` | An HTTP response arrived, but its envelope/body did not yield a usable structured object. |

Every provider attempt, including a failed one, contributes one attempted `model_calls` unit and retains latency, Token, and cost evidence when available. Only `COMPLETED` contributes to `model_call_completed_count`; the other three contribute to `model_call_failed_count`. Non-2xx responses preserve an explicit `MODEL_HTTP_<status>` error, and pre-response failures preserve their transport code.

One V04.1 run has a global ceiling of 96 attempted model calls across Perception, Structure, and Writer. A call at or beyond the ceiling is not sent. If S04 reaches the circuit breaker, remaining affected assets are recorded unresolved, the Structure model call is skipped, and the returned day is diagnostic `UNRESOLVED_DAY + PIPELINE_BLOCKED` rather than a false successful Empty Day or an unbounded retry loop. This is a call-count stop-loss, not a wall-clock deadline or Production capacity claim.

The result records the complete batching attempt graph, exact provider-call flags, `coverage_status`, and unresolved asset IDs. These controls improve failure containment but do not yet prove Production latency or capacity; fresh timing and cost evidence remain required.

## 8. Semantic state and delivery state are separate axes

V04.1 no longer compresses content meaning and engineering delivery into one ambiguous output label.

Semantic day state:

- `CHAPTER_DAY`: at least one grounded Chapter is selected;
- `HIGHLIGHT_DAY`: no Chapter, but one grounded Aha is selected;
- `EMPTY_DAY`: the full grounded pipeline completes and selects no Memory;
- `UNRESOLVED_DAY`: one or more assets remain unresolved, so the day-level semantic conclusion is deliberately withheld rather than falsely reported as empty.

Delivery state:

- `READY_PRIMARY_COPY`;
- `READY_WITH_GROUNDED_COPY_FALLBACK`;
- `READY_WITH_ITEM_BLOCKS`;
- `PIPELINE_BLOCKED`;
- `NO_GROUNDED_MEMORY`.

Every selected Memory additionally records separate S09 selection, S10 media, S11 surface, and visibility outcomes. A Writer copy block, missing media, or unresolved perception asset is therefore visible as an engineering outcome rather than being confused with semantic emptiness.

The legacy `output_mode` remains only a compatibility projection. It is not the authoritative V04.1 state model.

### 8.1 Live runtime gate, JSON Schema, and Web audit boundary

The live algorithm producer runs a fail-closed V04.1 result-state audit before returning a result. It checks input-to-Observation and input-to-Evidence coverage, batching constants and attempt lineage, top-level versus nested coverage equality, unresolved IDs, model-call counts, semantic/delivery/output-state combinations, selected-Memory outcomes, public Memory publication/visibility, Highlight-day cardinality, and sequence-only time fields. A contradiction raises a contract error; it is not silently repaired.

The committed JSON Schema is a separate interchange contract. It closes object shapes, enums, constants, and expressible cross-field state branches, but it does not replace the runtime checks that require the original Bundle or derived ledgers. Conversely, a runtime-produced result is not final verification until an actual instance also validates against the committed Schema. The Web client applies its own Bundle-bound and health-handshake checks before treating any Memory as visible; diagnostic Memories must not enter visible counts, evaluation targets, or selected-media presentation. These three boundaries are complementary and must not be described as one validator proving all three.

## 9. Web source-order and time truth

The current Web research client receives manually imported phone-library material without trustworthy capture chronology. It must therefore expose time reliability rather than inventing a real day timeline.

- On the active V04.1 route, all currently supported App Library Bundle V01, V02, and V03 inputs are `timeline_basis = SYNTHETIC_SEQUENCE_ONLY`, `timeline_date = null`, and all time-reliability flags are false. A populated legacy timestamp field is metadata, not verified chronological proof.
- Synthetic import order must not be displayed as an actual date, duration, time of day, or proof that two assets were captured close together.
- The V04.1 Web manifest uses additive `DIARY_ONE_APP_LIBRARY_BUNDLE_V03` and records this only as a zero-based contiguous `sequence_index`; Bundle V03 forbids `timeline_offset_ms`.
- V04.1 retains read compatibility for Bundle V01/V02. Historical X02 V03 continues to accept V01/V02 only and explicitly rejects Bundle V03, so the new sequence semantics cannot silently rewrite a frozen route.
- Bundle V03 is not accepted by the historical E00 smoke path because that path would synthesize `sequence_index × 120 seconds`; import order is not a substitute for capture time.
- `CAPTURE_TIME` requires a future additive contract with verified timestamp provenance, timezone, and ordering validation. It is not reachable by merely populating a field in V01/V02/V03.
- The Web renders semantic day state, delivery state, selected-Memory outcomes, and Writer surface source separately.

This Web behavior is diagnostic-preview behavior only. The future App still needs an explicit verified metadata and Sync contract. The [App Library Bundle V03 sequence-only contract](app-library-bundle-v03.md) defines the active Web boundary; [App research export V01](app-research-export-v01.md) is retained as the historical V01 export reference.

## 10. Automated verification — pre-final only

Earlier intermediate suite output is `PREVIOUS_SNAPSHOT_SUPERSEDED`. Intermediate counts are not final evidence. The final candidate must be rerun after all source, test, Schema, Web, and documentation reconciliation is complete.

| Surface | Result | Claim boundary |
|---|---|---|
| Algorithm full unit suite | `FINAL_ALGORITHM_SUITE_RESULT_PENDING` | Fresh command output against the candidate commit; count and skip reason must be recorded |
| Loopback/server exercise | `FINAL_LOOPBACK_RESULT_PENDING` | Must exercise the current V04.1 route and health handshake |
| V04.1 deterministic behavior tests | `FINAL_V04_1_BEHAVIOR_TEST_RESULT_PENDING` | Implementation evidence only; not real-model quality evidence |
| V03 historical-compatibility tests | `FINAL_V03_COMPATIBILITY_RESULT_PENDING` | Must prove no semantic aliasing into V04.1 |
| V04.1 JSON Schema validation | `FINAL_SCHEMA_INSTANCE_VALIDATION_PENDING` | A real generated instance must validate against the committed schema |
| Web lint/tests/build | `FINAL_WEB_VERIFICATION_PENDING` | Must be recorded against the final Web diff |
| Diff whitespace check | `FINAL_DIFF_CHECK_PENDING` | Must be rerun before commit |

This table must be updated from fresh command output. No earlier count is an acceptance result.

## 11. Fresh real-run evidence — mandatory before acceptance

> **FINAL_REAL_RUN_EVIDENCE_PENDING**

The final checkpoint must record at least one fresh full run from raw media through Evidence preparation, S04, Storyline/Aha selection, Writer, S12, and Web rendering. A cached Observation replay or fixed-Evidence fixture may diagnose one layer but cannot replace this run.

Required fields:

- evaluation pack and read-only source path: `PENDING`;
- session ID: `PENDING`;
- run ID: `PENDING`;
- completed timestamp and timezone: `PENDING`;
- exact algorithm commit: `PENDING`;
- exact Web commit: `PENDING`;
- model/provider identity: `PENDING`;
- fresh-run and cache flags: `PENDING`;
- input assets, durations, frames, and bytes: `PENDING`;
- per-stage latency, calls, input/output Tokens, and configured API estimate: `PENDING`;
- user-visible total wait: `PENDING`;
- coverage status and unresolved assets: `PENDING`;
- Chapters and their exact members/media/story duties: `PENDING`;
- Ahas and their independence/conflict evidence: `PENDING`;
- model-versus-fallback Writer outcomes: `PENDING`;
- semantic day state and delivery state: `PENDING`;
- run-audit, client-trace, Human Review, and other evidence SHA-256 values: `PENDING`.

The real-run review must explicitly assess Chapter purity, missing important storylines, over-splitting, Aha surprise and independence, copy naturalness and grounding, and whether the output is useful to a user. It must preserve failures as evidence rather than tuning or rewriting the same run after seeing the answer.

## 12. Acceptance matrix and non-claims

| Area | Draft status | What is still required |
|---|---|---|
| V04.1 identity/routes | implemented; final fingerprints pending | final tests, hashes, and commit |
| Storyline V02 stop-loss | implemented; deterministic evidence pre-final | fresh full-run Chapter review across real material |
| Aha value-first selection | implemented; deterministic evidence pre-final | fresh full-run Aha quality and independence review |
| Writer same-candidate fallback | implemented; deterministic evidence pre-final | real provider failure/invalid-copy observation and surface review |
| S04 failure isolation | implemented; deterministic evidence pre-final | final schema validation plus real latency/cost/coverage evidence |
| Semantic/delivery state split | implemented; final schema/Web proof pending | committed schema instance and rendered Web evidence |
| Web time truth | implemented; final Web proof pending | final lint/test/build and captured preview evidence |
| Three-person evaluation | **NOT COMPLETE** | independent fresh full runs and human reviews for People 1, 2, and 3 |
| S13 HQ export | **NOT EXECUTED** | separately designed and implemented HQ path |
| Real-model quality | **NOT PROVED** | `FINAL_REAL_RUN_EVIDENCE_PENDING` |
| User satisfaction | **NOT PROVED** | structured item-level human review and accumulated evaluation data |
| Production readiness | **FALSE** | App/Sync/cloud/security/observability/performance/HQ/release gates |

V04.1 is not the final algorithm architecture. In particular, it does not claim complete Window-level Content Units, universal Storyline thresholds, learned user personalization, wearable-data validation, Production privacy/governance, S13 export, or general satisfaction.

## 13. Versioned artifact fingerprints — placeholders until final diff

### Algorithm

| Artifact | SHA-256 |
|---|---|
| `.gitignore` | `V04_1_GITIGNORE_SHA256_PENDING` |
| `README.md` | `V04_1_README_SHA256_PENDING` |
| `pyproject.toml` | `V04_1_PYPROJECT_SHA256_PENDING` |
| `contracts/app_library_bundle_v03.schema.json` | `APP_LIBRARY_BUNDLE_V03_SCHEMA_SHA256_PENDING` |
| `contracts/x02_staged_preview_v04_1.schema.json` | `V04_1_SCHEMA_SHA256_PENDING` |
| `docs/00_READ_FIRST.md` | `V04_1_READ_FIRST_SHA256_PENDING` |
| `docs/FOR_CLAUDE_ALGORITHM_WORKFLOW_AND_CROSS_VALIDATION_PACK_V0_1.md` | `V04_1_CLAUDE_PACK_SHA256_PENDING` |
| `docs/INTEGRATION_CHECKPOINT_V1_32_X02_V04_1_STOP_LOSS.md` | `V04_1_CHECKPOINT_EXTERNAL_SHA256_RECORD_PENDING` |
| `docs/app-library-bundle-v03.md` | `APP_LIBRARY_BUNDLE_V03_DOC_SHA256_PENDING` |
| `src/diary_one_ci/bundle.py` | `APP_LIBRARY_BUNDLE_V03_LOADER_SHA256_PENDING` |
| `src/diary_one_ci/contracts/x02_storyline_v02.json` | `V04_1_STORYLINE_CONTRACT_SHA256_PENDING` |
| `src/diary_one_ci/x02.py` | `V04_1_X02_PY_SHA256_PENDING` |
| `src/diary_one_ci/x01_server.py` | `V04_1_SERVER_SHA256_PENDING` |
| `tests/test_bundle.py` | `APP_LIBRARY_BUNDLE_V03_TEST_SHA256_PENDING` |
| `tests/test_x02.py` | `V04_1_X02_TEST_SHA256_PENDING` |
| `tests/test_x01.py` | `V04_1_SERVER_TEST_SHA256_PENDING` |

### Web research client

| Artifact | SHA-256 |
|---|---|
| `README.md` | `V04_1_WEB_README_SHA256_PENDING` |
| `package.json` | `V04_1_WEB_PACKAGE_SHA256_PENDING` |
| `app/globals.css` | `V04_1_WEB_CSS_SHA256_PENDING` |
| `app/lib/contract-findings.ts` | `V04_1_WEB_FINDINGS_SHA256_PENDING` |
| `app/lib/contracts.ts` | `V04_1_WEB_CONTRACTS_SHA256_PENDING` |
| `app/lib/media-evidence.ts` | `V04_1_WEB_EVIDENCE_SHA256_PENDING` |
| `app/lib/research-run-control.ts` | `V04_1_WEB_RUN_CONTROL_SHA256_PENDING` |
| `app/lib/result-contract.ts` | `V04_1_WEB_RESULT_CONTRACT_SHA256_PENDING` |
| `app/page.tsx` | `V04_1_WEB_PAGE_SHA256_PENDING` |
| `tests/research-run-control.test.mjs` | `V04_1_WEB_RUN_CONTROL_TEST_SHA256_PENDING` |
| `tests/rendered-html.test.mjs` | `V04_1_WEB_TEST_SHA256_PENDING` |
| `tests/result-contract.test.mjs` | `V04_1_WEB_RESULT_CONTRACT_TEST_SHA256_PENDING` |

The checkpoint cannot embed its own final byte hash without changing that hash. Its SHA-256 must therefore be recorded in the immutable external closeout/commit evidence referenced by the final checkpoint; the exact Git commit and blob remain the in-repository identity.

The ignored `var/` directory and the three source-media folders must remain untracked. Evidence hashes may be recorded here, but raw private media and local run artifacts are not committed.

## 14. Rollback and next evidence sequence

The algorithm rollback point is the frozen parent baseline commit `8b79fb7faa4981cf352551e4f15dff24c92a3a7e`. The Web rollback point is `4336bc80d56777158dd00c58b5be6e8caac6a2e9`. Historical V03/V04 run audits remain append-only evidence and are not rewritten by rollback.

Required closeout order:

1. finish source, Schema, test, documentation, historical-boundary, and private-artifact exclusion checks;
2. rerun the final Algorithm unit/loopback/Schema-fixture checks and Web lint/tests/build against that exact diff;
3. create traceable Algorithm and Web **candidate commits**, record their hashes, and verify the working trees contain no unrecorded implementation drift; candidate does not mean accepted;
4. restart the local service from the exact candidate, then verify `/health`, Bundle V03, route, schema/pipeline, Storyline, Writer, batching, and contract fingerprints before selecting private media;
5. after the required action-time privacy confirmation, run a fresh raw-media full pipeline from the candidate and record truthful latency, Token, cost, output, coverage, Schema-instance, Web-contract, and rendered-result evidence;
6. conduct item-level Chapter/Aha/copy review without silently retuning that run, then record sidecar/Human Review and evidence SHA-256 values;
7. if the review causes any implementation change, create a new candidate and repeat the full fresh run; old evidence remains immutable and cannot certify the new candidate;
8. only after all placeholders are replaced decide whether V1.32 is accepted, rejected, or superseded.

Until all eight steps are complete, the only defensible claim is: **V04.1 stop-loss implementation exists locally as a candidate under final deterministic verification; fresh real-model quality, S13, user satisfaction, and Production readiness remain unproved.**
