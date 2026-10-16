import type {
  EvidenceBundle,
  X01CandidateDecision,
  X01Editorial,
  X01Result,
  X02PerceptionBatchAttempt,
  X02SelectedMemoryOutcome,
} from "./contracts";

export type MemoryType = "CHAPTER" | "AHA";

export type TypedMemory = {
  memory: X01Editorial;
  type: MemoryType;
};

type SelectedCandidate = {
  candidate: X01CandidateDecision;
  candidateId: string;
  type: MemoryType;
};

const VERIFIED_SURFACE_STATES = new Set([
  "MODEL_SURFACE_VERIFIED",
  "DETERMINISTIC_FALLBACK_VERIFIED",
]);

function memoryKey(type: MemoryType, id: string) {
  return `${type}:${id}`;
}

function candidateKey(type: MemoryType, id: string) {
  return `${type}:${id}`;
}

function typedMemories(result: X01Result): TypedMemory[] {
  return [
    ...result.chapters.map((memory) => ({ memory, type: "CHAPTER" as const })),
    ...result.ahas.map((memory) => ({ memory, type: "AHA" as const })),
  ];
}

function isVerifiedSurface(outcome: X02SelectedMemoryOutcome) {
  return outcome.media_state === "S10_MEDIA_READY"
    && VERIFIED_SURFACE_STATES.has(outcome.surface_state);
}

function isBlockedOutcome(outcome: X02SelectedMemoryOutcome) {
  return (
    outcome.media_state === "S10_MEDIA_BLOCKED"
    && outcome.surface_state === "NOT_ATTEMPTED"
    && outcome.visibility_state === "DIAGNOSTIC_ONLY"
  ) || (
    outcome.media_state === "S10_MEDIA_READY"
    && outcome.surface_state === "COPY_BLOCKED"
    && outcome.visibility_state === "DIAGNOSTIC_ONLY"
  );
}

function expectedSurfaceSource(outcome: X02SelectedMemoryOutcome) {
  if (outcome.surface_state === "MODEL_SURFACE_VERIFIED") return "MODEL_WRITER";
  if (outcome.surface_state === "DETERMINISTIC_FALLBACK_VERIFIED") {
    return "DETERMINISTIC_GROUNDED_FALLBACK";
  }
  return null;
}

function exactStringArray(left: unknown, right: readonly string[]) {
  return Array.isArray(left)
    && left.length === right.length
    && left.every((item, index) => typeof item === "string" && item === right[index]);
}

function exactStringSet(left: unknown, right: readonly string[]) {
  if (!Array.isArray(left) || left.some((item) => typeof item !== "string")) return false;
  if (new Set(left).size !== left.length || new Set(right).size !== right.length) return false;
  if (left.length !== right.length) return false;
  const expected = new Set(right);
  return left.every((item) => expected.has(item));
}

function publicAssetId(sourceAssetId: string) {
  return sourceAssetId.startsWith("asset_") ? sourceAssetId.slice(6) : sourceAssetId;
}

export function projectV041Memories(result: X01Result) {
  const outcomeByKey = new Map(
    result.selected_memory_outcomes.map((outcome) => [
      memoryKey(outcome.memory_type, outcome.memory_id),
      outcome,
    ]),
  );
  const isVisible = (item: TypedMemory) => {
    const outcome = outcomeByKey.get(memoryKey(item.type, item.memory.id));
    return item.memory.publication_status === "STAGED_PREVIEW_VALIDATED"
      && outcome?.visibility_state === "VISIBLE_PREVIEW";
  };
  const chapters = result.chapters.map((memory) => ({ memory, type: "CHAPTER" as const }));
  const ahas = result.ahas.map((memory) => ({ memory, type: "AHA" as const }));
  const visibleChapters = chapters.filter(isVisible).map((item) => item.memory);
  const visibleAhas = ahas.filter(isVisible).map((item) => item.memory);
  const diagnosticMemories = [...chapters, ...ahas].filter((item) => !isVisible(item));
  return {
    visibleChapters,
    visibleAhas,
    visibleMemories: [...visibleChapters, ...visibleAhas],
    diagnosticMemories,
  };
}

