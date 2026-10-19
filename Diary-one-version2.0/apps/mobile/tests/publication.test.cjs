const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const Module = require('node:module');
const crypto = require('node:crypto');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'),
  { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, filename);
const originalLoad = Module._load;
Module._load = function(name, ...args) {
  if (name === 'expo-file-system/legacy') return {};
  if (name === 'expo-crypto') return { CryptoDigestAlgorithm: { SHA1: 'sha1' },
    digest: async (algorithm, bytes) => Uint8Array.from(crypto.createHash(algorithm).update(bytes).digest()).buffer };
  if (name === '../config/buildProfile') return { isFormalConsumerApp: true, isLabToolsEnabled: false };
  return originalLoad.call(this, name, ...args);
};
const { applyChapterMediaHints } = require('../src/pipeline/attachChapterMedia.ts');
const { validatePreviewResult } = require('../src/cloud/validatePreviewResult.ts');
Module._load = originalLoad;
const { ALGORITHM_LOCK } = require('../src/config/algorithmLock.ts');
const fixture = JSON.parse(fs.readFileSync('../../services/bff/tests/fixtures/synthetic_qwen38_result.json', 'utf8'));
const manifest = { bundle_version: ALGORITHM_LOCK.bundleV04, session: { session_id: fixture.session_id },
  assets: [{ asset_id: 'asset-0', media_kind: 'PHOTO', frames: [{ frame_id: 'asset-0-f0', sha256: '0'.repeat(64) }] }] };
function result() {
  const value = structuredClone(fixture);
  value._publish = { ...value._publish, input_bound: true,
    result_contract_version: ALGORITHM_LOCK.resultContractVersion, session_id: fixture.session_id,
    result_contract_sha256: ALGORITHM_LOCK.previewContractSha256, bundle_version: ALGORITHM_LOCK.bundleV04 };
  return value;
}
const input = { manifest, manifestSha256: fixture.bundle_manifest_sha256 };
test('consumer validates input binding, media lineage and complete visible sets independently', async () => {
  assert.equal((await validatePreviewResult(result(), input)).ok, true);
  assert.equal((await validatePreviewResult(result())).ok, false);
  for (const mutate of [
    r => { r.bundle_manifest_sha256 = 'bad'; },
    r => { r._publish.input_bound = false; },
    r => { r._publish.result_contract_sha256 = 'old-schema'; },
    r => { r.ahas[0].selected_media[0].asset_id = 'unknown'; },
    r => { r.ahas[0].selected_media[0].evidence_frame_ids = ['unknown-frame']; },
    r => { r.selected_memory_outcomes = []; },
    r => { r.ahas[0].story = 12; },
    r => { r.delivery_state = 'NO_GROUNDED_MEMORY'; },
  ]) {
    const value = result(); mutate(value);
    assert.equal((await validatePreviewResult(value, input)).ok, false);
  }
});
test('hero uses its exact selected frame and unknown frames fail instead of falling back', () => {
  const chapter = { id: 'ch', moments: [] };
  const index = new Map([['a', { uris: ['file:///first.jpg', 'file:///chosen.jpg'], frameIds: ['f0', 'f1'] }]]);
  const hints = { ch: { heroAssetId: 'a', momentIds: [],
    selectedMedia: [{ role: 'HERO', asset_id: 'a', evidence_frame_ids: ['f1'] }] } };
  assert.equal(applyChapterMediaHints([chapter], hints, index)[0].heroUri, 'file:///chosen.jpg');
  hints.ch.selectedMedia[0].evidence_frame_ids = ['missing'];
  assert.throws(() => applyChapterMediaHints([chapter], hints, index), /missing/);
});
