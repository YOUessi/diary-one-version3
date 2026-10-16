export type MediaKind = "PHOTO" | "VIDEO";

export type TestAsset = {
  id: string;
  file: File;
  name: string;
  kind: MediaKind;
  url: string;
  size: number;
  width: number;
  height: number;
  durationMs: number | null;
  decodeStatus: "READY" | "UNSUPPORTED";
  decodeMessage?: string;
};

export type EvidenceFrame = {
  frameId: string;
  canonicalOffsetMs: 1500 | 4500 | 7500;
  windowIndex: number;
  windowCount: 1 | 2 | 4 | 6;
  sampleRole: "PHOTO_REPRESENTATIVE" | "WINDOW_EARLY" | "WINDOW_MIDDLE" | "WINDOW_LATE";
  sourceTimestampMs: number | null;
  relativePath: string;
  sha256: string;
  blob: Blob;
};

export type ClientAssetTrace = {
  asset_id: string;
  sequence: number;
  source_display_name: string;
  media_kind: MediaKind;
  original_bytes: number;
  evidence_bytes: number;
  evidence_frame_count: number;
  evidence_generation_ms: number;
  source_hash_ms: number;
  total_duration_ms: number;
};

export type ClientRunStageMetric = {
  stage: "EVIDENCE_PREPARATION" | "UPLOAD_AND_SERVICE_ROUND_TRIP" | "RESPONSE_PARSE";
  started_at: string;
  finished_at: string;
  duration_ms: number;
  input_bytes: number | null;
  output_bytes: number | null;
};

export type ClientRunTrace = {
  trace_version: "DIARY_ONE_WEB_CLIENT_TRACE_V01";
  session_id: string;
  run_id?: string;
  started_at: string;
  finished_at: string | null;
  total_duration_ms: number | null;
  asset_count: number;
  original_bytes: number;
  evidence_bytes: number;
  evidence_frame_count: number;
  http_status: number | null;
  asset_metrics: ClientAssetTrace[];
  stages: ClientRunStageMetric[];
};

export type EvidenceBundle = {
  manifest: AppLibraryBundleManifest;
  frames: EvidenceFrame[];
  evidenceBytes: number;
  /** Optional during the V01-to-V02 Web migration. */
  clientTrace?: ClientRunTrace;
};

export type AppLibraryBundleManifest = {
  bundle_version: "DIARY_ONE_APP_LIBRARY_BUNDLE_V03" | "DIARY_ONE_APP_LIBRARY_BUNDLE_V04";
  research_only: true;
  session: {
    session_id: string;
    exported_at: string;
    timezone: "TEST_DAY_NO_TIMEZONE";
  };
  device: {
    device_id: string;
    hardware_revision: "PHONE_LIBRARY_TEST";
    firmware_version: "NOT_APPLICABLE";
    sdk_version: "WEB_EVIDENCE_V03" | "WEB_EVIDENCE_V04";
  };
  normalization: {
    width: 768;
    height: 1024;
    orientation: "PORTRAIT";
    aspect_ratio: "3:4";
    spatial_transform: "CENTER_CROP_ASPECT_FILL" | "ASPECT_FIT_LETTERBOX";
    temporal_transform: "PHONE_TEST_DURATION_WINDOWS_V01";
    canonical_frame_offsets_ms: [1500, 4500, 7500];
    evidence_profile_version: "PHONE_TEST_DURATION_WINDOWS_V01";
  };
  assets: Array<{
    asset_id: string;
    /** Local display label only; never use as identity or model evidence. */
    source_display_name?: string;
    media_kind: MediaKind;
    media_source: "PHONE_LIBRARY_DAY_TEST";
    original_file_extension: string;
    original_sha256: string;
    original_bytes: number;
    original_width: number;
    original_height: number;
    original_duration_ms: number | null;
    capture_time?: never;
    original_included: false;
    /** Stable import order only; it is not a timestamp or elapsed duration. */
    sequence_index: number;
    /** Required 9-second normalization envelope; never chronology or elapsed time. */
    logical_asset_duration_ms: 9000;
    materialized_video: false;
    evidence_sampling_profile: "PHOTO_SINGLE_FRAME" | "VIDEO_SINGLE_WINDOW_THREE" | "VIDEO_MULTI_WINDOW_TWO_PER_WINDOW";
    evidence_window_count: 1 | 2 | 4 | 6;
    frames: Array<{
      frame_id: string;
      window_index: number;
      window_count: 1 | 2 | 4 | 6;
      sample_role: "PHOTO_REPRESENTATIVE" | "WINDOW_EARLY" | "WINDOW_MIDDLE" | "WINDOW_LATE";
      canonical_offset_ms: 1500 | 4500 | 7500;
      source_timestamp_ms: number | null;
      relative_path: string;
      sha256: string;
      width: 768;
      height: 1024;
      spatial_transform: "CENTER_CROP_ASPECT_FILL" | "ASPECT_FIT_LETTERBOX";
    }>;
  }>;
};

