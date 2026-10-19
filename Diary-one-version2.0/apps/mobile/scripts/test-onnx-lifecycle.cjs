// Exercise actual TS lifecycle/analyzer code with native and file adapters.
// These fault injections do not replace native simulator reload verification.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
const settle = () => new Promise(resolve => setImmediate(resolve));
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
function context() { return vm.createContext({ console, AbortController, setTimeout, clearTimeout, atob, Float32Array, Uint8Array, DataView }); }
function load(file, stubs = {}, ctx = context()) {
  const source = ts.transpileModule(fs.readFileSync(path.join(root, file), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  }).outputText;
  const module = { exports: {} };
  ctx.__nextModule = module;
  ctx.__nextRequire = name => { if (Object.hasOwn(stubs, name)) return stubs[name]; throw Error(`Unmocked ${name}`); };
  vm.runInContext(`(function(module, exports, require) {\n${source}\n})(__nextModule, __nextModule.exports, __nextRequire)`, ctx, { filename: file });
  return module.exports;
}
const lifecycle = () => load('src/evidence/mobileclip/sessionLifecycle.ts').createSessionLifecycle();

test('concurrent callers initialize once, run serially and preserve result order', async () => {
  const manager = lifecycle(), gate = deferred(); let creates = 0, active = 0, maxActive = 0;
  const resource = { session: { release: async () => {} } };
  const init = async () => { creates++; await gate.promise; return resource; };
  const run = value => manager.run(init, async () => { active++; maxActive = Math.max(maxActive, active); await settle(); active--; return value; });
  const first = run(1), second = run(2); await settle(); assert.equal(creates, 1); gate.resolve();
  assert.deepEqual(await Promise.all([first, second]), [1, 2]); assert.equal(maxActive, 1); assert.equal(creates, 1);
});

test('initialization failure is surfaced and does not poison the retry queue', async () => {
  const manager = lifecycle(); let creates = 0;
  const init = async () => { if (++creates === 1) throw Error('native model load failed'); return { session: { release: async () => {} } }; };
  await assert.rejects(manager.run(init, async () => 1), /native model load failed/);
  assert.equal(await manager.run(init, async () => 2), 2); assert.equal(creates, 2);
});

test('release waits for an in-flight run; subsequent request gets a fresh session', async () => {
  const manager = lifecycle(), gate = deferred(), events = []; let creates = 0;
  const init = async () => { const id = ++creates; return { session: { release: async () => events.push(`release-${id}`) }, id }; };
  const first = manager.run(init, async () => { events.push('start'); await gate.promise; events.push('end'); });
  await settle(); const releasing = manager.release(); const next = manager.run(init, async x => x.id);
  await settle(); assert.deepEqual(events, ['start']); gate.resolve();
  await first; await releasing; assert.equal(await next, 2); assert.deepEqual(events, ['start', 'end', 'release-1']);
});

test('native inference failure releases before the next run and preserves the error', async () => {
  const manager = lifecycle(); let released = 0, created = 0;
  const init = async () => { created++; return { session: { release: async () => { released++; } } }; };
  await assert.rejects(manager.run(init, async () => { throw Error('ORT out of memory'); }), /ORT out of memory/);
  assert.equal(released, 1); assert.equal(await manager.run(init, async () => 'retry'), 'retry'); assert.equal(created, 2);
});

test('cancelled queued work neither initializes nor executes; later calls still work', async () => {
  const manager = lifecycle(), controller = new AbortController(); controller.abort(); let created = 0, executed = 0;
  const init = async () => { created++; return { session: { release: async () => {} } }; };
  await assert.rejects(manager.run(init, async () => executed++, controller.signal), { name: 'AbortError' });
  assert.equal(created, 0); assert.equal(executed, 0);
  assert.equal(await manager.run(init, async () => 'ok'), 'ok');
});

test('cancellation during inference discards results and waits for native completion before release', async () => {
  const manager = lifecycle(), controller = new AbortController(), gate = deferred(); let released = 0;
  const init = async () => ({ session: { release: async () => { released++; } } });
  const pending = manager.run(init, async () => { await gate.promise; return 'must not publish'; }, controller.signal);
  const rejection = assert.rejects(pending, { name: 'AbortError' }); await settle(); controller.abort();
  await settle(); assert.equal(released, 0); gate.resolve(); await rejection; assert.equal(released, 1);
});

