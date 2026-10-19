const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
const plain = value => JSON.parse(JSON.stringify(value));
function load(file, stubs) {
  const module = { exports: {} };
  const code = ts.transpileModule(fs.readFileSync(path.join(root, file), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, require(name) {
    if (Object.hasOwn(stubs, name)) return stubs[name];
    if (name.startsWith('.')) return load(path.join(path.dirname(file), name + '.ts'), stubs);
    throw Error('Unmocked dependency ' + name);
  } }, { filename: file });
  return module.exports;
}
function harness(hooks = {}) {
  const calls = { copies: [], semantic: [], normalized: [], writes: [] };
  const api = load('src/pipeline/buildAppLibraryBundle.ts', {
    'expo-file-system/legacy': {
      makeDirectoryAsync: async () => {},
      copyAsync: async args => calls.copies.push(args),
      writeAsStringAsync: async (uri, text) => calls.writes.push({ uri, value: JSON.parse(text) }),
    },
    'expo-crypto': { randomUUID: () => 'session-test' },
    './sha256File': { sha256File: async () => 'a'.repeat(64) },
    './ensureLocalFileUri': { ensureLocalFileUri: async uri => uri },
    './evidenceNormalize': {
      EVIDENCE_FRAME: { width: 768, height: 1024 },
      writeNormalizedFrame: async (...args) => calls.normalized.push(args),
    },
    '../evidence/runSemanticVideoEvidence': { buildSemanticVideoEvidence: async args => {
      calls.semantic.push(args); await hooks.semantic?.(args);
      return { frames: [{ frame_id: 'real-frame', source_timestamp_ms: 16, window_index: 0, window_count: 12 }],
        evidence_window_count: 12, evidence_sampling_profile: 'MOBILECLIP_S0_FP16_COVERAGE_V07_BALANCED_V1' };
    } },
  });
  return { calls, run: (items, fence = () => {}, version = 'V04') => api.buildAppLibraryBundle(items, 'file:///documents/bundle/', version, fence) };
}
const video = { uri: 'file:///picker/source.mov', mediaType: 'video', fileName: 'ride.mov', durationMs: 120000,
  width: 1920, height: 1080, fileSize: 9001, creationTimeMs: 123456789,
  captureDayKey: '2026-10-18', captureTimeRaw: '2026:10:18 08:30:00', captureTimeSource: 'EXIF_OFFSET', captureUtcOffset: '+08:00', confirmedDayKey: '2026-10-18' };
test('main durable original and capture metadata survive the algorithm-only video replacement', async () => {
  const h = harness(); const fence = () => {}; const { bundle, sourceUris } = await h.run([video], fence);
  assert.deepEqual(plain(h.calls.copies), [{ from: video.uri, to: 'file:///documents/bundle/sources/asset-0.mov' }]);
  assert.equal(h.calls.semantic[0].localVideoUri, sourceUris['asset-0'].uri);
  assert.equal(h.calls.semantic[0].assertCurrent, fence);
  for (const field of ['creationTimeMs', 'durationMs', 'captureDayKey', 'captureTimeRaw', 'captureTimeSource', 'captureUtcOffset', 'confirmedDayKey']) assert.equal(sourceUris['asset-0'][field], video[field], field);
  assert.equal(bundle.assets[0].evidence_window_count, 12);
  assert.equal(bundle.assets[0].frames[0].source_timestamp_ms, 16);
  assert.equal(bundle.assets[0].original_included, false);
  assert.equal(bundle.assets[0].original_duration_ms, 120000);
  assert.equal(bundle.assets[0].evidence_sampling_profile, 'MOBILECLIP_S0_FP16_COVERAGE_V07_BALANCED_V1');
  assert.equal(h.calls.normalized.length, 0, 'selected real probe files are reused by the algorithm');
  assert.equal(h.calls.writes.length, 2);
});
for (const error of ['native decode failed', 'ONNX inference failed']) test(`${error} is propagated without synthetic thumbnail fallback or bundle publication`, async () => {
  const h = harness({ semantic: () => { throw Error(error); } });
  await assert.rejects(h.run([video]), new RegExp(error));
  assert.equal(h.calls.normalized.length, 0); assert.equal(h.calls.writes.length, 0);
});
test('missing/invalid video duration is rejected instead of inventing a 9s timeline', async () => {
  for (const durationMs of [undefined, 0, -1, NaN, Infinity]) {
    const h = harness(); await assert.rejects(h.run([{ ...video, durationMs }]), /duration/);
    assert.equal(h.calls.semantic.length, 0); assert.equal(h.calls.writes.length, 0);
  }
});
test('main owner fence change during inference prevents both manifest and source-map publication', async () => {
  let current = true;
  const h = harness({ semantic: args => { assert.equal(typeof args.assertCurrent, 'function'); current = false; } });
  await assert.rejects(h.run([video], () => { if (!current) throw Error('owner changed'); }), /owner changed/);
  assert.equal(h.calls.writes.length, 0);
});
test('main photo path keeps its durable original, capture metadata and V03 support', async () => {
  const photo = { ...video, uri: 'file:///picker/photo.jpg', fileName: 'photo.jpg', mediaType: 'image', durationMs: undefined };
  const h = harness(); const result = await h.run([photo], undefined, 'V03');
  assert.equal(h.calls.semantic.length, 0); assert.equal(h.calls.normalized.length, 1);
  assert.equal(result.bundle.assets[0].frames[0].source_timestamp_ms, null);
  assert.equal(result.bundle.assets[0].evidence_sampling_profile, 'PHOTO_SINGLE_FRAME');
  assert.equal(result.bundle.assets[0].frames[0].spatial_transform, 'CENTER_CROP_ASPECT_FILL');
  assert.equal(result.sourceUris['asset-0'].captureDayKey, photo.captureDayKey);
  assert.equal(result.sourceUris['asset-0'].uri, 'file:///documents/bundle/sources/asset-0.jpg');
});
