import * as FileSystem from 'expo-file-system/legacy';

/** Copy content:// (Android) or ph:// URIs into cache so ImageManipulator / SHA can read them. */
export async function ensureLocalFileUri(uri: string, label = 'asset'): Promise<string> {
  if (uri.startsWith('file://') || uri.startsWith('/')) {
    return uri.startsWith('/') ? `file://${uri}` : uri;
  }
  const root = FileSystem.cacheDirectory;
  if (!root) throw new Error('cacheDirectory unavailable');
  const safe = label.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 24) || 'asset';
  const dest = `${root}intake-${Date.now()}-${safe}`;
  try {
    await FileSystem.copyAsync({ from: uri, to: dest });
  } catch (e) {
    throw new Error(
      `Cannot copy media into app cache (${e instanceof Error ? e.message : String(e)}). ` +
        'On Expo Go Android, try the Demo photo button if the system picker fails.',
    );
  }
  return dest;
}
