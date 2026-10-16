import * as ImageManipulator from 'expo-image-manipulator';
import type { SemanticRoutingProfile } from './types';

export type ProbeQualityMetrics = {
  meanLuma: number;
  darkPixelRatio: number;
  sharpness: number;
  eligibleForSelection: boolean;
  qualityReasonCodes: string[];
};

function decodeBase64ToBytes(base64: string): Uint8Array {
  const atobFn = globalThis.atob;
  if (!atobFn) {
    return new Uint8Array();
  }
  const binary = atobFn(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

/** Rough luma / variance proxy from a tiny PNG (no OpenCV on device). */
export async function measureProbeQualityFromUri(
  uri: string,
  profile: Pick<
    SemanticRoutingProfile,
    'blankMeanLumaMax' | 'blankDarkPixelRatioMin' | 'blankSharpnessMax'
  >,
): Promise<ProbeQualityMetrics> {
  const manipulated = await ImageManipulator.manipulateAsync(
    uri,
    [{ resize: { width: 48, height: 48 } }],
    { compress: 1, format: ImageManipulator.SaveFormat.PNG, base64: true },
  );
  const bytes = decodeBase64ToBytes(manipulated.base64 ?? '');
  let sum = 0;
  let dark = 0;
  let count = 0;
  const samples: number[] = [];
  for (let i = 0; i + 3 < bytes.length; i += 4) {
    const r = bytes[i];
    const g = bytes[i + 1];
    const b = bytes[i + 2];
    const luma = 0.299 * r + 0.587 * g + 0.114 * b;
    sum += luma;
    if (luma <= 32) dark += 1;
    samples.push(luma);
    count += 1;
    if (count >= 400) break;
  }
  if (!count) {
    return {
      meanLuma: 128,
      darkPixelRatio: 0,
      sharpness: 50,
      eligibleForSelection: true,
      qualityReasonCodes: [],
    };
  }
  const meanLuma = sum / count;
  const darkPixelRatio = dark / count;
  let variance = 0;
  for (const s of samples) variance += (s - meanLuma) ** 2;
  variance /= samples.length;
  const sharpness = variance * 4;
  const blank =
    meanLuma <= profile.blankMeanLumaMax &&
    darkPixelRatio >= profile.blankDarkPixelRatioMin &&
    sharpness <= profile.blankSharpnessMax;
  return {
    meanLuma,
    darkPixelRatio,
    sharpness,
    eligibleForSelection: !blank,
    qualityReasonCodes: blank ? ['BLANK_OR_BLACK_FRAME'] : [],
  };
}