export function isV041SelectedMemoryOutcome(value: unknown): value is X02SelectedMemoryOutcome {
  if (!value || typeof value !== "object") return false;
  const item = value as Record<string, unknown>;
  const baseValid = (item.memory_type === "CHAPTER" || item.memory_type === "AHA")
    && typeof item.memory_id === "string"
    && item.memory_id.length > 0
    && item.selection_state === "S09_SELECTED"
    && (item.media_state === "S10_MEDIA_READY" || item.media_state === "S10_MEDIA_BLOCKED")
    && (
      item.surface_state === "MODEL_SURFACE_VERIFIED"
      || item.surface_state === "DETERMINISTIC_FALLBACK_VERIFIED"
      || item.surface_state === "COPY_BLOCKED"
      || item.surface_state === "NOT_ATTEMPTED"
    )
    && (item.visibility_state === "VISIBLE_PREVIEW" || item.visibility_state === "DIAGNOSTIC_ONLY");
  if (!baseValid) return false;
  if (item.media_state === "S10_MEDIA_BLOCKED") {
    return item.surface_state === "NOT_ATTEMPTED"
      && item.visibility_state === "DIAGNOSTIC_ONLY";
  }
  if (item.surface_state === "COPY_BLOCKED") {
    return item.visibility_state === "DIAGNOSTIC_ONLY";
  }
  if (item.surface_state === "NOT_ATTEMPTED") return false;
  return item.visibility_state === "VISIBLE_PREVIEW" || item.visibility_state === "DIAGNOSTIC_ONLY";
}

export function publicationAndOutcomeConsistent(result: X01Result) {
  const memories = typedMemories(result);
  const memoryByKey = new Map(
    memories.map((item) => [memoryKey(item.type, item.memory.id), item]),
  );
  if (memoryByKey.size !== memories.length) return false;

  const outcomeByKey = new Map(
    result.selected_memory_outcomes.map((outcome) => [
      memoryKey(outcome.memory_type, outcome.memory_id),
      outcome,
    ]),
  );
  if (outcomeByKey.size !== result.selected_memory_outcomes.length) return false;

  for (const outcome of result.selected_memory_outcomes) {
    const item = memoryByKey.get(memoryKey(outcome.memory_type, outcome.memory_id));
    if (!isVerifiedSurface(outcome)) {
      if (item) return false;
      continue;
    }
    if (!item) return false;
    const expectedPublication = outcome.visibility_state === "VISIBLE_PREVIEW"
      ? "STAGED_PREVIEW_VALIDATED"
      : "STAGED_PREVIEW_DIAGNOSTIC_ONLY";
    if (item.memory.publication_status !== expectedPublication) return false;
    if (item.memory.surface_source !== expectedSurfaceSource(outcome)) return false;
    if (item.memory.surface_policy_version !== result.writer_surface_policy_version) return false;
  }

  return memories.every((item) => {
    const outcome = outcomeByKey.get(memoryKey(item.type, item.memory.id));
    return Boolean(outcome && isVerifiedSurface(outcome));
  });
}

type ManifestAsset = EvidenceBundle["manifest"]["assets"][number];
type ManifestFrame = ManifestAsset["frames"][number];

type BundleTruth = {
  assetIds: string[];
  frameIds: string[];
  assetById: Map<string, ManifestAsset>;
  frameById: Map<string, ManifestFrame>;
  frameOwnerById: Map<string, string>;
  frameBytesById: Map<string, number>;
};

function bundleTruth(bundle: EvidenceBundle): BundleTruth | null {
  const version = bundle.manifest.bundle_version;
  if (version !== "DIARY_ONE_APP_LIBRARY_BUNDLE_V03" && version !== "DIARY_ONE_APP_LIBRARY_BUNDLE_V04") return null;
  const transform = version === "DIARY_ONE_APP_LIBRARY_BUNDLE_V04" ? "ASPECT_FIT_LETTERBOX" : "CENTER_CROP_ASPECT_FILL";
  if (bundle.manifest.normalization?.spatial_transform !== transform
    || bundle.manifest.assets.some((asset) => asset.frames.some((frame) => frame.spatial_transform !== transform))) return null;
  const assets = bundle.manifest.assets;
  if (!assets.length) return null;
  const assetIds = assets.map((asset) => asset.asset_id);
  if (assetIds.some((id) => typeof id !== "string" || !id) || new Set(assetIds).size !== assetIds.length) {
    return null;
  }
  if (assets.some((asset, index) => (
    asset.sequence_index !== index
    || asset.logical_asset_duration_ms !== 9000
    || !Array.isArray(asset.frames)
    || !asset.frames.length
  ))) return null;

  const frameById = new Map<string, ManifestFrame>();
  const frameOwnerById = new Map<string, string>();
  const frameIds: string[] = [];
  for (const asset of assets) {
    for (const frame of asset.frames) {
      if (!frame.frame_id || frameById.has(frame.frame_id)) return null;
      frameIds.push(frame.frame_id);
      frameById.set(frame.frame_id, frame);
      frameOwnerById.set(frame.frame_id, asset.asset_id);
    }
  }

  const frameBytesById = new Map<string, number>();
  for (const frame of bundle.frames) {
    if (!frame.frameId || frameBytesById.has(frame.frameId) || frame.blob.size < 1) return null;
    frameBytesById.set(frame.frameId, frame.blob.size);
  }
  if (!exactStringSet([...frameBytesById.keys()], frameIds)) return null;
  const measuredEvidenceBytes = [...frameBytesById.values()].reduce((sum, value) => sum + value, 0);
  if (bundle.evidenceBytes !== measuredEvidenceBytes) return null;

  return {
    assetIds,
    frameIds,
    assetById: new Map(assets.map((asset) => [asset.asset_id, asset])),
    frameById,
    frameOwnerById,
    frameBytesById,
  };
}

