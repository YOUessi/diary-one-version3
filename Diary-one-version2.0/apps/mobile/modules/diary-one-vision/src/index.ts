import { requireNativeModule } from 'expo-modules-core';

export type DiaryOneExtractedFrame = {
  uri: string;
  requestedMs: number;
  actualPtsMs: number;
  decodeTimeMs?: number;
};

const DiaryOneVision = requireNativeModule<{
  isAvailable?: boolean;
  normalizeEvidenceFrame(sourceUri: string, destUri: string): Promise<void>;
  extractVideoWindowFrames(
    videoUri: string,
    timestampsMs: number[],
    destDir: string,
    bounds: [number, number],
  ): Promise<DiaryOneExtractedFrame[]>;
  extractVideoFrames(
    videoUri: string,
    timestampsMs: number[],
    destDir: string,
  ): Promise<DiaryOneExtractedFrame[]>;
}>('DiaryOneVision');

export async function extractVideoFrames(
  videoUri: string,
  timestampsMs: number[],
  destDir: string,
): Promise<DiaryOneExtractedFrame[]> {
  return DiaryOneVision.extractVideoFrames(videoUri, timestampsMs, destDir);
}

export default DiaryOneVision;
