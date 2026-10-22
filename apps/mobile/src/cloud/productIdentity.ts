import * as Crypto from 'expo-crypto';

/** UUIDv5 wire identity, using the existing Expo crypto implementation (not a hash reimplementation). */
export async function productMemoryIdentities(result: unknown, sessionId: string): Promise<Record<string, string>> {
  const out: Record<string, string> = {};
  const value = result as { editor_policy?: string; decision_trace?: { selected_structure?: { chapters?: { id: string }[]; moments?: { id: string; parent_chapter_id: string | null }[] } } };
  if (!value?.editor_policy || !value.decision_trace?.selected_structure) return out;
  const hex = sessionId.replace(/-/g, '');
  if (!/^[0-9a-f]{32}$/i.test(hex)) throw new Error('Invalid product session UUID');
  const entries = [
    ...(value.decision_trace.selected_structure.chapters ?? []).map(item => `chapter:${item.id}`),
    ...(value.decision_trace.selected_structure.moments ?? []).map(item => `${item.parent_chapter_id === null ? 'aha' : 'highlight'}:${item.id}`),
  ];
  for (const entry of entries) {
    const name = new TextEncoder().encode(`${value.editor_policy}:${entry}`);
    const bytes = new Uint8Array(16 + name.length);
    for (let i = 0; i < 16; i++) bytes[i] = Number.parseInt(hex.slice(i * 2, i * 2 + 2), 16);
    bytes.set(name, 16);
    const hash = new Uint8Array(await Crypto.digest(Crypto.CryptoDigestAlgorithm.SHA1, bytes));
    hash[6] = (hash[6] & 0x0f) | 0x50; hash[8] = (hash[8] & 0x3f) | 0x80;
    const id = Array.from(hash.slice(0, 16), n => n.toString(16).padStart(2, '0')).join('');
    out[entry] = `${id.slice(0, 8)}-${id.slice(8, 12)}-${id.slice(12, 16)}-${id.slice(16, 20)}-${id.slice(20)}`;
  }
  return out;
}
