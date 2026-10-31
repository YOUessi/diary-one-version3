/** Final Chapter Motion materialization; NEVER export unselected source clips.

 * V05 is opt-in until the updated native app/server are deployed. Each cover
 * references a verified frame/10s local original. Export failures retain a
 * precise in-app 3-second source-window fallback; they are not falsely called
 * saved Apple Live Photos.
 */
import * as FileSystem from 'expo-file-system/legacy';
import * as Crypto from 'expo-crypto';
import { requireOptionalNativeModule } from 'expo';
import type { Chapter, ChapterMotionCover, MemoryMedia } from '../model';

type ExportResponse = {
  videoUri: string;
  stillUri: string;
  startMs: number;
  endMs: number;
  focusMs: number;
  clipDurationMs: number;
  isApplePhotosPaired: false;
};

const native = requireOptionalNativeModule<{
  exportChapterMotion(
    videoUri: string, destDir: string, assetKey: string,
    focusMs: number, durationMs: number,
  ): Promise<ExportResponse>;
}>('DiaryOneVision');

export function motionRange(focusTimeSec: number, sourceDurationSec: number, durationSec = 3) {
  if (!Number.isFinite(focusTimeSec) || !Number.isFinite(sourceDurationSec)
      || sourceDurationSec < durationSec || durationSec <= 0
      || focusTimeSec < 0 || focusTimeSec >= sourceDurationSec) {
    throw new Error('Motion range requires a valid keyframe from the local original');
  }
  const start = Math.max(0, Math.min(focusTimeSec - durationSec / 2, sourceDurationSec - durationSec));
  return { start, end: start + durationSec };
}

async function materializeOne(item: MemoryMedia, destination: string): Promise<MemoryMedia> {
  const uri = item.playbackUri;
  const poster = item.posterUri;
  const focus = item.focusTimeSec;
  const length = item.sourceDurationSec;
  if (!(uri && poster && typeof focus === 'number' && typeof length === 'number'
        && item.sourceAssetId && item.selectedFrameId && uri.startsWith('file://'))) {
    return item; // PHOTO asset is valid but cannot be made into real motion.
  }
  const { start, end } = motionRange(focus, length);
  let cover: ChapterMotionCover = {
    kind:'chapter_motion', status:'source_window',
    posterUri:poster,motionUri:uri,sourceVideoUri:uri,
    focusTimeSec:focus,clipStartSec:start,clipEndSec:end,
    applePhotosPaired:false,
  };
  if (native?.exportChapterMotion) {
    try {
      const key = await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256,
        [item.sourceAssetId,item.selectedFrameId,focus.toFixed(6),'chapter-motion-v01'].join('|'));
      const output = await native.exportChapterMotion(uri,destination,key,focus * 1000,3000);
      const file = await FileSystem.getInfoAsync(output.videoUri);
      const still = await FileSystem.getInfoAsync(output.stillUri);
      if (!file.exists || file.isDirectory || !still.exists || still.isDirectory
          || output.isApplePhotosPaired !== false ||
          Math.abs(output.focusMs - focus * 1000) > 100 ||
          Math.abs(output.endMs - output.startMs - 3000) > 60) {
        throw new Error('Native motion export verification failed');
      }
      cover = { ...cover,status:'rendered',posterUri:output.stillUri,
        motionUri:output.videoUri,
        clipStartSec:0,clipEndSec:3,focusTimeSec:(output.focusMs - output.startMs)/1000 };
    } catch {
      // A real source-window is still available; this is not an Apple Photos asset.
      // Do not modify the original or claim the MOV is exported.
    }
  }
  return { ...item, motionCover:cover };
}

/** Materialize ONLY final Chapter-selected images, never all candidate evidence. */
export async function buildLiveChapterCovers(chapters: Chapter[], bundleDir: string): Promise<Chapter[]> {
  const output = bundleDir + 'chapter-motion/';
  await FileSystem.makeDirectoryAsync(output,{intermediates:true});
  const result: Chapter[] = [];
  for (const chapter of chapters) {
    const moments: MemoryMedia[] = [];
    for (const item of chapter.moments) {
      moments.push(await materializeOne(item,output));
    }
    const highlights = chapter.highlights
      ? await Promise.all(chapter.highlights.map(async highlight => ({
          ...highlight,
          media: highlight.media
            ? await Promise.all(highlight.media.map(item => materializeOne(item, output)))
            : undefined,
        })))
      : undefined;
    const hero = moments.find(m => m.posterUri === chapter.heroUri);
    result.push({
      ...chapter, moments, ...(highlights ? { highlights } : {}),
      motionCover:hero?.motionCover,
    });
  }
  return result;
}
