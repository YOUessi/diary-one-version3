import * as Crypto from 'expo-crypto';
import { File } from 'expo-file-system';

/** Multipart sends compact JSON, rather than the pretty-printed local bundle file. */
export async function sha256SubmittedManifest(manifest: unknown): Promise<string> {
  return Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, JSON.stringify(manifest));
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
  // Native byte reads avoid a large Base64 string and synchronous JS decoding
  // when hashing videos or the model. The digest still covers every raw byte.
  const bytes = await new File(uri).bytes();
  const digest = await Crypto.digest(Crypto.CryptoDigestAlgorithm.SHA256, bytes);
  return arrayBufferToHex(digest);
}
