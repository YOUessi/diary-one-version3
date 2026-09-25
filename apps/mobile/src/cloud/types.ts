/** 与 eval-web `X01Result` 对齐的最小 App 侧类型（仅消费展示字段）。 */
export type PreviewChapter = {
  id: string;
  title: string;
  time_label: string;
  story: string;
  tags: string[];
  moment_ids: string[];
  publication_status: string;
};

export type PreviewAha = {
  id: string;
  story: string;
  publication_status: string;
};

export type PreviewMemoryOutcome = {
  memory_type: 'CHAPTER' | 'AHA';
  memory_id: string;
  visibility_state: 'VISIBLE_PREVIEW' | 'DIAGNOSTIC_ONLY';
};

export type X02PreviewResult = {
  schema_version: string;
  chapters: PreviewChapter[];
  ahas: PreviewAha[];
  selected_memory_outcomes: PreviewMemoryOutcome[];
  semantic_day_state?: string;
  delivery_state?: string;
  coverage_status?: string;
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
