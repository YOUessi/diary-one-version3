import * as FileSystem from 'expo-file-system/legacy';
import type { PersistedSnapshot } from '../db/sqlite';

const PREFIX = 'diary-documents://';
function managed(relative: string): boolean {
  return /^bundles\/bundle-[\w-]+\/(?:[\w.-]+\/)*[\w.-]*$/.test(relative)
    && relative.split('/').every(part => part !== '.' && part !== '..');
}
function oldRoot(uri?: string): string | undefined {
  return uri?.match(/^(file:\/\/[^?#%]*\/Containers\/Data\/Application\/[a-f0-9-]{36}\/Documents\/)bundles\/bundle-[\w-]+\/$/i)?.[1];
}
export function persistAppMediaUri(uri?: string): string | undefined {
  const root = FileSystem.documentDirectory;
  if (uri && root && uri.startsWith(root) && managed(uri.slice(root.length))) {
    return PREFIX + uri.slice(root.length);
  }
  return uri;
}
export function resolveAppMediaUri(uri?: string, roots: string[] = []): string | undefined {
  if (!uri) return uri;
  if (uri.startsWith(PREFIX)) {
    const relative = uri.slice(PREFIX.length);
    if (!managed(relative) || !FileSystem.documentDirectory) throw new Error('Invalid saved media path');
    return FileSystem.documentDirectory + relative;
  }
  for (const root of roots) {
    if (oldRoot(root + 'bundles/bundle-check/') !== root) continue;
    if (uri.startsWith(root) && managed(uri.slice(root.length)) && FileSystem.documentDirectory) {
      return FileSystem.documentDirectory + uri.slice(root.length);
    }
  }
  return uri;
}

/** Legacy source sidecar may contain its former container. Only the exact same
 * managed bundle is eligible; attachment must still verify the original SHA. */
export function resolveBundleSourceUri(uri: string, bundleDir: string): string {
  const root = FileSystem.documentDirectory;
  if (!root || !bundleDir.startsWith(root)) return uri;
  const relative = bundleDir.slice(root.length);
  if (!managed(relative)) return uri;
  const marker = uri.indexOf('/Documents/' + relative);
  if (marker < 0) return resolveAppMediaUri(uri)!;
  const previous = uri.slice(0, marker + '/Documents/'.length);
  return resolveAppMediaUri(uri, [previous])!;
}

function mapSnapshot(snapshot: PersistedSnapshot, map: (uri?: string) => string | undefined): PersistedSnapshot {
  const media = <T extends { heroUri?: string; posterUri?: string; playbackUri?: string }>(item: T): T => ({
    ...item,
    ...(item.heroUri !== undefined ? { heroUri: map(item.heroUri) } : {}),
    ...(item.posterUri !== undefined ? { posterUri: map(item.posterUri) } : {}),
    ...(item.playbackUri !== undefined ? { playbackUri: map(item.playbackUri) } : {}),
  });
  return { ...snapshot,
    chapters: snapshot.chapters.map(chapter => ({ ...media(chapter), moments: chapter.moments?.map(media) })),
    capturedOriginals: (snapshot.capturedOriginals ?? []).map(media),
    pipelineTasks: snapshot.pipelineTasks?.map(task => ({ ...task,
      bundleDir: map(task.bundleDir), bundleJsonPath: map(task.bundleJsonPath) })),
    pipelineAssetLedger: snapshot.pipelineAssetLedger?.map(row => ({ ...row, bundleJsonPath: map(row.bundleJsonPath) })),
  };
}
export function persistSnapshotMediaPaths(snapshot: PersistedSnapshot): PersistedSnapshot {
  return mapSnapshot(snapshot, persistAppMediaUri);
}
export function restoreSnapshotMediaPaths(snapshot: PersistedSnapshot): PersistedSnapshot {
  const roots = (snapshot.pipelineTasks ?? []).map(task => oldRoot(task.bundleDir))
    .filter((root): root is string => Boolean(root));
  return mapSnapshot(snapshot, uri => resolveAppMediaUri(uri, roots));
}