function expectedAttemptMetrics(attempt: X02PerceptionBatchAttempt, truth: BundleTruth) {
  let frameCount = 0;
  let evidenceBytes = 0;
  for (const assetId of attempt.asset_ids) {
    const asset = truth.assetById.get(assetId);
    if (!asset) return null;
    frameCount += asset.frames.length;
    for (const frame of asset.frames) {
      const size = truth.frameBytesById.get(frame.frame_id);
      if (size === undefined) return null;
      evidenceBytes += size;
    }
  }
  return { frameCount, evidenceBytes };
}

function validBatchAttemptShape(value: unknown, truth: BundleTruth): value is X02PerceptionBatchAttempt {
  if (!value || typeof value !== "object") return false;
  const item = value as Record<string, unknown>;
  if (
    typeof item.attempt_id !== "string"
    || !item.attempt_id
    || (item.parent_attempt_id !== null && typeof item.parent_attempt_id !== "string")
    || !Array.isArray(item.asset_ids)
    || item.asset_ids.some((assetId) => typeof assetId !== "string" || !assetId)
    || new Set(item.asset_ids).size !== item.asset_ids.length
    || !Number.isInteger(item.asset_count)
    || Number(item.asset_count) !== item.asset_ids.length
    || Number(item.asset_count) < 1
    || Number(item.asset_count) > 3
    || !Number.isInteger(item.frame_count)
    || Number(item.frame_count) < 1
    || Number(item.frame_count) > 18
    || !Number.isInteger(item.evidence_bytes)
    || Number(item.evidence_bytes) < 1
    || typeof item.provider_call_attempted !== "boolean"
    || !["ROOT", "SPLIT_CHILD", "ORIGINAL_BATCH_RETRY", "SINGLETON_RETRY", "ITEM_RETRY"].includes(String(item.attempt_kind))
    || !["FAILED", "REJECTED_PREFLIGHT", "VALIDATED", "VALIDATED_WITH_ITEM_FAILURES"].includes(String(item.status))
    || typeof item.reason_code !== "string"
    || !item.reason_code
    || ![
      "NONE", "BISECT", "ORIGINAL_BATCH_RETRY", "SINGLETON_RETRY", "ITEM_LEVEL_RETRY",
      "TERMINAL_ITEM_FAILURE", "TERMINAL_UNRESOLVED", "TERMINAL_PREFLIGHT",
    ].includes(String(item.recovery_action))
    || !Array.isArray(item.terminal_unresolved_asset_ids)
    || item.terminal_unresolved_asset_ids.some((assetId) => typeof assetId !== "string" || !assetId)
  ) return false;

  const attempt = item as unknown as X02PerceptionBatchAttempt;
  if (new Set(attempt.terminal_unresolved_asset_ids).size !== attempt.terminal_unresolved_asset_ids.length) {
    return false;
  }
  const expected = expectedAttemptMetrics(attempt, truth);
  if (!expected || attempt.frame_count !== expected.frameCount || attempt.evidence_bytes !== expected.evidenceBytes) {
    return false;
  }
  if (!attempt.terminal_unresolved_asset_ids.every((assetId) => attempt.asset_ids.includes(assetId))) {
    return false;
  }
  if (attempt.provider_call_attempted && attempt.evidence_bytes > 4194304) return false;
  if (attempt.status === "REJECTED_PREFLIGHT") {
    return !attempt.provider_call_attempted
      && attempt.asset_count === 1
      && attempt.evidence_bytes > 4194304
      && attempt.reason_code === "EVIDENCE_BUDGET_EXCEEDED"
      && attempt.recovery_action === "TERMINAL_PREFLIGHT"
      && exactStringArray(attempt.terminal_unresolved_asset_ids, attempt.asset_ids);
  }
  if (attempt.status === "FAILED") {
    if (
      attempt.provider_call_attempted
      === (attempt.reason_code === "MODEL_CALL_CIRCUIT_BREAKER_OPEN")
    ) return false;
  }
  if (attempt.status === "VALIDATED" || attempt.status === "VALIDATED_WITH_ITEM_FAILURES") {
    if (!attempt.provider_call_attempted) return false;
  }
  return true;
}

