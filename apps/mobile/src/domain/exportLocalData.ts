import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import type { PersistedSnapshot } from '../db/sqlite';

export async function exportSnapshotJson(snapshot: PersistedSnapshot): Promise<void> {
  const root = FileSystem.cacheDirectory;
  if (!root) throw new Error('Cache unavailable');
  const path = `${root}diary-one-export-${Date.now()}.json`;
  const payload = {
    exported_at: new Date().toISOString(),
    schema: 'DIARY_ONE_LOCAL_EXPORT_V1',
    snapshot,
  };
  await FileSystem.writeAsStringAsync(path, JSON.stringify(payload, null, 2));
  const canShare = await Sharing.isAvailableAsync();
  if (!canShare) {
    throw new Error('Sharing is not available on this device.');
  }
  await Sharing.shareAsync(path, {
    mimeType: 'application/json',
    dialogTitle: 'Export Diary One data',
  });
}