test('failed native cleanup blocks a second session until explicit cleanup succeeds', async () => {
  const manager = lifecycle(); let releaseFails = true, created = 0;
  const init = async () => { created++; return { session: { release: async () => { if (releaseFails) throw Error('release failed'); } } }; };
  await assert.rejects(manager.run(init, async () => { throw Error('inference failed'); }), /inference failed/);
  await assert.rejects(manager.run(init, async () => 1), /cleanup failed/); assert.equal(created, 1);
  releaseFails = false; await manager.release(); assert.equal(await manager.run(init, async () => 2), 2); assert.equal(created, 2);
});

function analyzerHarness() {
  const ctx = context(), faults = {}, calls = { creates: 0, runs: 0, releases: 0, tensorDisposals: 0, outputDisposals: 0, reads: [] };
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'assets/models/mobileclip-s0-fp16/manifest.json')));
  const makeOutput = () => ({ type: 'float32', data: Float32Array.from({ length: 512 }, (_, i) => i === 0 ? 1 : 0), dispose() { calls.outputDisposals++; } });
  const ort = {
    Tensor: class { dispose() { calls.tensorDisposals++; } },
    InferenceSession: { create: async () => {
      calls.creates++; if (faults.initError) throw Error(faults.initError);
      if (faults.initGate) await faults.initGate.promise;
      return { inputNames: [faults.badContract ? 'wrong' : 'image'], outputNames: ['embedding'],
        release: async () => { calls.releases++; },
        run: async () => { calls.runs++; if (faults.runGate) await faults.runGate.promise; if (faults.runError) throw Error(faults.runError); return { embedding: faults.output?.() ?? makeOutput() }; } };
    } },
  };
  const stubs = {
    'expo-asset': { Asset: { fromModule: name => ({ localUri: `file:///${path.basename(name)}`, downloadAsync: async () => {} }) } },
    'expo-file-system': { File: class {
      constructor(uri) { this.uri = uri; }
      async bytes() {
        const uri = this.uri;
        calls.reads.push(uri); if (faults.readError && !uri.includes('prompts')) throw Error(faults.readError);
        return new Uint8Array(uri.includes('prompts') ? manifest.labels.length * 512 * 4 : 4);
      }
    } },
    'jpeg-js': { decode: () => { if (faults.jpegError) throw Error(faults.jpegError); return { width: 1, height: 1, data: new Uint8Array(4) }; } },
    'onnxruntime-react-native': ort,
    '../../../assets/models/mobileclip-s0-fp16/manifest.json': manifest,
    '../../../assets/models/mobileclip-s0-fp16/image_encoder.onnx': 'image_encoder.onnx',
    '../../../assets/models/mobileclip-s0-fp16/prompts.f32.bin': 'prompts.f32.bin',
    '../../pipeline/sha256File': { sha256File: async uri => faults.badHash ? 'wrong' : manifest.files[path.basename(uri)].sha256 },
    '../similarity': load('src/evidence/similarity.ts'),
    './pixels': { preprocessAsync: async (_, assertCurrent) => { if (faults.preprocessGate) await faults.preprocessGate.promise; assertCurrent(); return new Float32Array(3 * 256 * 256); }, pixelQuality: () => ({ eligibleForSelection: true }) },
    './sessionLifecycle': load('src/evidence/mobileclip/sessionLifecycle.ts'),
    '../videoWindows': load('src/evidence/videoWindows.ts'),
  };
  const reload = () => load('src/evidence/mobileclip/analyzer.ts', stubs, ctx);
  return { api: reload(), reload, faults, calls, makeOutput };
}

test('analyzer module reevaluation preserves its runtime queue/session without parallel native inference', async () => {
  const h = analyzerHarness(); h.faults.initGate = deferred();
  const first = h.api.analyzeMobileClip(['photo-1']); await settle();
  const reloaded = h.reload(); const second = reloaded.analyzeMobileClip(['photo-2']);
  await settle(); assert.equal(h.calls.creates, 1); h.faults.initGate.resolve();
  assert.equal((await first).length, 1); assert.equal((await second).length, 1);
  assert.equal(h.calls.creates, 1); assert.equal(h.calls.runs, 2); await reloaded.releaseMobileClip(); assert.equal(h.calls.releases, 1);
});

