import { requireOptionalNativeModule } from 'expo-modules-core';
import type { SemanticAnalyzer, SemanticAnalyzeResult } from './semanticAnalyzer';

type NativeVisionPayload = {
  modelId: string;
  vectors: number[][];
  classifications: Array<Array<{ identifier: string; confidence: number }>>;
};

const NativeDiaryOneVision = requireOptionalNativeModule<{
  analyzeImages: (uris: string[]) => Promise<NativeVisionPayload>;
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

export type { SemanticAnalyzeResult };
