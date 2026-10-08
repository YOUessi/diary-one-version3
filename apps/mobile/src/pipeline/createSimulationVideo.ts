import * as FileSystem from 'expo-file-system/legacy';
import { resolveMotionUri } from '../assets/motionAssets';
import type { PickedMedia } from './types';

export async function createSimulationPickedVideo(): Promise<PickedMedia> {
  const src = await resolveMotionUri('morning');
  const root = FileSystem.cacheDirectory;
  if (!root) throw new Error('cacheDirectory unavailable');
  const dest = `${root}sim-video-${Date.now()}.mp4`;
  await FileSystem.copyAsync({ from: src, to: dest });
  const info = await FileSystem.getInfoAsync(dest);
  return {
    uri: dest,
    mediaType: 'video',
    width: 720,
    height: 406,
    fileSize: info.exists ? info.size : undefined,
    durationMs: 8000,
    fileName: 'simulation-morning.mp4',
  };
}
