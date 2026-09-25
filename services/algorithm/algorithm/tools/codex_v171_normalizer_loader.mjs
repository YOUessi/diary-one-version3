// Reuse the frozen V1.68 decoder/extractor; change only auditable job metadata.
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const target = pathToFileURL(path.join(root, 'tools/codex_prepare_experience_first_evidence_v1_68.mjs')).href;
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
export async function load(url, context, nextLoad) {
  const loaded = await nextLoad(url, context);
  if (url !== target) return loaded;
  let source = Buffer.from(loaded.source).toString('utf8');
  if (hash(source) !== 'e7795b18537ea94e6e7364fd2fbf9c505fecc7daa5885fea7963e458a55cbe88') throw new Error('Frozen normalizer drift');
  const replacements = [
    ['var/codex_v1_68_experience_first_chapter', 'var/codex_v1_71_full_chain_execution'],
    ["preparation.experiment !== 'CODEX_V1_68_EXPERIENCE_FIRST_CHAPTER'", "preparation.experiment !== 'CODEX_V1_71_FULL_CHAIN'"],
    ["preparation.algorithm_baseline !== 'V1.67'", "preparation.algorithm_baseline !== 'V1.70'"],
    ["candidate.algorithm_baseline !== 'V1.67'", "candidate.algorithm_candidate !== 'V1.71'"],
    ["candidate.algorithm_candidate !== 'V1.68'", "candidate.algorithm_candidate !== 'V1.71'"],
    ['candidate.preparation_sha256 !== hash(fs.readFileSync(preparationPath))', 'preparation.candidate_sha256 !== hash(fs.readFileSync(candidatePath))'],
    ['candidate.normalization_harness_sha256', 'preparation.normalization_harness_sha256'],
    ['candidate.runtime_policies?.chapter_coherence', 'preparation.runtime_policies?.chapter_coherence'],
  ];
  for (const [before, after] of replacements) {
    if (source.split(before).length !== 2) throw new Error('Expected one job-metadata replacement: ' + before);
    source = source.replace(before, after);
  }
  return { ...loaded, source, shortCircuit: true };
}