/** Current local staged-preview gateway. The X01 name is kept as a source-compatible alias. */
export type X01Health = {
  runtimePolicies?: Record<string, string>;
  status: "ok";
  schemaVersion: "DIARY_ONE_X02_STAGED_PREVIEW_V04_1";
  experiment: "X02_STAGED_REAL_MEDIA_PREVIEW";
  experimental: true;
  leaderboardEligible: false;
  productionReady: false;
  modelReady: boolean;
  provider: string;
  model: string;
  maxAssets: number;
  previewPath: string;
  runSidecarPath?: string;
  maxSidecarBytes?: number;
  runAuditEnabled?: boolean;
  failedRunAuditEnabled?: boolean;
  granularObservationValidation?: boolean;
  fieldLevelObservationDegradation?: boolean;
  durationAwarePhoneTestEvidence?: boolean;
  evaluationRunMode?: "FRESH_FULL_RUN";
  crossRunSemanticCacheUsed?: false;
  appLibraryBundleVersion?: "DIARY_ONE_APP_LIBRARY_BUNDLE_V03";
  supportedAppLibraryBundleVersions?: string[];
  phoneTestSpatialTransforms?: string[];
  phoneTestEvidenceProfileVersion?: "PHONE_TEST_DURATION_WINDOWS_V01";
  observationSemanticContractVersion: string;
  observationSemanticContractSHA256: string;
  fieldDegradationContractVersion: string;
  fieldDegradationContractSHA256: string;
  storylineContractVersion?: "DIARY_ONE_X02_STORYLINE_V03";
  storylineContractSHA256: string;
  writerSurfacePolicyVersion?: "DIARY_ONE_X02_WRITER_SURFACE_V02";
  chapterMediaPolicyVersion: "DIARY_ONE_X02_CHAPTER_MEDIA_V01";
  perceptionBatchMaxAssets: 3;
  perceptionBatchMaxFrames: 18;
  perceptionBatchMaxEvidenceBytes: 4194304;
  perceptionSingleAssetRetryLimit: 1;
  contractBasis?: string;
  executionMode?: string;
  pipelineVersion?: string;
  stagedRealMediaPreviewImplemented?: boolean;
  storylineSegmentationImplemented?: boolean;
  fullStagedPipelineImplemented?: boolean;
  s13Executed?: boolean;
  historicalX01?: {
    schemaVersion: "DIARY_ONE_X01_PREVIEW_V01";
    previewPath: string;
    runSidecarPath: string;
    executionMode: string;
  };
  historicalX02V03?: {
    schemaVersion: "DIARY_ONE_X02_STAGED_PREVIEW_V03";
    pipelineVersion: "X02_STAGED_REAL_MEDIA_PREVIEW_V03";
    previewPath: "/x02/v0.3/preview";
    runSidecarPath: "/x02/v0.3/run-sidecar";
    executionMode: string;
  };
};

export type X02StorylineBeat = {
  observation_id: string;
  beat_role: "ENTRY" | "PROGRESSION" | "DISCOVERY" | "INTERACTION" | "CONTRAST" | "PEAK" | "RESULT" | "EXIT" | "ATMOSPHERE_SUPPORT";
  fact_ids: string[];
  contribution: string;
};

