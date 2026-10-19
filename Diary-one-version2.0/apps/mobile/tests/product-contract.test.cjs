// Actual cloud mapping/binding and remote SQLite. Historical output replay, no model calls.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const Module = require('node:module');
const { DatabaseSync } = require('node:sqlite');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'),
  { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText, filename);
const db = new DatabaseSync(':memory:');
const sql = { execAsync: async q => db.exec(q), getFirstAsync: async (q, ...a) => db.prepare(q).get(...a),
  getAllAsync: async (q, ...a) => db.prepare(q).all(...a), runAsync: async (q, ...a) => db.prepare(q).run(...a) };
const oldLoad = Module._load;
Module._load = function(name, ...args) {
  if (name === 'expo-file-system') return { File: class {
    constructor(uri) { this.uri = uri; }
    async bytes() { return fs.readFileSync(new URL(this.uri)); }
  } };
  if (name === 'expo-crypto') return { CryptoDigestAlgorithm: { SHA1: 'sha1', SHA256: 'sha256' },
    digest: async (algo, bytes) => Uint8Array.from(crypto.createHash(algo).update(bytes).digest()).buffer };
  if (name === 'expo-file-system/legacy') return {
    EncodingType: { Base64: 'base64' },
    readAsStringAsync: async (uri, options) => fs.readFileSync(new URL(uri), options?.encoding ?? 'utf8'),
    getInfoAsync: async uri => ({ exists: fs.existsSync(new URL(uri)) }),
  };
  if (name === 'expo-sqlite') return { openDatabaseAsync: async () => sql };
  if (name === '../config/buildProfile') return { isFormalConsumerApp: true, isLabToolsEnabled: false };
  return oldLoad.call(this, name, ...args);
};
const validator = require('../src/cloud/validatePreviewResult.ts');
const mapper = require('../src/cloud/mapPreviewResult.ts');
const media = require('../src/pipeline/attachChapterMedia.ts');
const sqlite = require('../src/db/sqlite.ts');
const { ALGORITHM_LOCK: lock } = require('../src/config/algorithmLock.ts');
Module._load = oldLoad;
test.after(() => db.close());
const fixtures = path.resolve(__dirname, '../../../services/bff/tests/fixtures/product_contract');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function fixture(name = 'photo_v07') {
  const raw = fs.readFileSync(path.join(fixtures, name + '-manifest.json'));
  const manifest = JSON.parse(raw), result = JSON.parse(fs.readFileSync(path.join(fixtures, name + '-result.json')));
  const input = { manifest, manifestSha256: sha(raw) };
  assert.equal(result.bundle_manifest_sha256, input.manifestSha256, 'preserved fixture must bind its exact manifest bytes');
  result._publish = { publish_admit: true, input_bound: true, fail_job: false, is_mock_fallback: false,
    result_contract_version: lock.resultContractVersion, result_contract_sha256: lock.resultContractSha256[result.schema_version],
    bundle_manifest_sha256: input.manifestSha256, session_id: result.session_id,
    bundle_version: manifest.bundle_version, schema_version: result.schema_version, delivery_state: result.delivery_state };
  return { result, input };
}
for (const [name, chapterCount, ahaCount] of [['nagoya_r52', 1, 0], ['zoo_r52', 3, 0], ['rural_r55', 0, 2], ['photo_v07', 1, 0]]) {
  test(`historical ${name} output passes actual App binding and preserves Chapter/Aha mapping`, async () => {
    const { result, input } = fixture(name), frozen = JSON.stringify(result);
    const check = await validator.validatePreviewResult(result, input); assert.equal(check.ok, true, check.reason);
    const mapped = mapper.mapPreviewToDiary(result, '2026-10-19');
    assert.equal(mapped.chapters.length, chapterCount); assert.equal(mapped.smallMemories.length, ahaCount);
    mapped.chapters.forEach((c, i) => {
      assert.equal(c.aiStory, result.chapters[i].story); assert.equal(c.previewStory, result.chapters[i].preview_story);
      assert.deepEqual(c.highlights, result.chapters[i].highlights.map(h => ({ id: h.id, text: h.story })));
    });
    mapped.smallMemories.forEach((m, i) => assert.equal(m.text, result.ahas[i].story));
    assert.equal(JSON.stringify(result), frozen);
  });
}