test('cancellation during preprocessing does not create tensors or call native inference', async () => {
  const h = analyzerHarness(), controller = new AbortController();
  h.faults.preprocessGate = deferred();
  const pending = h.api.analyzeMobileClip(['photo'], { signal: controller.signal });
  const rejection = assert.rejects(pending, { name: 'AbortError' });
  await settle(); controller.abort(); h.faults.preprocessGate.resolve(); await rejection;
  assert.equal(h.calls.runs, 0); assert.equal(h.calls.tensorDisposals, 0);
  delete h.faults.preprocessGate;
  assert.equal((await h.api.analyzeMobileClip(['photo'])).length, 1);
});

test('invalid model checksum fails closed before native creation and can be retried', async () => {
  const h = analyzerHarness(); h.faults.badHash = true;
  await assert.rejects(h.api.analyzeMobileClip(['photo']), /模型文件校验失败/); assert.equal(h.calls.creates, 0);
  h.faults.badHash = false; assert.equal((await h.api.analyzeMobileClip(['photo'])).length, 1);
});

test('wrong model input contract releases the created session before reporting failure', async () => {
  const h = analyzerHarness(); h.faults.badContract = true;
  await assert.rejects(h.api.analyzeMobileClip(['photo']), /model contract/); assert.equal(h.calls.releases, 1);
  h.faults.badContract = false; assert.equal((await h.api.analyzeMobileClip(['photo'])).length, 1); assert.equal(h.calls.creates, 2);
});

test('inference failure disposes input tensor and releases session before retry', async () => {
  const h = analyzerHarness(); h.faults.runError = 'simulated native failure';
  await assert.rejects(h.api.analyzeMobileClip(['photo']), /simulated native failure/);
  assert.equal(h.calls.tensorDisposals, 1); assert.equal(h.calls.outputDisposals, 0); assert.equal(h.calls.releases, 1);
  delete h.faults.runError; assert.equal((await h.api.analyzeMobileClip(['photo'])).length, 1);
  assert.equal(h.calls.creates, 2); assert.equal(h.calls.outputDisposals, 1);
});

test('NaN or wrong-size embeddings never produce semantic labels and all tensors are disposed', async () => {
  for (const mutate of [output => { output.data[0] = NaN; }, output => { output.data = new Float32Array(511); }]) {
    const h = analyzerHarness(); h.faults.output = () => { const output = h.makeOutput(); mutate(output); return output; };
    await assert.rejects(h.api.analyzeMobileClip(['photo']), /embedding/);
    assert.equal(h.calls.tensorDisposals, 1); assert.equal(h.calls.outputDisposals, 1); assert.equal(h.calls.releases, 1);
  }
});

test('cancel during a native run drops outputs and skips later photos after native completion', async () => {
  const h = analyzerHarness(), controller = new AbortController(); h.faults.runGate = deferred();
  const pending = h.api.analyzeMobileClip(['photo-1', 'photo-2'], { signal: controller.signal });
  const rejection = assert.rejects(pending, { name: 'AbortError' }); await settle(); controller.abort();
  assert.equal(h.calls.releases, 0); h.faults.runGate.resolve(); await rejection;
  assert.equal(h.calls.runs, 1); assert.equal(h.calls.outputDisposals, 1); assert.equal(h.calls.releases, 1);
  assert.ok(!h.calls.reads.includes('photo-2'));
});

test('bad JPEG/file read errors are surfaced without calling native inference and queue recovers', async () => {
  for (const fault of ['jpegError', 'readError']) {
    const h = analyzerHarness(); h.faults[fault] = 'damaged input';
    await assert.rejects(h.api.analyzeMobileClip(['photo']), /damaged input/); assert.equal(h.calls.runs, 0);
    delete h.faults[fault]; assert.equal((await h.api.analyzeMobileClip(['photo'])).length, 1);
  }
});

test('empty batch does not initialize native runtime', async () => {
  const h = analyzerHarness(); assert.equal((await h.api.analyzeMobileClip([])).length, 0); assert.equal(h.calls.creates, 0);
});

test('main assertCurrent owner fence stops later photos after a pending native run settles', async () => {
  const h = analyzerHarness(); h.faults.runGate = deferred(); let current = true;
  const pending = h.api.analyzeMobileClip(['photo-1', 'photo-2'], { assertCurrent: () => {
    if (!current) throw Error('owner changed');
  } });
  const rejected = assert.rejects(pending, /owner changed/); await settle(); current = false;
  assert.equal(h.calls.releases, 0); h.faults.runGate.resolve(); await rejected;
  assert.equal(h.calls.runs, 1); assert.equal(h.calls.outputDisposals, 1);
  assert.equal(h.calls.releases, 1); assert.ok(!h.calls.reads.includes('photo-2'));
});
