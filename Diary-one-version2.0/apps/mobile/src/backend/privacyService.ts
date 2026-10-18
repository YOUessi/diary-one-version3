import { setLocalCleanupPending, type PersistedSnapshot } from '../db/sqlite';
import { exportSnapshotJson } from '../domain/exportLocalData';
import { resetLocalAppData } from '../store/hydrate';
import type { PrivacyExportPayload } from './types';
import { buildUserDataExport } from '../domain/dataExport';
import { useAppStore } from '../store/useAppStore';

export async function exportLocalDataService(snapshot: PersistedSnapshot): Promise<void> {
  await exportSnapshotJson(snapshot);
}

export function buildExportPayload(snapshot: PersistedSnapshot): PrivacyExportPayload {
  return {
    exportedAt: new Date().toISOString(),
    schema: 'DIARY_ONE_LOCAL_EXPORT_V1',
    snapshot: buildUserDataExport(snapshot),
  };
}

export async function wipeLocalDataService(): Promise<void> {
  await setLocalCleanupPending(true);
  await resetLocalAppData();
}

export async function deleteAccountAndDataService(): Promise<void> {
  const { sessionToken, productionApiBaseUrl } = useAppStore.getState();
  if (!sessionToken || !productionApiBaseUrl.trim()) throw new Error('Sign in to delete your cloud account and data.');
  const response = await fetch(`${productionApiBaseUrl.replace(/\/+$/, '')}/v1/account`, {
    method: 'DELETE', headers: { Authorization: `Bearer ${sessionToken}` },
  });
  if (!response.ok) {
    if (response.status === 409) throw new Error('Wait for your cloud processing to finish, then try deletion again.');
    if (response.status === 404) throw new Error('Account deletion requires the updated backend. Your local data has not been cleared.');
    throw new Error(`Account deletion failed (${response.status}). Please try again.`);
  }
  const result = await response.json() as { deleted?: boolean };
  if (result.deleted !== true) throw new Error('Cloud deletion was not confirmed. Your local data has not been cleared.');
  if (useAppStore.getState().sessionToken !== sessionToken) throw new Error('Account changed during deletion.');
  await setLocalCleanupPending(true);
  try {
    await resetLocalAppData();
  } catch {
    throw new Error('Cloud deletion was confirmed. Local cleanup is incomplete; restart Diary One to resume cleanup.');
  }
}
