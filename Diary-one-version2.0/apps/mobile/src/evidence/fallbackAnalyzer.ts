import * as FileSystem from 'expo-file-system/legacy';
import type { SemanticAnalyzer } from './semanticAnalyzer';
import { normalizeVector } from './similarity';

const FALLBACK_MODEL_ID = 'EXPO_GO_BRIGHTNESS_HISTOGRAM_V01';

function histogramVector(bytes: Uint8Array, dims = 768): number[] {
  const bins = new Array(16).fill(0);
  let sum = 0;
  let count = 0;
  for (let i = 0; i < bytes.length; i++) {
    sum += bytes[i];
    bins[Math.min(15, Math.floor(bytes[i] / 16))] += 1;
    count += 1;
    if (count > 8000) break;
  }
  const mean = count ? sum / count / 255 : 0.5;
  const out = new Array(dims).fill(0);
  for (let i = 0; i < 16; i++) out[i] = bins[i] / Math.max(1, count);
  for (let i = 16; i < dims; i++) {
    out[i] = mean * Math.sin(i * 0.17 + bytes[i % bytes.length] * 0.01);
  }
  return normalizeVector(out);
}

/** Expo Go only — not Apple Vision quality. */
export function createFallbackSemanticAnalyzer(): SemanticAnalyzer {
  return {
    kind: 'fallback_expo_go',
    degraded: true,
    async analyzeImageUri(uri) {
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      const binary = globalThis.atob?.(base64) ?? '';
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      return {
        vector: histogramVector(bytes),
        classifications: [],
        degraded: true,
        modelId: FALLBACK_MODEL_ID,
      };
    },
  };
}
