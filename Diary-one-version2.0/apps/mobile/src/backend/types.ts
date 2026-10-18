import type { TodayStatus } from '../model';
import type { X02PreviewResult } from '../cloud/types';

export type CloudProcessingTarget = 'research' | 'production';

export type DeviceSyncOutcome =
  | { ok: true; lastSyncedAt: string }
  | { ok: false; reason: 'not_connected' | 'nothing_to_sync' | 'cancelled' | 'sync_failed'; detail?: string };

export type AuthOutcome =
  | { ok: true }
  | { ok: false; reason: 'invalid_code' | 'not_available' };

export type CloudJobPoll =
  | { state: 'pending'; message?: string }
  | { state: 'succeeded'; result: X02PreviewResult }
  | { state: 'failed'; message: string };

export type BackendHealth = {
  research: { configured: boolean; reachable: boolean; detail?: string };
  production: { configured: boolean; reachable: boolean; detail?: string };
  device: { linked: boolean };
  account: { email?: string; mode: 'local' | 'email_verified' };
};

export type PrivacyExportPayload = {
  exportedAt: string;
  schema: 'DIARY_ONE_LOCAL_EXPORT_V1';
  snapshot: ReturnType<typeof import('../domain/dataExport').buildUserDataExport>;
};

export type ApplyPreviewOutcome = {
  todayStatus: TodayStatus;
  chapterCount: number;
  smallMemoryCount: number;
};
