import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

const source = await readFile(new URL("../app/lib/result-contract.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  fileName: "result-contract.ts",
}).outputText;
const contract = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`);
const {
  perceptionBatchingConsistent,
  projectV041Memories,
  publicationAndOutcomeConsistent,
  resultStateMatrixConsistent,
  selectedOutcomeLineageConsistent,
  v041ResultContractConsistent,
} = contract;

const SESSION_ID = "11111111-1111-4111-8111-111111111111";
const SOURCE_IDS = [
  "asset_aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1",
  "asset_aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2",
  "asset_aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3",
  "asset_aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa4",
];

function uuidV5(namespace, name) {
  const namespaceBytes = Buffer.from(namespace.replaceAll("-", ""), "hex");
  const bytes = createHash("sha1").update(namespaceBytes).update(name).digest().subarray(0, 16);
  bytes[6] = (bytes[6] & 0x0f) | 0x50;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function testBundle(assetCount = 2, sizes = []) {
  const manifestAssets = SOURCE_IDS.slice(0, assetCount).map((assetId, index) => {
    const frameId = `frame-${index + 1}`;
    return {
      asset_id: assetId,
      media_kind: "PHOTO",
      sequence_index: index,
      logical_asset_duration_ms: 9000,
      frames: [{
        frame_id: frameId,
        window_index: 0,
        window_count: 1,
        sample_role: "PHOTO_REPRESENTATIVE",
        canonical_offset_ms: 4500,
        source_timestamp_ms: null,
        spatial_transform: "CENTER_CROP_ASPECT_FILL",
      }],
    };
  });
  const frames = manifestAssets.map((asset, index) => ({
    frameId: asset.frames[0].frame_id,
    canonicalOffsetMs: 4500,
    windowIndex: 0,
    windowCount: 1,
    sampleRole: "PHOTO_REPRESENTATIVE",
    sourceTimestampMs: null,
    relativePath: `evidence/${asset.asset_id}/${asset.frames[0].frame_id}.jpg`,
    sha256: `hash-${index}`,
    blob: new Blob([new Uint8Array(sizes[index] || 100 + index)]),
  }));
  return {
    manifest: {
      bundle_version: "DIARY_ONE_APP_LIBRARY_BUNDLE_V03",
      normalization: { spatial_transform: "CENTER_CROP_ASPECT_FILL" },
      session: { session_id: SESSION_ID },
      assets: manifestAssets,
    },
    frames,
    evidenceBytes: frames.reduce((sum, frame) => sum + frame.blob.size, 0),
  };
}

function attemptForAssets(bundle, assetIds, index) {
  const assetSet = new Set(assetIds);
  const frameIds = bundle.manifest.assets
    .filter((asset) => assetSet.has(asset.asset_id))
    .flatMap((asset) => asset.frames.map((frame) => frame.frame_id));
  return {
    attempt_id: `attempt-${index}`,
    parent_attempt_id: null,
    asset_ids: assetIds,
    asset_count: assetIds.length,
    frame_count: frameIds.length,
    evidence_bytes: bundle.frames
      .filter((frame) => frameIds.includes(frame.frameId))
      .reduce((sum, frame) => sum + frame.blob.size, 0),
    provider_call_attempted: true,
    attempt_kind: "ROOT",
    status: "VALIDATED",
    reason_code: "PERCEPTION_BATCH_VALIDATED",
    recovery_action: "NONE",
    terminal_unresolved_asset_ids: [],
  };
}

function batchingForBundle(bundle) {
  const roots = [];
  for (let index = 0; index < bundle.manifest.assets.length; index += 3) {
    roots.push(attemptForAssets(
      bundle,
      bundle.manifest.assets.slice(index, index + 3).map((asset) => asset.asset_id),
      roots.length + 1,
    ));
  }
  return {
    policy: "V04_1_BOUNDED_ASSETS_FRAMES_BYTES_WITH_FAILURE_ISOLATION",
    max_assets: 3,
    max_frames: 18,
    max_evidence_bytes: 4194304,
    single_asset_retry_limit: 1,
    run_max_model_call_attempts: 96,
    model_call_attempt_count: roots.length,
    circuit_breaker_tripped: false,
    planned_batch_count: roots.length,
    attempts: roots,
    coverage_status: "COMPLETE",
    unresolved_asset_ids: [],
  };
}

function baseResult(bundle = testBundle()) {
  const observations = bundle.manifest.assets.map((asset, index) => ({
    id: `observation-${index + 1}`,
    asset_id: asset.asset_id.slice(6),
    source_asset_id: asset.asset_id,
    media_kind: asset.media_kind,
    status: "OBSERVED",
    facts: [{ text: `fact-${index + 1}`, evidence_frame_ids: [asset.frames[0].frame_id] }],
    degraded_fields: [],
    evidence_frame_ids: [asset.frames[0].frame_id],
  }));
  const batching = batchingForBundle(bundle);
  return {
    session_id: SESSION_ID,
    writer_surface_policy_version: "DIARY_ONE_X02_WRITER_SURFACE_V02",
    coverage_status: "COMPLETE",
    unresolved_asset_ids: [],
    semantic_day_state: "EMPTY_DAY",
    delivery_state: "NO_GROUNDED_MEMORY",
    output_mode: "EMPTY_DAY",
    selected_memory_outcomes: [],
    chapters: [],
    ahas: [],
    observations,
    decision_trace: {
      counts: {
        asset_count: bundle.manifest.assets.length,
        accepted_observation_count: bundle.manifest.assets.length,
        field_degraded_observation_count: 0,
        insufficient_evidence_observation_count: 0,
        failed_observation_count: 0,
      },
      evidence_selection: {
        selected: bundle.manifest.assets.flatMap((asset) => asset.frames).map((frame, index) => {
          const asset = bundle.manifest.assets.find((entry) => entry.frames.includes(frame));
          return {
            selection_order: index,
            asset_id: asset.asset_id.slice(6),
            source_asset_id: asset.asset_id,
            frame_id: frame.frame_id,
            media_kind: asset.media_kind,
            window_index: frame.window_index,
            window_count: frame.window_count,
            canonical_offset_ms: frame.canonical_offset_ms,
            source_timestamp_ms: frame.source_timestamp_ms,
          };
        }),
      },
      perception_batching: batching,
      observation_candidates: observations.map((observation) => ({
        source_asset_id: observation.source_asset_id,
        observation_id: observation.id,
        validation_status: "PASSED",
        terminal_status: observation.status,
      })),
      chapter_candidates: [],
      aha_candidates: [],
      s10_chapter_media: [],
      s10_aha_media: [],
      writer_items: [],
      blocked_memories: [],
    },
    trace: {
      input_bundle_version: "DIARY_ONE_APP_LIBRARY_BUNDLE_V03",
      asset_count: bundle.manifest.assets.length,
      evidence_frame_count: bundle.frames.length,
      uploaded_bytes: bundle.evidenceBytes,
      originals_uploaded: 0,
      model_calls: batching.model_call_attempt_count,
      run_max_model_call_attempts: 96,
      model_call_attempted_count: batching.model_call_attempt_count,
      model_call_completed_count: batching.model_call_attempt_count,
      model_call_failed_count: 0,
      model_call_circuit_breaker_tripped: false,
      stage_metrics: batching.attempts.map((attempt) => ({
        stage: attempt.attempt_id,
        duration_ms: 1,
        model_calls: 1,
        input_tokens: 1,
        output_tokens: 1,
        estimated_cost_usd: 0,
        call_status: "COMPLETED",
      })),
    },
  };
}

function recomputeResultState(result) {
  if (result.coverage_status === "PARTIAL_UNRESOLVED") {
    result.semantic_day_state = "UNRESOLVED_DAY";
    result.delivery_state = "PIPELINE_BLOCKED";
    result.output_mode = "PIPELINE_BLOCKED";
    return;
  }
  const chapterOutcomes = result.selected_memory_outcomes.filter((item) => item.memory_type === "CHAPTER");
  const ahaOutcomes = result.selected_memory_outcomes.filter((item) => item.memory_type === "AHA");
  const visible = result.selected_memory_outcomes.filter((item) => item.visibility_state === "VISIBLE_PREVIEW");
  result.semantic_day_state = chapterOutcomes.length
    ? "CHAPTER_DAY"
    : ahaOutcomes.length === 1
      ? "HIGHLIGHT_DAY"
      : "EMPTY_DAY";
  result.delivery_state = !result.selected_memory_outcomes.length
    ? "NO_GROUNDED_MEMORY"
    : visible.length < result.selected_memory_outcomes.length
      ? visible.length ? "READY_WITH_ITEM_BLOCKS" : "PIPELINE_BLOCKED"
      : result.selected_memory_outcomes.some((item) => item.surface_state === "DETERMINISTIC_FALLBACK_VERIFIED")
        ? "READY_WITH_GROUNDED_COPY_FALLBACK"
        : "READY_PRIMARY_COPY";
  result.output_mode = result.delivery_state === "PIPELINE_BLOCKED"
    ? "PIPELINE_BLOCKED"
    : result.semantic_day_state;
}

function addSelectedOutcome(result, {
  type = "CHAPTER",
  candidateId = `${type.toLowerCase()}-candidate-1`,
  surfaceState = "MODEL_SURFACE_VERIFIED",
  visibilityState = "VISIBLE_PREVIEW",
} = {}) {
  const ledger = type === "CHAPTER"
    ? result.decision_trace.chapter_candidates
    : result.decision_trace.aha_candidates;
  ledger.push({
    candidate_kind: type,
    candidate_id: candidateId,
    validation_status: "PASSED",
    selection_status: "SELECTED",
  });
  const memoryId = uuidV5(SESSION_ID, `${type === "CHAPTER" ? "chapter" : "aha"}:${candidateId}`);
  const mediaState = surfaceState === "NOT_ATTEMPTED" ? "S10_MEDIA_BLOCKED" : "S10_MEDIA_READY";
  const mediaCount = mediaState === "S10_MEDIA_BLOCKED" ? 0 : type === "CHAPTER" ? 3 : 1;
  const mediaLedger = type === "CHAPTER"
    ? result.decision_trace.s10_chapter_media
    : result.decision_trace.s10_aha_media;
  mediaLedger.push({
    candidate_id: candidateId,
    ...(type === "CHAPTER" ? { candidate_content_unit_count: 3 } : {}),
    final_media_count: mediaCount,
    media: Array.from({ length: mediaCount }, (_, index) => ({ index })),
  });
  result.selected_memory_outcomes.push({
    memory_type: type,
    memory_id: memoryId,
    selection_state: "S09_SELECTED",
    media_state: mediaState,
    surface_state: surfaceState,
    visibility_state: visibilityState,
  });
  if (surfaceState === "MODEL_SURFACE_VERIFIED" || surfaceState === "DETERMINISTIC_FALLBACK_VERIFIED") {
    const memory = {
      id: memoryId,
      candidate_id: candidateId,
      publication_status: visibilityState === "VISIBLE_PREVIEW"
        ? "STAGED_PREVIEW_VALIDATED"
        : "STAGED_PREVIEW_DIAGNOSTIC_ONLY",
      surface_source: surfaceState === "MODEL_SURFACE_VERIFIED"
        ? "MODEL_WRITER"
        : "DETERMINISTIC_GROUNDED_FALLBACK",
      surface_policy_version: "DIARY_ONE_X02_WRITER_SURFACE_V02",
    };
    (type === "CHAPTER" ? result.chapters : result.ahas).push(memory);
  } else {
    const failureOwner = mediaState === "S10_MEDIA_BLOCKED" ? "S10_MEDIA_EDITORIAL" : "S11_WRITER";
    result.decision_trace.blocked_memories.push({
      candidate_id: candidateId,
      memory_type: type,
      failure_owner: failureOwner,
      reason_code: failureOwner === "S10_MEDIA_EDITORIAL" ? "FINAL_MEDIA_COUNT_INVALID" : "NO_VALID_WRITER_OUTPUT_AFTER_BOUNDED_RETRY",
    });
    if (failureOwner === "S11_WRITER") {
      result.decision_trace.writer_items.push({
        candidate_id: candidateId,
        memory_type: type,
        validation_status: "REJECTED",
        reason_codes: ["WRITER_FAILED"],
      });
    }
  }
  recomputeResultState(result);
  return { candidateId, memoryId };
}

function makePartial(result, failedSourceId = result.observations.at(-1).source_asset_id) {
  const observation = result.observations.find((item) => item.source_asset_id === failedSourceId);
  observation.status = "FAILED";
  observation.facts = [];
  observation.evidence_frame_ids = [];
  const candidate = result.decision_trace.observation_candidates.find((item) => item.source_asset_id === failedSourceId);
  candidate.validation_status = "REJECTED";
  candidate.terminal_status = "FAILED";
  const root = result.decision_trace.perception_batching.attempts.find((item) => item.asset_ids.includes(failedSourceId));
  root.status = "VALIDATED_WITH_ITEM_FAILURES";
  root.reason_code = "ITEM_LEVEL_VALIDATION_FAILURE_ISOLATED";
  root.recovery_action = "TERMINAL_ITEM_FAILURE";
  root.terminal_unresolved_asset_ids = [failedSourceId];
  result.coverage_status = "PARTIAL_UNRESOLVED";
  result.unresolved_asset_ids = [failedSourceId];
  result.decision_trace.perception_batching.coverage_status = "PARTIAL_UNRESOLVED";
  result.decision_trace.perception_batching.unresolved_asset_ids = [failedSourceId];
  result.decision_trace.counts.accepted_observation_count -= 1;
  result.decision_trace.counts.failed_observation_count += 1;
  recomputeResultState(result);
  return result;
}

test("projects only validated and visible memories into the formal result", () => {
  const result = baseResult();
  const { memoryId } = addSelectedOutcome(result, {
    visibilityState: "DIAGNOSTIC_ONLY",
  });
  result.coverage_status = "PARTIAL_UNRESOLVED";
  result.unresolved_asset_ids = [SOURCE_IDS[1]];
  result.chapters[0].publication_status = "STAGED_PREVIEW_DIAGNOSTIC_ONLY";
  const projection = projectV041Memories(result);
  assert.deepEqual(projection.visibleChapters, []);
  assert.equal(projection.diagnosticMemories[0].memory.id, memoryId);
});

test("accepts the complete V04.1 delivery matrix with real S09 lineage", async (t) => {
  await t.test("empty day", async () => {
    const bundle = testBundle();
    assert.equal(await v041ResultContractConsistent(baseResult(bundle), bundle), true);
  });

  await t.test("primary model copy", async () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    addSelectedOutcome(result);
    assert.equal(await v041ResultContractConsistent(result, bundle), true);
  });

  await t.test("grounded fallback copy", async () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    addSelectedOutcome(result, {
      type: "AHA",
      surfaceState: "DETERMINISTIC_FALLBACK_VERIFIED",
    });
    assert.equal(await v041ResultContractConsistent(result, bundle), true);
  });

  await t.test("one visible item and one copy block", async () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    addSelectedOutcome(result);
    addSelectedOutcome(result, {
      type: "AHA",
      surfaceState: "COPY_BLOCKED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    assert.equal(await v041ResultContractConsistent(result, bundle), true);
  });

  await t.test("all selected copy is blocked", async () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    addSelectedOutcome(result, {
      surfaceState: "COPY_BLOCKED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    assert.equal(await v041ResultContractConsistent(result, bundle), true);
  });

  await t.test("a selected item can be explicitly blocked by the S10 media ledger", async () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    addSelectedOutcome(result, {
      surfaceState: "NOT_ATTEMPTED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    assert.equal(await v041ResultContractConsistent(result, bundle), true);
  });
});

test("rejects memory and selected outcome provenance disagreement", async (t) => {
  await t.test("surface source does not match surface state", () => {
    const result = baseResult();
    addSelectedOutcome(result, { surfaceState: "DETERMINISTIC_FALLBACK_VERIFIED" });
    result.chapters[0].surface_source = "MODEL_WRITER";
    assert.equal(publicationAndOutcomeConsistent(result), false);
  });

  await t.test("item policy version differs from the result policy", () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.chapters[0].surface_policy_version = "STALE_WRITER_POLICY";
    assert.equal(publicationAndOutcomeConsistent(result), false);
  });

  await t.test("materialized outcome has no matching memory", () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.chapters = [];
    assert.equal(publicationAndOutcomeConsistent(result), false);
  });

  await t.test("blocked outcome incorrectly materializes a memory", () => {
    const result = baseResult();
    const { candidateId, memoryId } = addSelectedOutcome(result, {
      surfaceState: "COPY_BLOCKED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    result.chapters.push({
      id: memoryId,
      candidate_id: candidateId,
      publication_status: "STAGED_PREVIEW_DIAGNOSTIC_ONLY",
      surface_source: "MODEL_WRITER",
      surface_policy_version: "DIARY_ONE_X02_WRITER_SURFACE_V02",
    });
    assert.equal(publicationAndOutcomeConsistent(result), false);
  });
});

test("binds batching, evidence, observations, and coverage to the local Bundle V03", async (t) => {
  await t.test("accepts exact four-asset root partition", () => {
    const bundle = testBundle(4);
    assert.equal(perceptionBatchingConsistent(baseResult(bundle), bundle), true);
  });

  await t.test("rejects an omitted manifest asset at the roots", () => {
    const bundle = testBundle(4);
    const result = baseResult(bundle);
    result.decision_trace.perception_batching.attempts.pop();
    result.decision_trace.perception_batching.planned_batch_count -= 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects duplicate root coverage", () => {
    const bundle = testBundle(4);
    const result = baseResult(bundle);
    result.decision_trace.perception_batching.attempts[1].asset_ids = [SOURCE_IDS[0]];
    result.decision_trace.perception_batching.attempts[1].asset_count = 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects trace asset and frame count drift", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.trace.evidence_frame_count += 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects a missing or reordered Evidence presentation", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.decision_trace.evidence_selection.selected.reverse();
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects an Observation that cites another asset frame", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.observations[0].evidence_frame_ids = ["frame-2"];
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects an uncovered or duplicated Observation", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.observations[1].source_asset_id = result.observations[0].source_asset_id;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects Observation decision status or aggregate count drift", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.decision_trace.observation_candidates[0].validation_status = "REJECTED";
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
    result.decision_trace.observation_candidates[0].validation_status = "PASSED";
    result.decision_trace.counts.accepted_observation_count -= 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("accepts an exact terminal failure ledger", async () => {
    const bundle = testBundle();
    const result = makePartial(baseResult(bundle));
    assert.equal(perceptionBatchingConsistent(result, bundle), true);
    assert.equal(await v041ResultContractConsistent(result, bundle), true);
  });

  await t.test("rejects COMPLETE when a terminal failure exists", () => {
    const bundle = testBundle();
    const result = makePartial(baseResult(bundle));
    result.coverage_status = "COMPLETE";
    result.unresolved_asset_ids = [];
    result.decision_trace.perception_batching.coverage_status = "COMPLETE";
    result.decision_trace.perception_batching.unresolved_asset_ids = [];
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects unresolved IDs that do not equal terminal failures", () => {
    const bundle = testBundle();
    const result = makePartial(baseResult(bundle));
    result.unresolved_asset_ids = [SOURCE_IDS[0]];
    result.decision_trace.perception_batching.unresolved_asset_ids = [SOURCE_IDS[0]];
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects actual frame or byte metrics that differ from local blobs", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.decision_trace.perception_batching.attempts[0].evidence_bytes += 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects a non-V03 local bundle", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    bundle.manifest.bundle_version = "DIARY_ONE_APP_LIBRARY_BUNDLE_V02";
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("accepts RESPONSE_INVALID as a distinct completed-HTTP-but-invalid-output call audit", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.trace.stage_metrics.push({
      stage: "S05_RESPONSE_INVALID",
      duration_ms: 1,
      model_calls: 1,
      input_tokens: 1,
      output_tokens: 1,
      estimated_cost_usd: 0,
      call_status: "RESPONSE_INVALID",
    });
    result.trace.model_calls += 1;
    result.trace.model_call_attempted_count += 1;
    result.trace.model_call_failed_count += 1;
    result.decision_trace.perception_batching.model_call_attempt_count += 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), true);
  });

  await t.test("rejects model call totals that do not reconcile with stage call_status", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.trace.model_call_failed_count = 1;
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });

  await t.test("rejects a no-provider failure unless the circuit breaker is open", () => {
    const bundle = testBundle();
    const result = baseResult(bundle);
    result.decision_trace.perception_batching.attempts[0].status = "FAILED";
    result.decision_trace.perception_batching.attempts[0].provider_call_attempted = false;
    result.decision_trace.perception_batching.attempts[0].reason_code = "MODEL_HTTP_500";
    result.decision_trace.perception_batching.attempts[0].recovery_action = "TERMINAL_UNRESOLVED";
    result.decision_trace.perception_batching.attempts[0].terminal_unresolved_asset_ids = [...SOURCE_IDS.slice(0, 2)];
    assert.equal(perceptionBatchingConsistent(result, bundle), false);
  });
});

test("fails closed on phantom selected outcomes and missing block provenance", async (t) => {
  await t.test("rejects an outcome whose UUID does not derive from its selected candidate", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.selected_memory_outcomes[0].memory_id = "22222222-2222-4222-8222-222222222222";
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects an outcome backed only by a non-selected candidate", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.decision_trace.chapter_candidates[0].selection_status = "NOT_SELECTED";
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects a selected candidate omitted from outcomes", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.selected_memory_outcomes = [];
    result.chapters = [];
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects a memory whose candidate_id disagrees", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.chapters[0].candidate_id = "another-candidate";
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects copy block without S11 block and rejected writer audit", async () => {
    const result = baseResult();
    addSelectedOutcome(result, {
      surfaceState: "COPY_BLOCKED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    result.decision_trace.writer_items = [];
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects media block attributed to the wrong owner", async () => {
    const result = baseResult();
    addSelectedOutcome(result, {
      surfaceState: "NOT_ATTEMPTED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    result.decision_trace.blocked_memories[0].failure_owner = "S11_WRITER";
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects a phantom blocked-memory ledger entry", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.decision_trace.blocked_memories.push({
      candidate_id: "phantom",
      memory_type: "AHA",
      failure_owner: "S11_WRITER",
      reason_code: "PHANTOM",
    });
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects a selected outcome without its exact S10 media ledger entry", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.decision_trace.s10_chapter_media = [];
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects S10 media readiness that disagrees with the actual selected count", async () => {
    const result = baseResult();
    addSelectedOutcome(result);
    result.decision_trace.s10_chapter_media[0].final_media_count = 0;
    result.decision_trace.s10_chapter_media[0].media = [];
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });

  await t.test("rejects a blocked ledger with a reason from another stage", async () => {
    const result = baseResult();
    addSelectedOutcome(result, {
      surfaceState: "COPY_BLOCKED",
      visibilityState: "DIAGNOSTIC_ONLY",
    });
    result.decision_trace.blocked_memories[0].reason_code = "FINAL_MEDIA_COUNT_INVALID";
    assert.equal(await selectedOutcomeLineageConsistent(result), false);
  });
});

test("complete coverage allows diagnostic outcomes only for real media or copy blocks", () => {
  const result = baseResult();
  addSelectedOutcome(result, { visibilityState: "DIAGNOSTIC_ONLY" });
  assert.equal(publicationAndOutcomeConsistent(result), true);
  assert.equal(resultStateMatrixConsistent(result), false);
});
