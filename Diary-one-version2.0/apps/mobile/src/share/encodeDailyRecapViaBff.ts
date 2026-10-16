import * as FileSystem from 'expo-file-system/legacy';
import { resolveProductionBearer } from '../backend/resolveProductionBearer';
import { appendRnFile, postMultipartArrayBuffer } from '../cloud/rnFormData';
import { useAppStore } from '../store/useAppStore';
import { RECAP_FPS, RECAP_SLIDE_DURATION_SEC } from './dailyRecapConstants';

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

/** Dev Lite / BFF with ffmpeg — works in Expo Go (LAN). */
export async function encodeDailyRecapViaBff(
  slideUris: string[],
  outputUri: string,
): Promise<string> {
  const api = baseUrl();
  if (!api) throw new Error('bff_url_required');

  const form = new FormData();
  form.append('slide_count', String(slideUris.length));
  form.append('fps', String(RECAP_FPS));
  form.append('slide_duration_sec', String(RECAP_SLIDE_DURATION_SEC));

  for (let index = 0; index < slideUris.length; index += 1) {
    appendRnFile(form, `slide_${index}`, slideUris[index]!, `slide_${index}.jpg`);
  }

  const posted = await postMultipartArrayBuffer(`${api}/v1/share/daily-recap/render`, form, {
    Accept: 'video/mp4',
    Authorization: `Bearer ${resolveProductionBearer()}`,
  });

  if (!posted.ok) {
    const text = posted.errorText;
    if (posted.status === 503 || /ffmpeg/i.test(text)) {
      throw new Error('ffmpeg_not_installed');
    }
    throw new Error(`recap_render_failed_${posted.status}${text ? `: ${text.slice(0, 200)}` : ''}`);
  }

  const dest = outputUri.endsWith('.mp4') ? outputUri : `${outputUri}.mp4`;
  if (!posted.buffer.byteLength) {
    throw new Error('recap_empty_mp4');
  }
  const base64 = bytesToBase64(new Uint8Array(posted.buffer));
  await FileSystem.writeAsStringAsync(dest, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });
  return dest;
}
