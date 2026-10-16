import * as FileSystem from 'expo-file-system/legacy';
import { appendRnFile, postMultipartArrayBuffer } from '../cloud/rnFormData';
import { resolveProductionBearer } from '../backend/resolveProductionBearer';
import { useAppStore } from '../store/useAppStore';

function baseUrl(): string | null {
  const s = useAppStore.getState();
  const url = s.productionApiBaseUrl.trim() || (process.env.EXPO_PUBLIC_DEV_BFF_URL ?? '').trim();
  return url ? url.replace(/\/+$/, '') : null;
}

function bytesToBase64(bytes: Uint8Array): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let result = '';
  for (let i = 0; i < bytes.length; i += 3) {
    const a = bytes[i]!;
    const hasB = i + 1 < bytes.length;
    const hasC = i + 2 < bytes.length;
    const b = hasB ? bytes[i + 1]! : 0;
    const c = hasC ? bytes[i + 2]! : 0;
    const bitmap = (a << 16) | (b << 8) | c;
    result += chars.charAt((bitmap >> 18) & 63);
    result += chars.charAt((bitmap >> 12) & 63);
    result += hasB ? chars.charAt((bitmap >> 6) & 63) : '=';
    result += hasC ? chars.charAt(bitmap & 63) : '=';
  }
  return result;
}

async function writeJpegBuffer(
  posted: { ok: boolean; status: number; buffer: ArrayBuffer; errorText: string },
  outputUri: string,
): Promise<string> {
  if (!posted.ok) {
    throw new Error(
      `share_compose_failed_${posted.status}${posted.errorText ? `: ${posted.errorText.slice(0, 200)}` : ''}`,
    );
  }
  const dest = outputUri.endsWith('.jpg') ? outputUri : `${outputUri}.jpg`;
  if (!posted.buffer.byteLength) throw new Error('share_compose_empty');
  await FileSystem.writeAsStringAsync(dest, bytesToBase64(new Uint8Array(posted.buffer)), {
    encoding: FileSystem.EncodingType.Base64,
  });
  return dest;
}

/** Multi-tile collage via PC BFF (Pillow) — Expo Go safe. */
export async function composeCollageViaBff(imageUris: string[], outputUri: string): Promise<string> {
  const api = baseUrl();
  if (!api) throw new Error('bff_url_required');
  if (!imageUris.length) throw new Error('no_images');

  const form = new FormData();
  const count = Math.min(imageUris.length, 4);
  form.append('image_count', String(count));
  for (let i = 0; i < count; i++) {
    appendRnFile(form, `image_${i}`, imageUris[i]!, `image_${i}.jpg`);
  }

  const posted = await postMultipartArrayBuffer(`${api}/v1/share/collage/render`, form, {
    Accept: 'image/jpeg',
    Authorization: `Bearer ${resolveProductionBearer()}`,
  });
  return writeJpegBuffer(posted, outputUri);
}

/** Illustrated style A/B/C via PC BFF (Pillow) — Expo Go safe. */
export async function composeIllustratedViaBff(
  imageUri: string,
  style: 'A' | 'B' | 'C',
  outputUri: string,
  title?: string,
): Promise<string> {
  const api = baseUrl();
  if (!api) throw new Error('bff_url_required');

  const form = new FormData();
  form.append('style', style);
  if (title) form.append('title', title.slice(0, 42));
  appendRnFile(form, 'image_0', imageUri, 'image_0.jpg');

  const posted = await postMultipartArrayBuffer(`${api}/v1/share/illustrated/render`, form, {
    Accept: 'image/jpeg',
    Authorization: `Bearer ${resolveProductionBearer()}`,
  });
  return writeJpegBuffer(posted, outputUri);
}
