import { Asset } from 'expo-asset';
import * as FileSystem from 'expo-file-system/legacy';
import jpeg from 'jpeg-js';
import type * as ORT from 'onnxruntime-react-native';
import manifest from '../../../assets/models/mobileclip-s0-fp16/manifest.json';
import { sha256File } from '../../pipeline/sha256File';
import { normalizeVector } from '../similarity';
import type { SemanticAnalyzeResult } from '../semanticAnalyzer';
import { pixelQuality, preprocess } from './pixels';
import { createSessionLifecycle, throwIfAnalysisCancelled } from './sessionLifecycle';

export const MODEL_ID = manifest.model_id;
export const MODEL_SHA256 = manifest.files['image_encoder.onnx'].sha256;
export const PROMPT_SHA256 = manifest.files['prompts.f32.bin'].sha256;
export { BALANCED_V07_SAMPLING_PROFILE as SAMPLING_PROFILE } from '../videoWindows';
export type Analysis = SemanticAnalyzeResult & { fullClassifications: NonNullable<SemanticAnalyzeResult['classifications']>; quality: ReturnType<typeof pixelQuality> };

function bytesFromBase64(encoded: string): Uint8Array {
  const binary = globalThis.atob(encoded);
  return Uint8Array.from(binary, c => c.charCodeAt(0));
}

async function assetPath(module: number, expectedHash: string) {
  const asset = Asset.fromModule(module);
  await asset.downloadAsync();
  if (!asset.localUri || await sha256File(asset.localUri) !== expectedHash) throw new Error('MobileCLIP 模型文件校验失败，请重新安装应用。');
  return asset.localUri;
}

type ModelResource = { ort: typeof ORT; session: ORT.InferenceSession; prompts: Float32Array };
async function loadModel() {
  let ort: typeof ORT;
  try {
    // Keep native loading lazy: Expo Go may open the UI, but cannot run this model.
    ort = require('onnxruntime-react-native');
  } catch {
    throw new Error('MobileCLIP 需要重新构建并安装开发版或 TestFlight App，Expo Go 不支持端上模型。');
  }
  const model = await assetPath(require('../../../assets/models/mobileclip-s0-fp16/image_encoder.onnx'), MODEL_SHA256);
  const promptFile = await assetPath(require('../../../assets/models/mobileclip-s0-fp16/prompts.f32.bin'), PROMPT_SHA256);
  const promptBytes = bytesFromBase64(await FileSystem.readAsStringAsync(promptFile, { encoding: FileSystem.EncodingType.Base64 }));
  const view = new DataView(promptBytes.buffer);
  const prompts = new Float32Array(manifest.labels.length * manifest.embedding_dim);
  if (promptBytes.length !== prompts.length * 4) throw new Error('MobileCLIP prompt shape mismatch');
  for (let i = 0; i < prompts.length; i++) prompts[i] = view.getFloat32(i * 4, true);
  // CPU first for reproducibility. FP16 refers to model internals, not every runtime op.
  const session = await ort.InferenceSession.create(decodeURIComponent(model.replace(/^file:\/\//, '')), {
    executionProviders: ['cpu'], intraOpNumThreads: 2, interOpNumThreads: 1,
  });
  return { ort, session, prompts };
}

// Fast Refresh may reevaluate this module without replacing Hermes. Preserve
// both the queue and session in that runtime so old and new callers cannot
// start independent native sessions. A full reload creates a fresh global.
const runtime = globalThis as typeof globalThis & {
  __diaryOneMobileClipRuntimeV1?: { identity: string; lifecycle: ReturnType<typeof createSessionLifecycle<ModelResource>> };
};
const identity = `${MODEL_SHA256}:${PROMPT_SHA256}`;
const cached = runtime.__diaryOneMobileClipRuntimeV1;
if (cached && cached.identity !== identity) throw new Error('MobileCLIP assets changed; restart the app to load the verified model.');
const lifecycle = cached?.lifecycle ?? createSessionLifecycle<ModelResource>();
runtime.__diaryOneMobileClipRuntimeV1 = { identity, lifecycle };

export function releaseMobileClip(): Promise<void> {
  return lifecycle.release();
}

export function analyzeMobileClip(uris: string[], options: { signal?: AbortSignal; assertCurrent?: () => void } = {}): Promise<Analysis[]> {
  if (!uris.length) return Promise.resolve([]);
  const assertCurrent = () => { throwIfAnalysisCancelled(options.signal); options.assertCurrent?.(); };
  return lifecycle.run(loadModel, async ({ ort, session, prompts }) => {
    assertCurrent();
    if (session.inputNames[0] !== 'image' || session.outputNames[0] !== 'embedding') throw new Error('Unexpected MobileCLIP model contract');
    const results: Analysis[] = [];
    for (const uri of uris) {
      assertCurrent();
      const bytes = bytesFromBase64(await FileSystem.readAsStringAsync(uri, { encoding: FileSystem.EncodingType.Base64 }));
      assertCurrent();
      const pixels = jpeg.decode(bytes, { useTArray: true, formatAsRGBA: true, maxResolutionInMP: 20, maxMemoryUsageInMB: 128 });
      const tensor = new ort.Tensor('float32', preprocess(pixels), [1, 3, 256, 256]);
      let outputs: ORT.InferenceSession.OnnxValueMapType | undefined;
      try {
        outputs = await session.run({ image: tensor });
        const raw = outputs.embedding;
        if (!raw || raw.type !== 'float32' || raw.data.length !== 512) throw new Error('MobileCLIP embedding shape mismatch');
        if (!Array.from(raw.data as Float32Array).every(Number.isFinite)) throw new Error('MobileCLIP embedding contains invalid values');
        assertCurrent();
        const vector = normalizeVector(Array.from(raw.data as Float32Array));
        const logits = manifest.labels.map((_, label) => {
          let dot = 0;
          for (let i = 0; i < 512; i++) dot += prompts[label * 512 + i] * vector[i];
          return dot * manifest.logit_scale;
        });
        const max = Math.max(...logits), exp = logits.map(v => Math.exp(Math.max(-80, v - max)));
        const total = exp.reduce((a, b) => a + b, 0);
        const fullClassifications = manifest.labels.map((identifier, i) => ({ identifier, confidence: exp[i] / total }))
          .sort((a, b) => b.confidence - a.confidence);
        results.push({ vector, classifications: fullClassifications.slice(0, 3), fullClassifications,
          modelId: MODEL_ID, degraded: false, quality: pixelQuality(pixels) });
      } finally {
        tensor.dispose();
        if (outputs) Object.values(outputs).forEach(value => value.dispose());
      }
      // Yield between images so progress/cancellation UI can paint.
      await new Promise<void>(resolve => setTimeout(resolve, 0));
    }
    return results;
  }, options.signal);
}
