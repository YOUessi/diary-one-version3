/**
 * Expo SDK 57 `fetch` cannot send RN file parts (`{ uri, name, type }`) and
 * Expo Go Blob cannot be constructed from ArrayBuffer / Uint8Array.
 * Multipart uploads must use XMLHttpRequest + RN FormData file objects.
 */
export function asFileUri(uri: string): string {
  const trimmed = uri.trim();
  if (!trimmed) return trimmed;
  if (
    trimmed.startsWith('file://') ||
    trimmed.startsWith('content://') ||
    trimmed.startsWith('ph://') ||
    trimmed.startsWith('asset:') ||
    trimmed.startsWith('http://') ||
    trimmed.startsWith('https://')
  ) {
    return trimmed;
  }
  return `file://${trimmed}`;
}

export function mimeFromName(filename: string): string {
  const lower = filename.toLowerCase();
  if (lower.endsWith('.png')) return 'image/png';
  if (lower.endsWith('.webp')) return 'image/webp';
  if (lower.endsWith('.json')) return 'application/json';
  if (lower.endsWith('.mp4')) return 'video/mp4';
  return 'image/jpeg';
}

type RnFilePart = { uri: string; name: string; type: string };

export function appendRnFile(
  form: FormData,
  field: string,
  uri: string,
  filename: string,
  mime?: string,
): void {
  const part: RnFilePart = {
    uri: asFileUri(uri),
    name: filename,
    type: mime ?? mimeFromName(filename),
  };
  form.append(field, part as unknown as Blob);
}

type XhrCtor = new () => XMLHttpRequest;

function createXhr(): XMLHttpRequest {
  const g = globalThis as typeof globalThis & { originalXMLHttpRequest?: XhrCtor };
  const Ctor = g.originalXMLHttpRequest ?? XMLHttpRequest;
  return new Ctor();
}

function applyHeaders(xhr: XMLHttpRequest, headers: Record<string, string>): void {
  for (const [key, value] of Object.entries(headers)) {
    if (key.toLowerCase() === 'content-type') continue;
    xhr.setRequestHeader(key, value);
  }
}

export function postMultipartText(
  url: string,
  form: FormData,
  headers: Record<string, string>,
  timeoutMs = 15 * 60 * 1000,
): Promise<{ ok: boolean; status: number; text: string }> {
  return new Promise((resolve, reject) => {
    const xhr = createXhr();
    xhr.open('POST', url);
    xhr.timeout = timeoutMs;
    xhr.responseType = 'text';
    applyHeaders(xhr, headers);
    xhr.onload = () => {
      resolve({
        ok: xhr.status >= 200 && xhr.status < 300,
        status: xhr.status,
        text: String(xhr.responseText ?? ''),
      });
    };
    xhr.onerror = () => reject(new Error(`Network error posting ${url}`));
    xhr.ontimeout = () => reject(new Error('Upload timed out'));
    xhr.send(form);
  });
}

export function postMultipartArrayBuffer(
  url: string,
  form: FormData,
  headers: Record<string, string>,
  timeoutMs = 15 * 60 * 1000,
): Promise<{ ok: boolean; status: number; buffer: ArrayBuffer; errorText: string }> {
  return new Promise((resolve, reject) => {
    const xhr = createXhr();
    xhr.open('POST', url);
    xhr.timeout = timeoutMs;
    xhr.responseType = 'arraybuffer';
    applyHeaders(xhr, headers);
    xhr.onload = () => {
      const ok = xhr.status >= 200 && xhr.status < 300;
      const raw = xhr.response;
      const buffer = raw instanceof ArrayBuffer ? raw : new ArrayBuffer(0);
      let errorText = '';
      if (!ok) {
        try {
          errorText = new TextDecoder().decode(new Uint8Array(buffer));
        } catch {
          errorText = xhr.statusText ?? '';
        }
      }
      resolve({ ok, status: xhr.status, buffer, errorText });
    };
    xhr.onerror = () => reject(new Error(`Network error posting ${url}`));
    xhr.ontimeout = () => reject(new Error('Upload timed out'));
    xhr.send(form);
  });
}