function validRecoveryTree(attempts: X02PerceptionBatchAttempt[]) {
  const attemptById = new Map(attempts.map((attempt) => [attempt.attempt_id, attempt]));
  if (attemptById.size !== attempts.length) return false;
  const childrenByParent = new Map<string, X02PerceptionBatchAttempt[]>();
  for (const attempt of attempts) {
    if (attempt.parent_attempt_id === null) {
      if (attempt.attempt_kind !== "ROOT") return false;
      continue;
    }
    const parent = attemptById.get(attempt.parent_attempt_id);
    if (!parent || !attempt.asset_ids.every((assetId) => parent.asset_ids.includes(assetId))) return false;
    if (attempt.attempt_kind === "ROOT") return false;
    const children = childrenByParent.get(parent.attempt_id) || [];
    children.push(attempt);
    childrenByParent.set(parent.attempt_id, children);
  }

  for (const attempt of attempts) {
    const children = childrenByParent.get(attempt.attempt_id) || [];
    const childIds = children.flatMap((child) => child.asset_ids);
    if (new Set(childIds).size !== childIds.length) return false;
    switch (attempt.recovery_action) {
      case "BISECT":
        if (
          attempt.status !== "FAILED"
          || (
            attempt.reason_code !== "MODEL_HTTP_413"
            && !attempt.reason_code.startsWith("PERCEPTION_ASSET_LOCAL_")
          )
          || children.length !== 2
          || !exactStringSet(childIds, attempt.asset_ids)
          || children.some((child) => child.attempt_kind !== "SPLIT_CHILD")
          || attempt.terminal_unresolved_asset_ids.length
        ) return false;
        break;
      case "SINGLETON_RETRY":
        if (
          attempt.status !== "FAILED"
          || !attempt.reason_code.startsWith("PERCEPTION_ASSET_LOCAL_")
          || attempt.asset_count !== 1
          || children.length !== 1
          || children[0].attempt_kind !== "SINGLETON_RETRY"
          || !exactStringArray(children[0].asset_ids, attempt.asset_ids)
          || attempt.terminal_unresolved_asset_ids.length
        ) return false;
        break;
      case "ORIGINAL_BATCH_RETRY":
        if (
          attempt.status !== "FAILED"
          || (
            attempt.reason_code !== "MODEL_TRANSPORT_TIMEOUT"
            && !/^MODEL_HTTP_5\d\d$/.test(attempt.reason_code)
          )
          || children.length !== 1
          || children[0].attempt_kind !== "ORIGINAL_BATCH_RETRY"
          || !exactStringArray(children[0].asset_ids, attempt.asset_ids)
          || attempt.terminal_unresolved_asset_ids.length
        ) return false;
        break;
      case "ITEM_LEVEL_RETRY":
        if (
          attempt.status !== "VALIDATED_WITH_ITEM_FAILURES"
          || attempt.reason_code !== "ITEM_LEVEL_VALIDATION_FAILURE_ISOLATED"
          || !children.length
          || children.some((child) => child.attempt_kind !== "ITEM_RETRY" || child.asset_count !== 1)
          || attempt.terminal_unresolved_asset_ids.length
        ) return false;
        break;
      case "NONE":
        if (
          attempt.status !== "VALIDATED"
          || attempt.reason_code !== "PERCEPTION_BATCH_VALIDATED"
          || children.length
          || attempt.terminal_unresolved_asset_ids.length
        ) {
          return false;
        }
        break;
      case "TERMINAL_ITEM_FAILURE":
        if (
          attempt.status !== "VALIDATED_WITH_ITEM_FAILURES"
          || attempt.reason_code !== "ITEM_LEVEL_VALIDATION_FAILURE_ISOLATED"
          || children.length
          || !attempt.terminal_unresolved_asset_ids.length
        ) return false;
        break;
      case "TERMINAL_UNRESOLVED":
        if (
          attempt.status !== "FAILED"
          || children.length
          || !exactStringArray(attempt.terminal_unresolved_asset_ids, attempt.asset_ids)
        ) return false;
        break;
      case "TERMINAL_PREFLIGHT":
        if (
          attempt.status !== "REJECTED_PREFLIGHT"
          || children.length
          || !exactStringArray(attempt.terminal_unresolved_asset_ids, attempt.asset_ids)
        ) return false;
        break;
      default:
        return false;
    }
  }

  for (const attempt of attempts) {
    const visited = new Set<string>();
    let cursor: X02PerceptionBatchAttempt | undefined = attempt;
    let boundedRetries = 0;
    while (cursor?.parent_attempt_id) {
      if (visited.has(cursor.attempt_id)) return false;
      visited.add(cursor.attempt_id);
      const parent = attemptById.get(cursor.parent_attempt_id);
      if (!parent) return false;
      if (
        cursor.attempt_kind === "SINGLETON_RETRY"
        || cursor.attempt_kind === "ORIGINAL_BATCH_RETRY"
        || cursor.attempt_kind === "ITEM_RETRY"
      ) {
        boundedRetries += 1;
      }
      cursor = parent;
    }
    if (boundedRetries > 1) return false;
  }
  return true;
}

