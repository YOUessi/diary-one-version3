/** 端侧素材处理任务（Sync 与 Cloud Processing 分开表达）。 */
export type PipelineTaskStatus =
  | 'queued'
  | 'building_evidence'
  | 'bundle_ready'
  | 'uploading'
  | 'cloud_processing'
  | 'succeeded'
  | 'failed';

export type PipelineTask = {
  id: string;
  createdAt: string;
  dayKey: string;
  dayRevisionId: string;
  intakeSource: 'PHOTO_LIBRARY_TEST';
  status: PipelineTaskStatus;
  message: string;
  sourceCount: number;
  bundleDir?: string;
  bundleJsonPath?: string;
  bundleVersion?: string;
  error?: string;
};

export type PickedMedia = {
  uri: string;
  mediaType: 'image' | 'video' | 'unknown';
  width?: number;
  height?: number;
  fileSize?: number;
  durationMs?: number;
  fileName?: string;
};
