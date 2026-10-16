import { Asset } from 'expo-asset';
import type { Chapter } from '../model';

const PACK = {
  morning: require('../../assets/motion/sim-morning.mp4'),
  walk: require('../../assets/motion/sim-walk.mp4'),
  river: require('../../assets/motion/sim-river.mp4'),
} as const;

export type MotionClipId = keyof typeof PACK;

/** Seed moment ids that should play bundled motion clips. */
export const MOTION_BY_MOMENT: Record<string, MotionClipId> = {
  m2: 'walk',
  m3: 'morning',
  'm-city-1': 'walk',
  'm-river-1': 'river',
  'm-water-1': 'river',
};

export async function resolveMotionUri(clip: MotionClipId): Promise<string> {
  const asset = Asset.fromModule(PACK[clip]);
  await asset.downloadAsync();
  const uri = asset.localUri ?? asset.uri;
  if (!uri) throw new Error(`motion clip missing: ${clip}`);
  return uri;
}

export async function applyBundledMotion(chapters: Chapter[]): Promise<Chapter[]> {
  const cache = new Map<MotionClipId, string>();
  const next = chapters.map((ch) => ({
    ...ch,
    moments: ch.moments.map((m) => ({ ...m })),
  }));
  for (const ch of next) {
    for (const moment of ch.moments) {
      const clip = MOTION_BY_MOMENT[moment.id];
      if (!clip) continue;
      if (!cache.has(clip)) cache.set(clip, await resolveMotionUri(clip));
      moment.playbackUri = cache.get(clip);
    }
  }
  return next;
}
