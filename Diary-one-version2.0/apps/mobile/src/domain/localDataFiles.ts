import * as FileSystem from 'expo-file-system/legacy';

/** Delete only app-owned data, never user-selected files in the system photo library. */
export async function clearLocalMediaFiles(): Promise<void> {
  const documents = FileSystem.documentDirectory;
  if (documents) {
    await FileSystem.deleteAsync(`${documents}bundles/`, { idempotent: true });
    await FileSystem.deleteAsync(`${documents}profile/`, { idempotent: true });
  }
  const cache = FileSystem.cacheDirectory;
  if (!cache) return;
  const names = await FileSystem.readDirectoryAsync(cache);
  const prefixes = ['diary-one-export-', 'intake-', 'collage_', 'illustrated_',
    'day_collage_', 'daily_recap_', 'recap_frames_'];
  for (const name of names) {
    if (!name.includes('/') && !name.includes('\\') &&
        (name === 'ImagePicker' || prefixes.some((prefix) => name.startsWith(prefix)))) {
      await FileSystem.deleteAsync(`${cache}${name}`, { idempotent: true });
    }
  }
}