export type X02StorylineIdentity = {
  contract_version: "DIARY_ONE_X02_STORYLINE_V03";
  storyline_basis: "EVENT_PROGRESSION" | "ACTIVITY_THREAD" | "DISCOVERY_SERIES" | "SOCIAL_INTERACTION";
  /** Legacy annotation only; empty is valid and it does not determine grouping. */
  focus_code: string;
  thesis: string;
  storyline_form: "SINGLE" | "ADJACENT_GROUP" | "RESUMED_EPISODE" | "LOCAL_EPISODE_GROUP" | "COMPACT_TWO_MEMBER";
  episode_codes: string[];
  temporal_segments: Array<{
    observation_ids: string[];
    source_asset_ids: string[];
    time_label: string;
  }>;
  interruption_observation_ids: string[];
  beat_map: X02StorylineBeat[];
  continuity_evidence: Array<Record<string, unknown>>;
  boundary_evidence: Array<Record<string, unknown>>;
  one_story_gate: {
    decision: "PASS";
    validation_scope: "STRUCTURE_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION";
    reason_codes: string[];
  };
};

export type X01Claim = {
  fact_id?: string;
  text: string;
  claim_type?: "OBSERVED" | "DERIVED";
  support_grade?: "STRONG" | "MODERATE" | "WEAK";
  evidence_frame_ids: string[];
};

export type X01Editorial = {
  id: string;
  candidate_id?: string;
  title: string;
  time_label: string;
  story: string;
  tags: string[];
  moment_ids: string[];
  hero_asset_id: string;
  confidence?: number;
  evidence_support?: "STRONG" | "MODERATE" | "LIMITED";
  evidence_frame_ids: string[];
  claims: X01Claim[];
  selected_media?: Array<{
    asset_id: string;
    source_asset_id: string;
    observation_id: string;
    role: "HERO" | "SUPPORT" | "CORE";
    media_kind: MediaKind;
    preview_format: "PHOTO_EVIDENCE";
    evidence_frame_ids: string[];
    quality_score: number;
    motifs: string[];
  }>;
  publication_status: "STAGED_PREVIEW_VALIDATED" | "STAGED_PREVIEW_DIAGNOSTIC_ONLY";
  storyline_identity?: X02StorylineIdentity;
  surface_source: "MODEL_WRITER" | "DETERMINISTIC_GROUNDED_FALLBACK";
  surface_policy_version: string;
};

export type X01SelectedEvidence = {
  selection_order: number;
  asset_id: string;
  source_asset_id: string;
  frame_id: string;
  media_kind: MediaKind;
  window_index: number;
  window_count: number;
  sample_role: string;
  canonical_offset_ms: number;
  source_timestamp_ms: number | null;
  reason_code: string;
};

export type X01CandidateDecision = {
  candidate_kind?: "CHAPTER" | "AHA";
  source_index: number;
  source_key?: string | null;
  candidate_key?: string;
  candidate_id?: string | null;
  title?: string;
  story?: string;
  confidence?: number | null;
  episode_code?: string;
  episode_codes?: string[];
  storyline_basis?: X02StorylineIdentity["storyline_basis"];
  focus_code?: X02StorylineIdentity["focus_code"];
  thesis?: string;
  model_grouping_reason?: string;
  storyline_identity?: X02StorylineIdentity;
  proposal_source?: string;
  source_asset_ids?: string[];
  observation_ids?: string[];
  source_asset_id?: string;
  observation_id?: string;
  event_kind?: string;
  event_salience?: string;
  evidence_frame_ids?: string[];
  validation_status: "PENDING" | "PASSED" | "REJECTED";
  selection_status: "NOT_ELIGIBLE" | "PENDING" | "SELECTED" | "NOT_SELECTED";
  reason_code?: string | null;
  reason_codes: string[];
};

