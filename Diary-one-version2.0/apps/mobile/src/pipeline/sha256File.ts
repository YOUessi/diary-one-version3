import * as Crypto from 'expo-crypto';
import * as FileSystem from 'expo-file-system/legacy';

/** Multipart sends compact JSON, rather than the pretty-printed local bundle file. */
export async function sha256SubmittedManifest(manifest: unknown): Promise<string> {
  return Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, JSON.stringify(manifest));
}

function base64ToUint8Array(base64: string): Uint8Array {
  const atobFn = globalThis.atob;
  if (!atobFn) {
    throw new Error('Cannot decode file bytes (missing atob)');
  }
  const binary = atobFn(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function arrayBufferToHex(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let hex = '';
  for (let i = 0; i < bytes.length; i += 1) {
    hex += bytes[i]!.toString(16).padStart(2, '0');
  }
  return hex;
}

/** SHA-256 of the file's raw bytes (must match X02 `sha256_file`). */
export async function sha256File(uri: string): Promise<string> {
  const base64 = await FileSystem.readAsStringAsync(uri, {
    encoding: FileSystem.EncodingType.Base64,
  });
  const bytes = base64ToUint8Array(base64);
  // Copy into a concrete ArrayBuffer so Crypto.digest accepts BufferSource under strict TS.
  const ab = new ArrayBuffer(bytes.byteLength);
  new Uint8Array(ab).set(bytes);
  const digest = await Crypto.digest(Crypto.CryptoDigestAlgorithm.SHA256, ab);
  return arrayBufferToHex(digest);
}
