import { requireNativeModule } from 'expo-modules-core';

export type DiaryOneVisionResult = {
  modelId: string;
  vectors: number[][];
  classifications: { identifier: string; confidence: number }[][];
};

export type DiaryOneExtractedFrame = {
  uri: string;
  requestedMs: number;
  actualPtsMs: number;
};

const DiaryOneVision = requireNativeModule<{
  isAvailable?: boolean;
  analyzeImages(uris: string[]): Promise<DiaryOneVisionResult>;
  extractVideoFrames(
    videoUri: string,
    timestampsMs: number[],
    destDir: string,
  ): Promise<DiaryOneExtractedFrame[]>;
}>('DiaryOneVision');

export async function analyzeImages(uris: string[]): Promise<DiaryOneVisionResult> {
  return DiaryOneVision.analyzeImages(uris);
}

export async function extractVideoFrames(
  videoUri: string,
  timestampsMs: number[],
  destDir: string,
): Promise<DiaryOneExtractedFrame[]> {
  return DiaryOneVision.extractVideoFrames(videoUri, timestampsMs, destDir);
}

export default DiaryOneVision;