test('wrong public/source/frame/claim/structure identities fail independently of a trusted-looking envelope', async () => {
  for (const patch of [
    r => { r._publish.result_contract_sha256 = lock.previewContractSha256; },
    r => { r.session_id = r._publish.session_id = '11111111-1111-4111-8111-111111111111'; },
    r => { r.chapters[0].id = 'foreign'; },
    r => { r.chapters[0].selected_media[0].asset_id = 'foreign'; },
    r => { r.chapters[0].selected_media[0].source_asset_id = 'foreign'; },
    r => { r.chapters[0].hero_frame_id = 'foreign'; },
    r => { r.chapters[0].selected_media[0].representative_frame_id = 'foreign'; },
    r => { r.chapters[0].claims[0].text = 'invented'; },
    r => { r.chapters[0].highlights[0].parent_chapter_id = 'foreign'; },
    r => { r.decision_trace.selected_structure.chapters[0].fact_ids = ['F999']; },
    r => { r.selected_memory_outcomes = []; },
  ]) {
    const { result, input } = fixture(); patch(result);
    assert.equal((await validator.validatePreviewResult(result, input)).ok, false);
  }
});

test('exact representative and hero images use source aliases without changing raw source playback', async t => {
  const { result, input } = fixture('nagoya_r52');
  assert.equal((await validator.validatePreviewResult(result, input)).ok, true);
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'diary-product-map-')); t.after(() => fs.rmSync(folder, { force: true, recursive: true }));
  const bundleDir = `file://${folder}/`, sourceUris = {};
  // Attachment-only synthetic bytes. The historical input binding assertion
  // above retains its untouched fixture; this is not a real-media E2E test.
  const attachmentManifest = structuredClone(input.manifest);
  for (const asset of attachmentManifest.assets) {
    for (const frame of asset.frames) { const file = path.join(folder, frame.relative_path); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, 'existence fixture only'); frame.sha256 = sha(fs.readFileSync(file)); }
    sourceUris[asset.asset_id] = { uri: `file://${folder}/${asset.asset_id}.mp4`, media_kind: asset.media_kind };
    fs.writeFileSync(new URL(sourceUris[asset.asset_id].uri), 'source existence fixture only');
    asset.original_sha256 = sha(fs.readFileSync(new URL(sourceUris[asset.asset_id].uri)));
  }
  fs.writeFileSync(path.join(folder, 'bundle.json'), JSON.stringify(attachmentManifest));
  fs.writeFileSync(path.join(folder, 'source_uris.json'), JSON.stringify(sourceUris));
  const mapped = mapper.mapPreviewToDiary(result, '2026-10-19');
  const attached = await media.attachChapterMediaFromBundle(mapped.chapters, result.chapters, bundleDir, bundleDir + 'bundle.json');
  const cloud = result.chapters[0], hero = cloud.selected_media.find(m => m.role === 'HERO');
  const asset = input.manifest.assets.find(a => a.asset_id === hero.source_asset_id);
  assert.equal(attached[0].heroUri, bundleDir + asset.frames.find(f => f.frame_id === cloud.hero_frame_id).relative_path);
  cloud.selected_media.forEach((m, i) => {
    const a = input.manifest.assets.find(a => a.asset_id === m.source_asset_id);
    assert.equal(attached[0].moments[i].posterUri, bundleDir + a.frames.find(f => f.frame_id === m.representative_frame_id).relative_path);
    assert.equal(attached[0].moments[i].playbackUri, sourceUris[m.source_asset_id].uri);
  });
  // Existing remote behavior remains: a missing source cannot be silently substituted.
  fs.unlinkSync(new URL(sourceUris[hero.source_asset_id].uri));
  await assert.rejects(media.attachChapterMediaFromBundle(mapped.chapters, result.chapters, bundleDir, bundleDir + 'bundle.json'), /unavailable/);
});

test('Product metadata and Aha text survive SQLite save/load with relative media paths', async () => {
  await sqlite.initDatabase();
  const chapter = fixture(), aha = fixture('rural_r55');
  const mapped = mapper.mapPreviewToDiary(chapter.result, '2026-10-19');
  const memories = mapper.mapPreviewToDiary(aha.result, '2026-10-19').smallMemories;
  await sqlite.saveSnapshot({ ...sqlite.emptySnapshot(), chapters: mapped.chapters, smallMemoriesByDate: { '2026-10-19': memories } });
  const restored = await sqlite.loadSnapshot();
  assert.deepEqual(restored.chapters, JSON.parse(JSON.stringify(mapped.chapters)));
  assert.deepEqual(restored.smallMemoriesByDate['2026-10-19'], memories);
  assert.equal(restored.chapters[0].highlights[0].text, chapter.result.chapters[0].highlights[0].story);
});
