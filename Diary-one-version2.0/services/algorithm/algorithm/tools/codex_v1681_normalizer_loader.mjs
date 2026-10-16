// Load the frozen V1.68 normalizer unchanged except for its isolated output area.
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const target = pathToFileURL(path.join(root, 'tools/codex_prepare_experience_first_evidence_v1_68.mjs')).href;
const expectedHash = 'e7795b18537ea94e6e7364fd2fbf9c505fecc7daa5885fea7963e458a55cbe88';
const originalArea = 'var/codex_v1_68_experience_first_chapter';
const revisedArea = 'var/codex_v1_68_1_experience_first_chapter_transport';
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

export async function load(url, context, nextLoad) {
  const loaded = await nextLoad(url, context);
  if (url !== target) return loaded;
  const source = Buffer.from(loaded.source).toString('utf8');
  if (hash(source) !== expectedHash) throw new Error('Frozen V1.68 normalizer drift');
  if (source.split(originalArea).length !== 2 || source.includes(revisedArea)) {
    throw new Error('Expected exactly one isolated-area substitution');
  }
  return {
    ...loaded,
    source: source.replace(originalArea, revisedArea),
    shortCircuit: true,
  };
}