function modelCallTraceConsistent(result: X01Result) {
  const trace = result.trace;
  if (!trace || !Array.isArray(trace.stage_metrics)) return false;
  let totalCalls = 0;
  let completedCalls = 0;
  let failedCalls = 0;
  for (const metric of trace.stage_metrics) {
    if (!Number.isInteger(metric.model_calls) || metric.model_calls < 0) return false;
    if (metric.model_calls === 0) {
      if (metric.call_status !== undefined) return false;
      continue;
    }
    if (![
      "COMPLETED",
      "HTTP_FAILED",
      "FAILED_BEFORE_RESPONSE",
      "RESPONSE_INVALID",
    ].includes(String(metric.call_status))) return false;
    totalCalls += metric.model_calls;
    if (metric.call_status === "COMPLETED") completedCalls += metric.model_calls;
    else failedCalls += metric.model_calls;
  }
  if (
    !Number.isInteger(trace.model_call_attempted_count)
    || !Number.isInteger(trace.model_call_completed_count)
    || !Number.isInteger(trace.model_call_failed_count)
    || trace.model_calls !== totalCalls
    || trace.model_call_attempted_count !== totalCalls
    || trace.model_call_completed_count !== completedCalls
    || trace.model_call_failed_count !== failedCalls
    || completedCalls + failedCalls !== totalCalls
  ) return false;
  return !trace.model_call_circuit_breaker_tripped
    || trace.model_call_attempted_count === trace.run_max_model_call_attempts;
}

function observationAndEvidenceConsistent(result: X01Result, truth: BundleTruth) {
  if (
    result.trace?.asset_count !== truth.assetIds.length
    || result.trace?.evidence_frame_count !== truth.frameIds.length
    || result.trace?.uploaded_bytes !== [...truth.frameBytesById.values()].reduce((sum, value) => sum + value, 0)
    || result.trace?.originals_uploaded !== 0
    || result.decision_trace?.counts?.asset_count !== truth.assetIds.length
  ) return false;

  const selected = result.decision_trace?.evidence_selection?.selected;
  if (!Array.isArray(selected) || selected.length !== truth.frameIds.length) return false;
  for (let index = 0; index < selected.length; index += 1) {
    const item = selected[index];
    const frameId = truth.frameIds[index];
    const frame = truth.frameById.get(frameId);
    const sourceAssetId = truth.frameOwnerById.get(frameId);
    const asset = sourceAssetId ? truth.assetById.get(sourceAssetId) : undefined;
    if (
      !frame
      || !asset
      || item.selection_order !== index
      || item.frame_id !== frameId
      || item.source_asset_id !== sourceAssetId
      || item.asset_id !== publicAssetId(sourceAssetId)
      || item.media_kind !== asset.media_kind
      || item.window_index !== frame.window_index
      || item.window_count !== frame.window_count
      || item.canonical_offset_ms !== frame.canonical_offset_ms
      || item.source_timestamp_ms !== frame.source_timestamp_ms
    ) return false;
  }

  if (!Array.isArray(result.observations) || result.observations.length !== truth.assetIds.length) {
    return false;
  }
  const sourceIds = result.observations.map((observation) => observation.source_asset_id);
  if (!exactStringArray(sourceIds, truth.assetIds)) return false;
  const observationIds = new Set<string>();
  for (const observation of result.observations) {
    const asset = truth.assetById.get(observation.source_asset_id);
    if (
      !asset
      || !observation.id
      || observationIds.has(observation.id)
      || observation.asset_id !== publicAssetId(observation.source_asset_id)
      || observation.media_kind !== asset.media_kind
      || !Array.isArray(observation.degraded_fields)
      || !Array.isArray(observation.evidence_frame_ids)
      || new Set(observation.evidence_frame_ids).size !== observation.evidence_frame_ids.length
    ) return false;
    observationIds.add(observation.id);
    const allowedFrames = new Set(asset.frames.map((frame) => frame.frame_id));
    if (!observation.evidence_frame_ids.every((frameId) => allowedFrames.has(frameId))) return false;
    if (!Array.isArray(observation.facts)) return false;
    if (
      observation.status === "FAILED"
      && (observation.facts.length || observation.evidence_frame_ids.length)
    ) return false;
    for (const fact of observation.facts) {
      if (
        !Array.isArray(fact.evidence_frame_ids)
        || !fact.evidence_frame_ids.length
        || !fact.evidence_frame_ids.every((frameId) => allowedFrames.has(frameId))
      ) return false;
    }
  }

  const observationCandidates = result.decision_trace.observation_candidates;
  if (!Array.isArray(observationCandidates)) return false;
  const knownCandidateBySource = new Map<string, typeof observationCandidates>();
  for (const candidate of observationCandidates) {
    if (!candidate.source_asset_id || !truth.assetById.has(candidate.source_asset_id)) {
      if (
        candidate.validation_status !== "REJECTED"
        || candidate.terminal_status !== "FAILED"
        || candidate.observation_id !== null
      ) return false;
      continue;
    }
    const entries = knownCandidateBySource.get(candidate.source_asset_id) || [];
    entries.push(candidate);
    knownCandidateBySource.set(candidate.source_asset_id, entries);
  }
  for (const observation of result.observations) {
    const entries = knownCandidateBySource.get(observation.source_asset_id);
    const expectedValidation = observation.status === "FAILED"
      ? "REJECTED"
      : observation.degraded_fields.length
        ? "PASSED_WITH_FIELD_DEGRADATION"
        : "PASSED";
    if (
      !entries
      || entries.length !== 1
      || entries[0].observation_id !== observation.id
      || entries[0].terminal_status !== observation.status
      || entries[0].validation_status !== expectedValidation
    ) return false;
  }
  const counts = result.decision_trace.counts;
  if (
    counts.accepted_observation_count !== result.observations.filter(
      (observation) => observation.status === "OBSERVED" || observation.status === "PARTIAL",
    ).length
    || counts.field_degraded_observation_count !== result.observations.filter(
      (observation) => observation.degraded_fields.length > 0,
    ).length
    || counts.insufficient_evidence_observation_count !== result.observations.filter(
      (observation) => observation.status === "INSUFFICIENT_EVIDENCE",
    ).length
    || counts.failed_observation_count !== result.observations.filter(
      (observation) => observation.status === "FAILED",
    ).length
  ) return false;
  return true;
}

