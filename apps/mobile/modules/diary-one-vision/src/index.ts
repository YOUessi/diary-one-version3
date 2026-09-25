import { requireNativeModule } from 'expo-modules-core';

export type DiaryOneVisionResult = {
  modelId: string;
  vectors: number[][];
  classifications: Array<Array<{ identifier: string; confidence: number }>>;
};

const DiaryOneVision = requireNativeModule<{
  analyzeImages(uris: string[]): Promise<DiaryOneVisionResult>;
}>('DiaryOneVision');

export async function analyzeImages(uris: string[]): Promise<DiaryOneVisionResult> {
  return DiaryOneVision.analyzeImages(uris);
}

export default DiaryOneVision;
