import type { PersistedSnapshot } from '../db/sqlite';
import { exportSnapshotJson } from '../domain/exportLocalData';
import { resetLocalAppData } from '../store/hydrate';
import type { PrivacyExportPayload } from './types';

export async function exportLocalDataService(snapshot: PersistedSnapshot): Promise<void> {
  await exportSnapshotJson(snapshot);
}

export function buildExportPayload(snapshot: PersistedSnapshot): PrivacyExportPayload {
  return {
    exportedAt: new Date().toISOString(),
    schema: 'DIARY_ONE_LOCAL_EXPORT_V1',
    snapshot,
  };
}

export async function wipeLocalDataService(): Promise<void> {
  await resetLocalAppData();
}
