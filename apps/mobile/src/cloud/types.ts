/** 与 eval-web `X01Editorial` / X02 preview 对齐的最小 App 侧类型（仅消费展示字段）。 */

export type PreviewSelectedMedia = {
  asset_id: string;
  source_asset_id?: string;
  role?: 'HERO' | 'SUPPORT' | 'CORE' | string;
  media_kind?: string;
  evidence_frame_ids?: string[];
  representative_frame_id?: string;
  start_ms?: number | null;
  end_ms?: number | null;
  range_basis?: string;
  focus_pts_ms?: number | null;
  source_sequence_index?: number;
};

export type PreviewChapter = {
  id: string;
  title: string;
  time_label: string;
  story: string;
  preview_story?: string;
  highlights?: { id: string; parent_chapter_id: string; story: string; selected_media?: PreviewSelectedMedia[] }[];
  tags: string[];
  moment_ids: string[];
  /** Cloud cover asset — resolve to local bundle frame URI. */
  hero_asset_id?: string;
  hero_frame_id?: string;
  /** Cloud Moments strip — ordered selected evidence. */
  selected_media?: PreviewSelectedMedia[];
  publication_status: string;
};

export type PreviewAha = {
  id: string;
  story: string;
  publication_status: string;
  selected_media?: PreviewSelectedMedia[];
};

export type PreviewMemoryOutcome = {
  memory_type: 'CHAPTER' | 'AHA';
  memory_id: string;
  visibility_state: 'VISIBLE_PREVIEW' | 'DIAGNOSTIC_ONLY';
};

export type PublishAdmission = {
  publish_admit: boolean;
  input_bound?: boolean;
  result_contract_version?: string;
  result_contract_sha256?: string;
  session_id?: string;
  bundle_manifest_sha256?: string;
  admit_reason?: string;
  fail_job?: boolean;
  delivery_state?: string;
  pipeline_version?: string;
  schema_version?: string;
  bundle_version?: string;
  production_ready?: boolean;
  is_mock_fallback?: boolean;
};

export type X02PreviewResult = {
  _publish?: PublishAdmission;
  schema_version: string;
  chapters: PreviewChapter[];
  ahas: PreviewAha[];
  selected_memory_outcomes: PreviewMemoryOutcome[];
  semantic_day_state?: string;
  delivery_state?: string;
  coverage_status?: string;
  /** Dev Lite: true when mock preview substituted for empty/failed X02. */
  dev_lite_fallback?: boolean;
};

export type ResearchHealth = {
  status: string;
  schemaVersion?: string;
  pipelineVersion?: string;
  previewPath?: string;
  runSidecarPath?: string;
  modelReady?: boolean;
  supportedAppLibraryBundleVersions?: string[];
};