export function perceptionBatchingConsistent(result: X01Result, bundle: EvidenceBundle) {
  const truth = bundleTruth(bundle);
  const batching = result.decision_trace?.perception_batching;
  if (!truth || !batching || typeof batching !== "object" || !modelCallTraceConsistent(result)) {
    return false;
  }
  if (
    result.session_id !== bundle.manifest.session.session_id
    || result.trace?.input_bundle_version !== bundle.manifest.bundle_version
    || batching.policy !== "V04_1_BOUNDED_ASSETS_FRAMES_BYTES_WITH_FAILURE_ISOLATION"
    || batching.max_assets !== 3
    || batching.max_frames !== 18
    || batching.max_evidence_bytes !== 4194304
    || batching.single_asset_retry_limit !== 1
    || batching.run_max_model_call_attempts !== 96
    || !Number.isInteger(batching.model_call_attempt_count)
    || batching.model_call_attempt_count < 0
    || batching.model_call_attempt_count > 96
    || typeof batching.circuit_breaker_tripped !== "boolean"
    || result.trace?.run_max_model_call_attempts !== 96
    || result.trace?.model_call_attempted_count !== batching.model_call_attempt_count
    || result.trace?.model_call_circuit_breaker_tripped !== batching.circuit_breaker_tripped
    || !Number.isInteger(batching.planned_batch_count)
    || batching.planned_batch_count < 1
    || !Array.isArray(batching.attempts)
    || batching.attempts.length < batching.planned_batch_count
    || batching.coverage_status !== result.coverage_status
    || !exactStringArray(batching.unresolved_asset_ids, result.unresolved_asset_ids)
  ) return false;

  if (!batching.attempts.every((attempt) => validBatchAttemptShape(attempt, truth))) return false;
  if (!validRecoveryTree(batching.attempts)) return false;
  const roots = batching.attempts.filter((attempt) => attempt.parent_attempt_id === null);
  if (
    roots.length !== batching.planned_batch_count
    || !exactStringArray(roots.flatMap((attempt) => attempt.asset_ids), truth.assetIds)
  ) return false;

  const terminalUnresolved = batching.attempts.flatMap(
    (attempt) => attempt.terminal_unresolved_asset_ids,
  );
  if (!exactStringSet(terminalUnresolved, result.unresolved_asset_ids)) return false;
  const failedObservationAssets = result.observations
    .filter((observation) => observation.status === "FAILED")
    .map((observation) => observation.source_asset_id);
  if (!exactStringSet(failedObservationAssets, result.unresolved_asset_ids)) return false;
  if (
    result.coverage_status === "COMPLETE"
    && (terminalUnresolved.length || failedObservationAssets.length)
  ) return false;
  return observationAndEvidenceConsistent(result, truth);
}

function selectedCandidates(result: X01Result): SelectedCandidate[] | null {
  const selected: SelectedCandidate[] = [];
  for (const [type, candidates] of [
    ["CHAPTER" as const, result.decision_trace?.chapter_candidates],
    ["AHA" as const, result.decision_trace?.aha_candidates],
  ] as const) {
    if (!Array.isArray(candidates)) return null;
    for (const candidate of candidates) {
      if (candidate.selection_status !== "SELECTED") continue;
      if (
        candidate.validation_status !== "PASSED"
        || typeof candidate.candidate_id !== "string"
        || !candidate.candidate_id
        || (candidate.candidate_kind !== undefined && candidate.candidate_kind !== type)
      ) return null;
      selected.push({ candidate, candidateId: candidate.candidate_id, type });
    }
  }
  if (new Set(selected.map((item) => candidateKey(item.type, item.candidateId))).size !== selected.length) {
    return null;
  }
  return selected;
}

