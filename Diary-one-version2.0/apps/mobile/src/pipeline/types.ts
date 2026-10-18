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
  /** Stable local provenance even if the remote revision is renewed after a conflict. */
  sourceBatchId?: string;
  /** BFF job id — persisted so REL01 can resume poll without a new billed task. */
  productionJobId?: string;
  intakeSource: import('../domain/mediaIntake').MediaIntakeSource;
  status: PipelineTaskStatus;
  message: string;
  sourceCount: number;
  bundleDir?: string;
  bundleJsonPath?: string;
  bundleVersion?: string;
  error?: string;
  /** True when dayKey came from capture EXIF/creationTime (IMP02). */
  dayKeyFromCapture?: boolean;
};

export type PickedMedia = {
  uri: string;
  mediaType: 'image' | 'video' | 'unknown';
  width?: number;
  height?: number;
  fileSize?: number;
  durationMs?: number;
  fileName?: string;
  /** Capture time from EXIF / asset metadata (ms). Missing = unknown (IMP02). */
  creationTimeMs?: number;
  /** Original calendar date, preserved without shifting it to the device timezone. */
  captureDayKey?: string;
  captureTimeSource?: 'EXIF_OFFSET' | 'EXIF_LOCAL' | 'ASSET_TIMESTAMP' | 'UNKNOWN';
  captureTimeRaw?: string;
  captureUtcOffset?: string;
  /** Explicit user decision for missing capture dates; never inferred from import time. */
  confirmedDayKey?: string;
};