export type X01MomentDecision = {
  source_index: number;
  source_key: string | null;
  confidence: number | null;
  source_asset_ids: string[];
  materialized_asset_ids: string[];
  evidence_frame_ids: string[];
  validation_status: "PENDING" | "PASSED" | "REJECTED";
  materialization_status:
    | "NOT_ELIGIBLE"
    | "PENDING"
    | "MATERIALIZED"
    | "PARTIALLY_MATERIALIZED"
    | "NOT_MATERIALIZED";
  reason_code: string | null;
  reason_codes: string[];
};

export type X01ObservationDecision = {
  source_index?: number;
  source_asset_id: string | null;
  observation_id?: string | null;
  confidence?: number | null;
  evidence_frame_ids?: string[];
  invalid_frame_ids?: string[];
  validation_status: "PENDING" | "PASSED" | "PASSED_WITH_FIELD_DEGRADATION" | "REJECTED";
  terminal_status?: "OBSERVED" | "PARTIAL" | "INSUFFICIENT_EVIDENCE" | "FAILED";
  reason_code?: string | null;
  reason_codes: string[];
  detail?: string;
  degraded_fields?: Array<{
    json_field_path: string;
    validation_rule_id: string;
    action: string;
    original_value_sentinel: string;
  }>;
};

export type X02StageStatus = {
  stage: string;
  status: string;
  reason_codes: string[];
};

export type X02PerceptionBatchAttempt = {
  attempt_id: string;
  parent_attempt_id: string | null;
  asset_ids: string[];
  asset_count: number;
  frame_count: number;
  evidence_bytes: number;
  provider_call_attempted: boolean;
  attempt_kind: "ROOT" | "SPLIT_CHILD" | "ORIGINAL_BATCH_RETRY" | "SINGLETON_RETRY" | "ITEM_RETRY";
  status: "FAILED" | "REJECTED_PREFLIGHT" | "VALIDATED" | "VALIDATED_WITH_ITEM_FAILURES";
  reason_code: string;
  recovery_action:
    | "NONE"
    | "BISECT"
    | "ORIGINAL_BATCH_RETRY"
    | "SINGLETON_RETRY"
    | "ITEM_LEVEL_RETRY"
    | "TERMINAL_ITEM_FAILURE"
    | "TERMINAL_UNRESOLVED"
    | "TERMINAL_PREFLIGHT";
  terminal_unresolved_asset_ids: string[];
};

export type X02PerceptionBatching = {
  policy: "V04_1_BOUNDED_ASSETS_FRAMES_BYTES_WITH_FAILURE_ISOLATION";
  max_assets: 3;
  max_frames: 18;
  max_evidence_bytes: 4194304;
  single_asset_retry_limit: 1;
  run_max_model_call_attempts: 96;
  model_call_attempt_count: number;
  circuit_breaker_tripped: boolean;
  planned_batch_count: number;
  attempts: X02PerceptionBatchAttempt[];
  coverage_status: "COMPLETE" | "PARTIAL_UNRESOLVED";
  unresolved_asset_ids: string[];
};

/** Structured audit evidence emitted by X02, never hidden model reasoning. */
export type X01DecisionTrace = {
  runtime_policies?: Record<string, string>;
  trace_type: "AUDITABLE_STAGE_DECISION_EVIDENCE";
  contains_hidden_reasoning: false;
  scope_note: string;
  evidence_selection: {
    strategy: string;
    input_order_bias_prevention: true;
    selected: X01SelectedEvidence[];
  };
  counts: Record<string, number>;
  stage_statuses: X02StageStatus[];
  perception_batching: X02PerceptionBatching;
  observation_candidates?: X01ObservationDecision[];
  boundary_edges: Array<{
    edge_id: string;
    left_observation_id: string;
    right_observation_id: string;
    continuity_evidence: string[];
    boundary_evidence: string[];
    decision: "JOIN" | "SPLIT" | "DEFER";
    reason_code: string;
  }>;
  observation_roles: Array<{
    observation_id: string;
    source_asset_id: string;
    role: "KEEP" | "CONTEXT_ONLY" | "DROP";
    reason_code: string;
  }>;
  chapter_candidates: X01CandidateDecision[];
  aha_candidates: X01CandidateDecision[];
  chapter_set_selection: Record<string, unknown>;
  aha_set_selection: Record<string, unknown>;
  s10_chapter_media: Array<{
    candidate_id: string;
    candidate_content_unit_count: number;
    final_media_count: number;
    display_selection?: {
      selection_source: string;
      model_reason: string;
      fallback_reason: string;
      omitted_observation_ids: string[];
      candidate_membership_changed: false;
    };
    [key: string]: unknown;
  }>;
  s10_aha_media: Array<Record<string, unknown>>;
  writer_items: Array<{
    candidate_id: string;
    memory_type: "CHAPTER" | "AHA";
    validation_status: "PASSED" | "REJECTED";
    reason_codes: string[];
    detail?: string;
    surface_source?: X01Editorial["surface_source"];
    writer_exit_policy_version?: string;
    validation_scope?: string;
    draft_text?: string;
    text_visible_characters?: number;
    length_status?: string;
    length_review_required?: boolean;
    quality_flags?: string[];
  }>;
  blocked_memories: Array<{
    candidate_id: string;
    memory_type: "CHAPTER" | "AHA";
    failure_owner: string;
    reason_code: string;
  }>;
};

