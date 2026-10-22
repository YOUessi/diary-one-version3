const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
function load(file, stubs = {}) {
  const module = { exports: {} };
  const code = ts.transpileModule(fs.readFileSync(path.join(root, file), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, require(name) {
    if (Object.hasOwn(stubs, name)) return stubs[name];
    if (name.startsWith('.')) return load(path.join(path.dirname(file), name + '.ts'), stubs);
    throw new Error('Unmocked dependency: ' + name);
  } }, { filename: file });
  return module.exports;
}
const windows = load('src/evidence/videoWindows.ts');
test('all supported durations partition completely into bounded nonempty windows, including 10ms tails', () => {
  for (let duration = 1; duration <= 120000; duration++) {
    const ranges = windows.balancedVideoWindows(duration);
    assert.equal(ranges.length, Math.ceil(duration / 10000));
    assert.equal(ranges[0].startMs, 0); assert.equal(ranges.at(-1).endMs, duration);
    ranges.forEach((r, i) => {
      assert.ok(r.endMs > r.startMs && r.endMs - r.startMs <= 10000);
      if (i) assert.equal(r.startMs, ranges[i - 1].endMs);
    });
  }
  assert.deepEqual(JSON.parse(JSON.stringify(windows.balancedVideoWindows(10010))), [
    { startMs: 0, endMs: 5005 }, { startMs: 5005, endMs: 10010 },
  ]);
  for (const invalid of [0, -1, NaN, Infinity, 10000.5, 120001]) assert.throws(() => windows.balancedVideoWindows(invalid));
});
function harness(mode = 'valid', hooks = {}) {
  const calls = { decode: [], analyze: [], analysisOptions: [], normalize: [], hashes: [], writes: [], deleted: [], published: [] };
  const mod = load('src/evidence/runSemanticVideoEvidence.ts', {
    'expo-file-system/legacy': {
      writeAsStringAsync: async (...args) => { calls.writes.push(args); await hooks.write?.(); },
      deleteAsync: async uri => calls.deleted.push(uri),
    },
    './nativeVideoDecoder': {
      extractVideoFramesAtTimes: async (_uri, requested, _dir, bounds) => {
        calls.decode.push({ requested, bounds });
        await hooks.decode?.();
        if (mode === 'decode-error') throw Error('corrupt video');
        const pts = mode === 'outside' ? bounds[1] : bounds[0] + 16;
        return requested.map(requestedMs => ({ uri: 'frame-' + pts, requestedMs, actualPtsMs: pts }));
      },
      normalizeVideoEvidenceFrame: async (...args) => { calls.normalize.push(args); await hooks.normalize?.(); },
    },
    './mobileclip/analyzer': {
      SAMPLING_PROFILE: windows.BALANCED_V07_SAMPLING_PROFILE, MODEL_ID: 'S0', MODEL_SHA256: 'model', PROMPT_SHA256: 'prompt',
      analyzeMobileClip: async (uris, options) => {
        calls.analyze.push(uris);
        calls.analysisOptions.push(options);
        await hooks.analyze?.();
        if (mode === 'inference-error') throw Error('model run failed');
        return uris.map(() => ({ vector: [1, 0], fullClassifications: [{ identifier: 'outdoor', confidence: 1 }],
          quality: { eligibleForSelection: mode !== 'unusable' } }));
      },
    },
    './semanticRouter': { routeSemanticClip: ({ probes }) => ({ selectedTimestampsMs: [probes[0].actualPtsMs], recommendedAnchorMs: {}, reasonCodes: [] }) },
    './mobileclip/coverageV07': { coverageV07: ({ baseline }) => ({ anchors: baseline, reason: 'KEEP' }) },
    './selectFrames': { sampleRoleForIndex: () => 'WINDOW_MIDDLE', canonicalOffsetForRole: () => 4500 },
    './lastSemanticRoute': { setLastSemanticRouteAudit: audit => calls.published.push(audit) },
    './types': { MOBILECLIP_FP16_V07_PROFILE: { probeStepMs: 1000, includeFinalFrame: true } },
    '../pipeline/sha256File': { sha256File: async uri => { calls.hashes.push(uri); await hooks.hash?.(); return 'actual-frame-hash'; } },
  });
  const run = (control = {}) => mod.buildSemanticVideoEvidence({ assetId: 'a', localVideoUri: 'file:///original.mp4',
    durationMs: 10010, bundleDir: 'file:///bundle/', spatial: 'ASPECT_FIT_LETTERBOX', ...control });
  return { calls, run };
}
test('duplicate probe mappings use one real PTS per window, without padding or moving the first sample', async () => {
  const h = harness(); const result = await h.run();
  assert.deepEqual(Array.from(result.frames, f => f.source_timestamp_ms), [16, 5021]);
  assert.equal(result.evidence_sampling_profile, windows.BALANCED_V07_SAMPLING_PROFILE);
  assert.equal(result.evidence_window_count, 2);
  assert.deepEqual(h.calls.analyze.map(x => x.length), [1, 1]);
  assert.equal(h.calls.normalize.length, 2);
  const audit = JSON.parse(h.calls.writes[0][1]);
  assert.deepEqual(audit.windows.map(w => [w.startMs, w.endMs]), [[0, 5005], [5005, 10010]]);
});
for (const [mode, message] of [['outside', /outside/], ['decode-error', /corrupt/], ['inference-error', /model run failed/], ['unusable', /没有可用画面/]]) {
  test(`failed ${mode} never writes a success audit or fabricates evidence`, async () => {
    const h = harness(mode); await assert.rejects(h.run, message);
    assert.equal(h.calls.writes.length, 0); assert.equal(h.calls.normalize.length, 0);
  });
}
test('an old native module cannot silently use its broken zero-time decoder', async () => {
  let oldCalls = 0;
  const decoder = load('src/evidence/nativeVideoDecoder.ts', {
    'expo-file-system/legacy': {}, 'expo': { requireOptionalNativeModule: () => ({ extractVideoFrames() { oldCalls++; } }) },
  });
  assert.equal(decoder.isNativeVideoDecoderAvailable(), false);
  await assert.rejects(() => decoder.extractVideoFramesAtTimes('file:///v', [0], 'file:///d', [0, 1]), /安装/);
  assert.equal(oldCalls, 0);
});

