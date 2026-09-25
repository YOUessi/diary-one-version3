import { Platform } from 'react-native';
import * as FileSystem from 'expo-file-system/legacy';
import { encodeVideo, mixAudio } from 'expo-video-encoder';
import {
  RECAP_FPS,
  RECAP_HEIGHT,
  RECAP_SLIDE_DURATION_SEC,
  RECAP_WIDTH,
} from './dailyRecapConstants';

function stripFileScheme(path: string): string {
  return path.replace(/^file:\/\//, '');
}

async function copyFrame(sourceUri: string, destPath: string): Promise<void> {
  const base = await FileSystem.readAsStringAsync(sourceUri, {
    encoding: FileSystem.EncodingType.Base64,
  });
  await FileSystem.writeAsStringAsync(destPath, base, {
    encoding: FileSystem.EncodingType.Base64,
  });
}

/** iOS Dev Client / production — AVFoundation H.264 MP4. */
export async function encodeDailyRecapNative(
  slideUris: string[],
  outputUri: string,
  audioUri?: string,
): Promise<string> {
  if (Platform.OS !== 'ios') {
    throw new Error('native_encoder_ios_only');
  }
  const framesDir = `${FileSystem.cacheDirectory}recap_frames_${Date.now()}/`;
  await FileSystem.makeDirectoryAsync(framesDir, { intermediates: true });

  const framesPerSlide = Math.max(1, Math.round(RECAP_FPS * RECAP_SLIDE_DURATION_SEC));
  let frameIndex = 0;
  for (const slide of slideUris) {
    for (let i = 0; i < framesPerSlide; i += 1) {
      const name = `frame_${String(frameIndex).padStart(6, '0')}.jpg`;
      await copyFrame(slide, `${framesDir}${name}`);
      frameIndex += 1;
    }
  }

  const silentPath = outputUri.endsWith('.mp4') ? outputUri : `${outputUri}.mp4`;
  await FileSystem.deleteAsync(silentPath, { idempotent: true });

  await encodeVideo({
    framesDir: stripFileScheme(framesDir),
    frameCount: frameIndex,
    fps: RECAP_FPS,
    width: RECAP_WIDTH,
    height: RECAP_HEIGHT,
    outputPath: stripFileScheme(silentPath),
  });

  if (audioUri && audioUri.startsWith('file://')) {
    const mixedPath = silentPath.replace(/\.mp4$/i, '_mixed.mp4');
    const totalDurationMs = Math.round(
      (frameIndex / RECAP_FPS) * 1000,
    );
    try {
      await mixAudio({
        videoPath: stripFileScheme(silentPath),
        outputPath: stripFileScheme(mixedPath),
        totalDurationMs,
        audioTracks: [
          {
            uri: stripFileScheme(audioUri),
            startMs: 0,
            durationMs: totalDurationMs,
            volume: 1,
          },
        ],
      });
      await FileSystem.deleteAsync(silentPath, { idempotent: true });
      return mixedPath.startsWith('file://') ? mixedPath : `file://${mixedPath}`;
    } catch {
      return silentPath.startsWith('file://') ? silentPath : `file://${silentPath}`;
    }
  }

  return silentPath.startsWith('file://') ? silentPath : `file://${silentPath}`;
}