export type X01StageMetric = {
  stage: string;
  duration_ms: number;
  model_calls: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost_usd: number;
  provider?: string;
  model?: string;
  request_id?: string;
  model_frame_count?: number;
  pricing_basis?: string;
  /** HTTP 2xx with unusable structured output is RESPONSE_INVALID, not transport failure. */
  call_status?: "COMPLETED" | "HTTP_FAILED" | "FAILED_BEFORE_RESPONSE" | "RESPONSE_INVALID";
};

export type X01ServerMetric = {
  stage: "REQUEST_MULTIPART_MATERIALIZATION";
  duration_ms: number;
  request_body_bytes: number;
};

export type X02SemanticDayState = "CHAPTER_DAY" | "HIGHLIGHT_DAY" | "EMPTY_DAY" | "UNRESOLVED_DAY";

export type X02DeliveryState =
  | "READY_PRIMARY_COPY"
  | "READY_WITH_GROUNDED_COPY_FALLBACK"
  | "READY_WITH_ITEM_BLOCKS"
  | "PIPELINE_BLOCKED"
  | "NO_GROUNDED_MEMORY";

export type X02SelectedMemoryOutcome = {
  memory_type: "CHAPTER" | "AHA";
  memory_id: string;
  selection_state: "S09_SELECTED";
  media_state: "S10_MEDIA_READY" | "S10_MEDIA_BLOCKED";
  surface_state:
    | "MODEL_SURFACE_VERIFIED"
    | "DETERMINISTIC_FALLBACK_VERIFIED"
    | "COPY_BLOCKED"
    | "NOT_ATTEMPTED";
  visibility_state: "VISIBLE_PREVIEW" | "DIAGNOSTIC_ONLY";
};