test('a cancelled video operation never begins native decoding', async () => {
  const controller = new AbortController(); controller.abort();
  const h = harness();
  await assert.rejects(h.run({ signal: controller.signal }), { name: 'AbortError' });
  assert.equal(h.calls.decode.length, 0);
  assert.equal(h.calls.writes.length, 0);
});

for (const stage of ['decode', 'analyze', 'normalize', 'hash']) {
  test(`cancellation during ${stage} stops the next native/window/write stage`, async () => {
    const controller = new AbortController();
    const h = harness('valid', { [stage]: () => controller.abort() });
    await assert.rejects(h.run({ signal: controller.signal }), { name: 'AbortError' });
    assert.equal(h.calls.decode.length, 1, 'must not decode a second window');
    assert.equal(h.calls.analyze.length, stage === 'decode' ? 0 : 1);
    if (stage !== 'decode') assert.equal(h.calls.analysisOptions[0].signal, controller.signal);
    assert.equal(h.calls.normalize.length, ['decode', 'analyze'].includes(stage) ? 0 : 1);
    assert.equal(h.calls.hashes.length, stage === 'hash' ? 1 : 0);
    assert.equal(h.calls.writes.length, 0);
    assert.equal(h.calls.published.length, 0);
  });
}

test('abort waits for in-flight inference to settle before stopping evidence work', async () => {
  const controller = new AbortController();
  let release, started;
  const nativeRun = new Promise(resolve => { release = resolve; });
  const running = new Promise(resolve => { started = resolve; });
  const h = harness('valid', { analyze: async () => { started(); await nativeRun; } });
  let settled = false;
  const pending = h.run({ signal: controller.signal }).finally(() => { settled = true; });
  await running; controller.abort(); await Promise.resolve();
  assert.equal(settled, false, 'cleanup must not race a pending native run');
  release();
  await assert.rejects(pending, { name: 'AbortError' });
  assert.equal(h.calls.decode.length, 1); assert.equal(h.calls.normalize.length, 0);
  assert.equal(h.calls.writes.length, 0);
});

test('session fence changes also stop a video whose AbortSignal is not aborted', async () => {
  const controller = new AbortController(); let current = true;
  const h = harness('valid', { decode: () => { current = false; } });
  await assert.rejects(h.run({ signal: controller.signal, assertCurrent: () => {
    if (!current) throw Error('Session changed');
  } }), /Session changed/);
  assert.equal(controller.signal.aborted, false);
  assert.equal(h.calls.analyze.length, 0); assert.equal(h.calls.writes.length, 0);
});

test('cancellation during the final audit write removes the marker and never publishes the audit', async () => {
  const controller = new AbortController();
  const h = harness('valid', { write: () => controller.abort() });
  await assert.rejects(h.run({ signal: controller.signal }), { name: 'AbortError' });
  assert.deepEqual(h.calls.deleted, ['file:///bundle/semantic_route_a.json']);
  assert.equal(h.calls.published.length, 0);
});
