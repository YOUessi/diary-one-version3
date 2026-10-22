import { Asset } from 'expo-asset';

const PACK = {
  morning: require('../../assets/motion/sim-morning.mp4'),
  walk: require('../../assets/motion/sim-walk.mp4'),
  river: require('../../assets/motion/sim-river.mp4'),
} as const;

export type MotionClipId = keyof typeof PACK;

export async function resolveMotionUri(clip: MotionClipId): Promise<string> {
  const asset = Asset.fromModule(PACK[clip]);
  await asset.downloadAsync();
  const uri = asset.localUri ?? asset.uri;
  if (!uri) throw new Error(`motion clip missing: ${clip}`);
  return uri;
}
