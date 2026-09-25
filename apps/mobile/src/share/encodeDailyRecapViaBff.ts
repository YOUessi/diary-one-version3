import * as FileSystem from 'expo-file-system/legacy';
import { resolveProductionBearer } from '../backend/resolveProductionBearer';
import { useAppStore } from '../store/useAppStore';
import { RECAP_FPS, RECAP_SLIDE_DURATION_SEC } from './dailyRecapConstants';

function baseUrl(): string | null {
  const s = useAppStore.getState();
  const url = s.productionApiBaseUrl.trim() || (process.env.EXPO_PUBLIC_DEV_BFF_URL ?? '').trim();
  return url ? url.replace(/\/+$/, '') : null;
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

  slideUris.forEach((uri, index) => {
    form.append(`slide_${index}`, {
      uri,
      name: `slide_${index}.jpg`,
      type: 'image/jpeg',
    } as unknown as Blob);
  });

  const res = await fetch(`${api}/v1/share/daily-recap/render`, {
    method: 'POST',
    headers: {
      Accept: 'video/mp4',
      Authorization: `Bearer ${resolveProductionBearer()}`,
    },
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`recap_render_failed_${res.status}${text ? `: ${text.slice(0, 200)}` : ''}`);
  }

  const dest = outputUri.endsWith('.mp4') ? outputUri : `${outputUri}.mp4`;
  const blob = await res.blob();
  const base64 = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('recap_blob_read_failed'));
    reader.onloadend = () => {
      const result = reader.result;
      if (typeof result !== 'string' || !result.includes(',')) {
        reject(new Error('recap_blob_invalid'));
        return;
      }
      resolve(result.split(',')[1] ?? '');
    };
    reader.readAsDataURL(blob);
  });
  await FileSystem.writeAsStringAsync(dest, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });
  return dest;
}