type MediaLedgerEntry = {
  candidate_id: string;
  candidate_content_unit_count?: number;
  final_media_count: number;
  media: unknown[];
};

function selectedMediaLedger(result: X01Result, selected: SelectedCandidate[]) {
  const byCandidate = new Map<string, MediaLedgerEntry>();
  for (const [type, rawEntries] of [
    ["CHAPTER" as const, result.decision_trace?.s10_chapter_media],
    ["AHA" as const, result.decision_trace?.s10_aha_media],
  ] as const) {
    if (!Array.isArray(rawEntries)) return null;
    for (const rawEntry of rawEntries) {
      if (!rawEntry || typeof rawEntry !== "object") return null;
      const entry = rawEntry as Record<string, unknown>;
      if (
        typeof entry.candidate_id !== "string"
        || !entry.candidate_id
        || !Number.isInteger(entry.final_media_count)
        || Number(entry.final_media_count) < 0
        || !Array.isArray(entry.media)
        || entry.media.length !== entry.final_media_count
        || (
          type === "CHAPTER"
          && (
            !Number.isInteger(entry.candidate_content_unit_count)
            || Number(entry.candidate_content_unit_count) < 2
          )
        )
      ) return null;
      const key = candidateKey(type, entry.candidate_id);
      if (byCandidate.has(key)) return null;
      byCandidate.set(key, entry as MediaLedgerEntry);
    }
  }
  const selectedKeys = selected.map((item) => candidateKey(item.type, item.candidateId));
  if (!exactStringSet([...byCandidate.keys()], selectedKeys)) return null;
  return byCandidate;
}

function mediaLedgerSaysReady(type: MemoryType, entry: MediaLedgerEntry) {
  if (type === "AHA") return entry.final_media_count === 1;
  return entry.final_media_count >= 3 && entry.final_media_count <= 5;
}

function uuidBytes(value: string) {
  const compact = value.toLowerCase().replace(/-/g, "");
  if (!/^[0-9a-f]{32}$/.test(compact)) return null;
  return Uint8Array.from(compact.match(/.{2}/g) || [], (part) => Number.parseInt(part, 16));
}