export type X01Result = {
  schema_version: "DIARY_ONE_X02_STAGED_PREVIEW_V04_1";
  experiment: "X02_STAGED_REAL_MEDIA_PREVIEW";
  experimental: true;
  leaderboard_eligible: false;
  validation_scope: "STAGED_PREVIEW_ONLY";
  production_ready: false;
  observation_semantic_contract_version: string;
  observation_semantic_contract_sha256: string;
  field_degradation_contract_version: "DIARY_ONE_X02_FIELD_DEGRADATION_V01";
  field_degradation_contract_sha256: string;
  storyline_contract_version: "DIARY_ONE_X02_STORYLINE_V03";
  storyline_contract_sha256: string;
  writer_surface_policy_version: "DIARY_ONE_X02_WRITER_SURFACE_V02";
  chapter_media_policy_version: "DIARY_ONE_X02_CHAPTER_MEDIA_V01";
  evaluation_run_mode: "FRESH_FULL_RUN";
  cross_run_semantic_cache_used: false;
  session_id: string;
  bundle_manifest_sha256: string;
  coverage_status: "COMPLETE" | "PARTIAL_UNRESOLVED";
  unresolved_asset_ids: string[];
  output_mode: "CHAPTER_DAY" | "HIGHLIGHT_DAY" | "EMPTY_DAY" | "PIPELINE_BLOCKED";
  semantic_day_state: X02SemanticDayState;
  delivery_state: X02DeliveryState;
  selected_memory_outcomes: X02SelectedMemoryOutcome[];
  timeline_basis: "CAPTURE_TIME" | "SYNTHETIC_SEQUENCE_ONLY";
  timeline_date: string | null;
  time_reliability: {
    capture_time_reliable: boolean;
    interval_reliable: boolean;
    timezone_reliable: boolean;
  };
  observations: Array<{
    id: string;
    asset_id: string;
    source_asset_id: string;
    media_kind: MediaKind;
    status: "OBSERVED" | "PARTIAL" | "INSUFFICIENT_EVIDENCE" | "FAILED";
    facts: X01Claim[];
    setting_code: string;
    activity_code: string;
    episode_code: string;
    subject_codes: string[];
    motifs: string[];
    event_kind: string;
    event_salience: string;
    quality_score: number;
    limitations: string[];
    degraded_fields: Array<{
      json_field_path: string;
      validation_rule_id: string;
      action: string;
      original_value_sentinel: string;
    }>;
    evidence_frame_ids: string[];
  }>;
  moments: Array<{
    id: string;
    sequence_index: number;
    observation_ids: string[];
    asset_ids: string[];
    source_asset_ids: string[];
    episode_codes: string[];
    setting_codes: string[];
    activity_codes: string[];
    roles: Array<"KEEP" | "CONTEXT_ONLY" | "DROP">;
    time_label: string;
  }>;
  chapters: X01Editorial[];
  ahas: X01Editorial[];
  decision_trace: X01DecisionTrace;
  trace: {
    /** Added by the HTTP gateway; identifies one immutable audit within a Session. */
    run_id?: string;
    pipeline_version: string;
    execution_mode: "STAGED_REAL_MEDIA_PREVIEW_NOT_PRODUCTION";
    evaluation_run_mode: "FRESH_FULL_RUN";
    cross_run_semantic_cache_used: false;
    input_bundle_version: "DIARY_ONE_APP_LIBRARY_BUNDLE_V01" | "DIARY_ONE_APP_LIBRARY_BUNDLE_V02" | "DIARY_ONE_APP_LIBRARY_BUNDLE_V03" | "DIARY_ONE_APP_LIBRARY_BUNDLE_V04";
    evidence_profile_version: string;
    provider: string;
    model: string;
    request_id: string;
    request_ids: string[];
    model_calls: number;
    model_call_attempted_count: number;
    model_call_completed_count: number;
    model_call_failed_count: number;
    run_max_model_call_attempts: 96;
    model_call_circuit_breaker_tripped: boolean;
    asset_count: number;
    evidence_frame_count: number;
    model_frame_count: number;
    uploaded_bytes: number;
    originals_uploaded: 0;
    input_tokens: number;
    output_tokens: number;
    latency_seconds: number;
    estimated_cost_usd: number;
    stage_metrics: X01StageMetric[];
    total_duration_ms: number;
    stage_metric_scope: string;
    s13_status: "NOT_EXECUTED_IN_WEB_PREVIEW";
    completed_at?: string;
    server_total_before_audit_ms?: number;
    server_metrics?: X01ServerMetric[];
    /** Client-side timings are saved as a sidecar and may be joined for display. */
    client_trace?: ClientRunTrace;
  };
};

export type HumanEvaluationV01 = {
  rating: number;
  issueCodes: string[];
  notes: string;
};

/** Compatibility alias for the current EvaluationPage during V02 migration. */
export type HumanEvaluation = HumanEvaluationV01;

export type HumanReviewVerdict = "UNREVIEWED" | "PASS" | "NEEDS_CHANGE" | "REJECT" | "MISSING";

export type HumanReviewAspect =
  | "BOUNDARY"
  | "MEDIA_SELECTION"
  | "TITLE"
  | "STORY"
  | "TAGS"
  | "AHA_INDEPENDENCE"
  | "ASSET_UNDERSTANDING";

