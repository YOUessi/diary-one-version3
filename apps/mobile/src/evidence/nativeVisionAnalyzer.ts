import * as FileSystem from 'expo-file-system/legacy';
import * as VideoThumbnails from 'expo-video-thumbnails';
import { requireOptionalNativeModule } from 'expo-modules-core';
import type { SemanticAnalyzer, SemanticAnalyzeResult } from './semanticAnalyzer';

type NativeVisionPayload = {
  modelId: string;
  vectors: number[][];
  classifications: Array<Array<{ identifier: string; confidence: number }>>;
};

export type ExtractedVideoFrame = {
  uri: string;
  requestedMs: number;
  actualPtsMs: number;
};

const NativeDiaryOneVision = requireOptionalNativeModule<{
  isAvailable?: boolean;
  analyzeImages: (uris: string[]) => Promise<NativeVisionPayload>;
  extractVideoFrames: (
    videoUri: string,
    timestampsMs: number[],
    destDir: string,
  ) => Promise<ExtractedVideoFrame[]>;
}>('DiaryOneVision');

export function isNativeVisionAvailable(): boolean {
  return Boolean(NativeDiaryOneVision?.analyzeImages);
}

export function createNativeVisionAnalyzer(): SemanticAnalyzer | null {
  if (!isNativeVisionAvailable()) return null;
  return {
    kind: 'native_vision',
    degraded: false,
    async analyzeImageUri(uri: string) {
      const batch = await this.analyzeImageUris!([uri]);
      return batch[0];
    },
    async analyzeImageUris(uris: string[]) {
      const payload = await NativeDiaryOneVision!.analyzeImages(uris);
      return payload.vectors.map((vector, index) => ({
        vector,
        classifications: payload.classifications[index] ?? [],
        modelId: payload.modelId,
        degraded: false,
      }));
    },
  };
}

/** AVFoundation timestamps on TestFlight/Dev Client; Expo thumbnails on Expo Go. */
export async function extractVideoFramesAtTimes(
  videoUri: string,
  timestampsMs: number[],
  destDir: string,
): Promise<ExtractedVideoFrame[]> {
  if (NativeDiaryOneVision?.extractVideoFrames) {
    await FileSystem.makeDirectoryAsync(destDir, { intermediates: true });
    return NativeDiaryOneVision.extractVideoFrames(videoUri, timestampsMs, destDir);
  }
  const rows: ExtractedVideoFrame[] = [];
  for (const requestedMs of timestampsMs) {
    const thumb = await VideoThumbnails.getThumbnailAsync(videoUri, {
      time: Math.max(0, requestedMs),
      quality: 0.85,
    });
    rows.push({
      uri: thumb.uri,
      requestedMs,
      actualPtsMs: requestedMs,
    });
  }
  return rows;
}

export type { SemanticAnalyzeResult };