async function uuidV5(namespace: string, name: string) {
  const namespaceBytes = uuidBytes(namespace);
  if (!namespaceBytes || !globalThis.crypto?.subtle) return null;
  const nameBytes = new TextEncoder().encode(name);
  const payload = new Uint8Array(namespaceBytes.length + nameBytes.length);
  payload.set(namespaceBytes);
  payload.set(nameBytes, namespaceBytes.length);
  const digest = new Uint8Array(await globalThis.crypto.subtle.digest("SHA-1", payload));
  const bytes = digest.slice(0, 16);
  bytes[6] = (bytes[6] & 0x0f) | 0x50;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = [...bytes].map((value) => value.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

export async function selectedOutcomeLineageConsistent(result: X01Result) {
  const selected = selectedCandidates(result);
  if (!selected || selected.length !== result.selected_memory_outcomes.length) return false;
  const mediaByCandidate = selectedMediaLedger(result, selected);
  if (!mediaByCandidate) return false;
  const expectedByMemoryId = new Map<string, SelectedCandidate>();
  for (const item of selected) {
    const memoryId = await uuidV5(
      result.session_id,
      `${item.type === "CHAPTER" ? "chapter" : "aha"}:${item.candidateId}`,
    );
    if (!memoryId || expectedByMemoryId.has(memoryId)) return false;
    expectedByMemoryId.set(memoryId, item);
  }

  const memoryByKey = new Map(
    typedMemories(result).map((item) => [memoryKey(item.type, item.memory.id), item.memory]),
  );
  const blockedByCandidate = new Map<string, X01Result["decision_trace"]["blocked_memories"][number]>();
  if (!Array.isArray(result.decision_trace?.blocked_memories)) return false;
  for (const blocked of result.decision_trace.blocked_memories) {
    const key = candidateKey(blocked.memory_type, blocked.candidate_id);
    if (blockedByCandidate.has(key) || !blocked.reason_code) return false;
    blockedByCandidate.set(key, blocked);
  }

  const expectedBlockedKeys = new Set<string>();
  for (const outcome of result.selected_memory_outcomes) {
    const selectedItem = expectedByMemoryId.get(outcome.memory_id);
    if (!selectedItem || selectedItem.type !== outcome.memory_type) return false;
    const key = candidateKey(selectedItem.type, selectedItem.candidateId);
    const mediaEntry = mediaByCandidate.get(key);
    if (
      !mediaEntry
      || mediaLedgerSaysReady(selectedItem.type, mediaEntry)
        !== (outcome.media_state === "S10_MEDIA_READY")
    ) return false;
    const memory = memoryByKey.get(memoryKey(outcome.memory_type, outcome.memory_id));
    if (isVerifiedSurface(outcome)) {
      if (!memory || memory.candidate_id !== selectedItem.candidateId || blockedByCandidate.has(key)) {
        return false;
      }
      continue;
    }
    expectedBlockedKeys.add(key);
    if (memory) return false;
    const blocked = blockedByCandidate.get(key);
    if (!blocked) return false;
    if (outcome.media_state === "S10_MEDIA_BLOCKED") {
      if (
        blocked.failure_owner !== "S10_MEDIA_EDITORIAL"
        || blocked.reason_code !== "FINAL_MEDIA_COUNT_INVALID"
      ) return false;
    } else if (outcome.surface_state === "COPY_BLOCKED") {
      const singlePass = ["DIARY_ONE_X02_WRITER_EXIT_V01", "DIARY_ONE_X02_WRITER_EXIT_V02"].includes(
        result.decision_trace.runtime_policies?.writer_exit || "",
      );
      if (
        blocked.failure_owner !== "S11_WRITER"
        || blocked.reason_code !== (singlePass
          ? "NO_VALID_WRITER_OUTPUT_AFTER_SINGLE_PASS_AND_LOCAL_FALLBACK"
          : "NO_VALID_WRITER_OUTPUT_AFTER_BOUNDED_RETRY")
      ) return false;
      const writerEntries = result.decision_trace.writer_items.filter((item) => (
        item.candidate_id === selectedItem.candidateId && item.memory_type === selectedItem.type
      ));
      if (
        !writerEntries.some((item) => item.validation_status === "REJECTED")
        || writerEntries.some((item) => item.validation_status === "PASSED")
      ) return false;
    } else {
      return false;
    }
  }
  return exactStringSet([...blockedByCandidate.keys()], [...expectedBlockedKeys]);
}

export function resultStateMatrixConsistent(result: X01Result) {
  const outcomes = result.selected_memory_outcomes;
  if (!outcomes.every(isV041SelectedMemoryOutcome)) return false;
  if (new Set(result.unresolved_asset_ids).size !== result.unresolved_asset_ids.length) return false;

  const chapterOutcomes = outcomes.filter((item) => item.memory_type === "CHAPTER");
  const ahaOutcomes = outcomes.filter((item) => item.memory_type === "AHA");
  const visibleOutcomes = outcomes.filter((item) => item.visibility_state === "VISIBLE_PREVIEW");
  const fallbackOutcomes = outcomes.filter(
    (item) => item.surface_state === "DETERMINISTIC_FALLBACK_VERIFIED",
  );

  let expectedSemanticState: X01Result["semantic_day_state"];
  if (result.coverage_status === "PARTIAL_UNRESOLVED") {
    if (!result.unresolved_asset_ids.length || visibleOutcomes.length) return false;
    expectedSemanticState = "UNRESOLVED_DAY";
  } else if (result.coverage_status === "COMPLETE") {
    if (result.unresolved_asset_ids.length) return false;
    if (outcomes.some((item) => item.visibility_state === "DIAGNOSTIC_ONLY" && !isBlockedOutcome(item))) {
      return false;
    }
    if (chapterOutcomes.length) expectedSemanticState = "CHAPTER_DAY";
    else if (ahaOutcomes.length === 1) expectedSemanticState = "HIGHLIGHT_DAY";
    else if (!ahaOutcomes.length) expectedSemanticState = "EMPTY_DAY";
    else return false;
  } else {
    return false;
  }
  if (result.semantic_day_state !== expectedSemanticState) return false;

  let expectedDeliveryState: X01Result["delivery_state"];
  if (result.coverage_status === "PARTIAL_UNRESOLVED") {
    expectedDeliveryState = "PIPELINE_BLOCKED";
  } else if (!outcomes.length) {
    expectedDeliveryState = "NO_GROUNDED_MEMORY";
  } else if (visibleOutcomes.length < outcomes.length) {
    expectedDeliveryState = visibleOutcomes.length ? "READY_WITH_ITEM_BLOCKS" : "PIPELINE_BLOCKED";
  } else if (fallbackOutcomes.length) {
    expectedDeliveryState = "READY_WITH_GROUNDED_COPY_FALLBACK";
  } else {
    expectedDeliveryState = "READY_PRIMARY_COPY";
  }
  if (result.delivery_state !== expectedDeliveryState) return false;

  const expectedOutputMode = expectedDeliveryState === "PIPELINE_BLOCKED"
    ? "PIPELINE_BLOCKED"
    : expectedSemanticState;
  return result.output_mode === expectedOutputMode;
}

export async function v041ResultContractConsistent(result: X01Result, bundle: EvidenceBundle) {
  try {
    return perceptionBatchingConsistent(result, bundle)
      && publicationAndOutcomeConsistent(result)
      && resultStateMatrixConsistent(result)
      && await selectedOutcomeLineageConsistent(result);
  } catch {
    return false;
  }
}