export type HumanReviewTargetType = "CHAPTER" | "AHA" | "ASSET";

export type HumanReviewAction =
  | "ADD"
  | "REMOVE"
  | "REPLACE"
  | "MOVE"
  | "SPLIT"
  | "MERGE"
  | "SUPPRESS"
  | "PROMOTE_TO_AHA";

export type HumanEvaluationIssueCodeV02 =
  | "CHAPTER_COUNT_WRONG"
  | "AHA_COUNT_WRONG"
  | "DAY_NOT_REPRESENTATIVE"
  | "FALSE_CLAIM_GLOBAL"
  | "START_WRONG"
  | "END_WRONG"
  | "SHOULD_SPLIT"
  | "SHOULD_MERGE"
  | "UNRELATED_ASSET_GROUPED"
  | "RELATED_ASSET_SEPARATED"
  | "MEDIA_IRRELEVANT"
  | "MEDIA_REDUNDANT"
  | "MEDIA_MISSING"
  | "HERO_WRONG"
  | "FRAME_WRONG"
  | "LOW_QUALITY_SELECTED"
  | "TITLE_INACCURATE"
  | "TITLE_GENERIC"
  | "TITLE_TONE"
  | "TITLE_TOO_LONG"
  | "STORY_FALSE_CLAIM"
  | "STORY_STIFF"
  | "STORY_OVER_INTERPRETED"
  | "STORY_MISSES_KEY_POINT"
  | "STORY_TOO_LONG"
  | "TAG_WRONG"
  | "TAG_MISSING"
  | "TAG_TOO_BROAD"
  | "AHA_NOT_INDEPENDENT"
  | "AHA_WRONG_CORE_ASSET"
  | "AHA_SHOULD_EXIST"
  | "AHA_SHOULD_NOT_EXIST"
  | "ASSET_MISUNDERSTOOD"
  | "ASSET_IMPORTANT_BUT_UNUSED"
  | "ASSET_CORRECTLY_UNUSED"
  | "CROP_LOST_SUBJECT";

export type HumanReviewSuggestionV02 = {
  text: string;
  tags: string[];
  action: HumanReviewAction | null;
};

export type HumanReviewItemV02 = {
  review_id: string;
  target_type: HumanReviewTargetType;
  target_id: string;
  parent_editorial_id: string | null;
  aspect: HumanReviewAspect;
  verdict: HumanReviewVerdict;
  issue_codes: HumanEvaluationIssueCodeV02[];
  /** Public/raw asset UUIDs used by X01Result, never filenames. */
  asset_ids: string[];
  /** Exact frame IDs when feedback is frame-specific; otherwise empty. */
  frame_ids: string[];
  /** Merge destination, related Chapter, or other explicitly linked entity. */
  related_entity_ids: string[];
  suggestion: HumanReviewSuggestionV02;
  notes: string;
};

export type HumanEvaluationGlobalV02 = {
  rating: 0 | 1 | 2 | 3 | 4 | 5;
  verdict: HumanReviewVerdict;
  issue_codes: HumanEvaluationIssueCodeV02[];
  notes: string;
};

export type HumanEvaluationV02 = {
  schema_version: "DIARY_ONE_HUMAN_EVALUATION_V02";
  session_id: string;
  run_id: string;
  evaluation_id: string;
  revision: number;
  bundle_manifest_sha256: string;
  pipeline_version: string;
  request_id: string;
  status: "DRAFT" | "SUBMITTED";
  created_at: string;
  updated_at: string;
  global: HumanEvaluationGlobalV02;
  /** An absent item means unreviewed; PASS is always an explicit judgment. */
  reviews: HumanReviewItemV02[];
};

export const EMPTY_HUMAN_EVALUATION_GLOBAL_V02: HumanEvaluationGlobalV02 = {
  rating: 0,
  verdict: "UNREVIEWED",
  issue_codes: [],
  notes: "",
};

export type ContractFinding = {
  severity: "PASS" | "REVIEW" | "BLOCK";
  code: string;
  message: string;
};
