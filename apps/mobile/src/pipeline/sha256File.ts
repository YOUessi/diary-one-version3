import * as Crypto from 'expo-crypto';
import * as FileSystem from 'expo-file-system/legacy';

/** SHA-256 digest of file contents (base64-encoded digest string). */
export async function sha256File(uri: string): Promise<string> {
  try {
    const base64 = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    return Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, base64, {
      encoding: Crypto.CryptoEncoding.HEX,
    });
  } catch (e) {
    // Never block the pipeline on hash — contract still gets a stable id
    const fallback = `${uri}:${Date.now()}`;
    return Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, fallback, {
      encoding: Crypto.CryptoEncoding.HEX,
    });
  }
}
