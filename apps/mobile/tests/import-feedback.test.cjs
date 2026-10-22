const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

const tick = () => new Promise(resolve => setImmediate(resolve));
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const video = (extra = {}) => ({ uri: 'file:///cycling.mov', type: 'video', duration: 60000,
  fileSize: 90 * 1024 * 1024, creationTime: Date.parse('2026-10-21T04:00:00Z'), ...extra });

function harness(options = {}) {
  const state = { language: 'zh-Hans', sessionToken: 'account-a', cloudEvidenceConsent: true, pipelineTasks: [], ...options.state };
  const listeners = new Set(), calls = { picker: [], hash: [], lookup: [], ledger: [], enqueue: [], alerts: [], panels: [] };
  const store = Object.assign(selector => selector(state), { getState: () => state,
    setState(patch) { Object.assign(state, patch); for (const fn of listeners) fn(state); },
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); } });
  const modules = new Map();
  function load(filename) {
    if (modules.has(filename)) return modules.get(filename).exports;
    const module = { exports: {} }; modules.set(filename, module);
    const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: {
      module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true,
    } }).outputText;
    vm.runInNewContext(code, { module, exports: module.exports, Error, Date, console,
      require(name) {
        if (name === 'zustand') return { create(init) {
          const s = init(); return Object.assign(fn => fn(s), { getState: () => s, setState(patch) { Object.assign(s, patch); calls.panels.push(s.feedback); } });
        } };
        if (name.endsWith('/store/useAppStore')) return { useAppStore: store };
        if (name === 'react') return {};
        if (name === 'react/jsx-runtime') { const jsx = (type, props) => ({ type, props }); return { jsx, jsxs: jsx }; }
        if (name === 'react-native-safe-area-context') return { useSafeAreaInsets: () => ({ top: 48 }) };
        if (name === 'react-native') return { Platform: { OS: options.platform || 'ios' }, Alert: { alert(...args) { calls.alerts.push(args); } },
          StyleSheet: { create: x => x }, ActivityIndicator: 'Spinner', Pressable: 'Button', ScrollView: 'Scroll', View: 'View', Text: 'Text' };
        if (name === 'expo-image-picker') return {
          UIImagePickerPreferredAssetRepresentationMode: { Current: 'current' },
          requestMediaLibraryPermissionsAsync: async () => { if (options.permissionError) throw options.permissionError; return { granted: options.permission !== false }; },
          launchImageLibraryAsync: async config => {
            calls.picker.push(config);
            if (options.picker) return options.picker(config);
            if (options.pickerError) throw options.pickerError;
            return options.result || { canceled: false, assets: [video()] };
          },
        };
        if (name === './runPipeline') return { enqueuePipeline(items, source) { calls.enqueue.push({ items, source }); return options.queueBusy ? null : 'task-1'; } };
        if (name === './sha256File') return { sha256File: async uri => { calls.hash.push(uri); return options.hash ? options.hash(uri) : uri; } };
        if (name === './ensureLocalFileUri') return { ensureLocalFileUri: async uri => uri };
        if (name === '../db/rawAssetLedger') return {
          findRawAssetBySha: async sha => { calls.lookup.push(sha); return options.known ? { assetKey: 'existing' } : null; },
          upsertRawAsset: async row => calls.ledger.push(row),
        };
        if (name === './createDemoPhoto') return {};
        if (name === './createSimulationVideo') return {};
        if (name === '../config/buildProfile') return { isLabToolsEnabled: false };
        if (name === '../backend/resolveProductionBearer') return { resolveProductionBearer: () => state.sessionToken };
        if (name.startsWith('.')) {
          const base = path.resolve(path.dirname(filename), name);
          return load(base + (fs.existsSync(base + '.ts') ? '.ts' : '.tsx'));
        }
        throw Error('Unmocked import dependency: ' + name);
      },
    }, { filename });
    return module.exports;
  }
  const source = rel => load(path.resolve(__dirname, '../src', rel));
  const api = source('pipeline/launchEvidenceImport.ts');
  const feedbackStore = source('store/useImportFeedbackStore.ts').useImportFeedbackStore;
  return { api, state, store, calls, listeners, source, get feedback() { return feedbackStore.getState().feedback; },
    render() { return source('components/ImportFeedbackPanel.tsx').ImportFeedbackPanel(); } };
}

test('iCloud original download is enabled and 60 second video reaches the pipeline once', async () => {
  const h = harness({ picker: async config => {
    if (!config.shouldDownloadFromNetwork) throw Error('PHPhotosErrorDomain 3164');
    return { canceled: false, assets: [video()] };
  } });
  await h.api.launchEvidenceImport();
  assert.equal(h.calls.picker[0].preferredAssetRepresentationMode, 'current');
  assert.equal(h.calls.enqueue.length, 1);
  assert.equal(h.calls.enqueue[0].items[0].durationMs, 60000);
  assert.match(h.feedback.message, /已接收 1/); assert.equal(h.listeners.size, 0);
});

test('feedback is already visible while Photos downloads, then while SHA checks run', async () => {
  const pick = deferred(), hash = deferred();
  const h = harness({ picker: () => pick.promise, hash: () => hash.promise });
  const run = h.api.launchEvidenceImport(); await tick();
  assert.equal(h.feedback.kind, 'busy'); assert.match(h.feedback.message, /iCloud/);
  assert.equal(h.render().props.children.props.testID, 'import-feedback');
  pick.resolve({ canceled: false, assets: [video()] }); await tick();
  assert.match(h.feedback.message, /第 1\/1/); assert.equal(h.calls.enqueue.length, 0);
  hash.resolve('hash'); await run;
  assert.equal(h.feedback.kind, 'notice');
});

for (const [name, options, code] of [
  ['picker fails after dismissal', { pickerError: Error('Cannot read video') }, 'READ'],
  ['iCloud download offline', { pickerError: Error('network unavailable') }, 'DOWNLOAD'],
  ['cache disk full', { pickerError: Error('ENOSPC') }, 'STORAGE'],
  ['permission native exception', { permissionError: Error('native rejected') }, 'READ'],
  ['hash read fails', { hash: async () => { throw Error('unreadable file:///private/secret-path'); } }, 'CHECK'],
]) {
  test(name + ' produces persistent safe feedback, not an unhandled rejection', async () => {
    const h = harness(options); await assert.doesNotReject(h.api.launchEvidenceImport());
    assert.equal(h.feedback.kind, 'error'); assert.match(h.feedback.message, new RegExp('IMPORT_' + code));
    assert.doesNotMatch(h.feedback.message, /secret-path|file:\/\//);
    assert.equal(h.calls.enqueue.length, 0); assert.equal(h.listeners.size, 0);
    h.feedback.dismiss(); assert.equal(h.feedback, null);
  });
}

test('native cancel clears preparation and allows another picker', async () => {
  const h = harness({ result: { canceled: true, assets: null } });
  await h.api.launchEvidenceImport(); assert.equal(h.feedback, null);
  await h.api.launchEvidenceImport(); assert.equal(h.calls.picker.length, 2); assert.equal(h.calls.hash.length, 0);
});

test('rapid taps cannot open parallel pickers, and cancel ignores a late native success', async () => {
  const pick = deferred(), h = harness({ picker: () => pick.promise });
  const run = h.api.launchEvidenceImport(); await tick(); await h.api.launchEvidenceImport();
  assert.equal(h.calls.picker.length, 1);
  h.feedback.dismiss(); await h.api.launchEvidenceImport(); assert.equal(h.calls.picker.length, 1);
  pick.resolve({ canceled: false, assets: [video()] }); await run;
  assert.equal(h.calls.hash.length, 0); assert.equal(h.calls.enqueue.length, 0);
});

for (const mode of ['cancel', 'account', 'consent']) {
  test(mode + ' during hashing stops before touching history or starting a cloud task', async () => {
    const hash = deferred(), h = harness({ hash: () => hash.promise, known: true });
    const run = h.api.launchEvidenceImport(); await tick();
    if (mode === 'cancel') h.feedback.dismiss();
    if (mode === 'account') h.store.setState({ sessionToken: 'account-b' });
    if (mode === 'consent') h.store.setState({ cloudEvidenceConsent: false });
    hash.resolve('hash'); await run;
    assert.equal(h.calls.lookup.length, 0); assert.equal(h.calls.ledger.length, 0); assert.equal(h.calls.enqueue.length, 0);
    assert.equal(h.feedback, null); assert.equal(h.listeners.size, 0);
  });
}

for (const decision of ['confirm', 'cancel', 'logout']) {
  test('missing video date has a stable in-app confirmation: ' + decision, async () => {
    const h = harness({ result: { canceled: false, assets: [video({ creationTime: undefined }), video({ creationTime: undefined })] } });
    const run = h.api.launchEvidenceImport(); await tick();
    assert.equal(h.feedback.kind, 'confirm'); assert.match(h.feedback.message, /跳过 1/);
    assert.equal(h.calls.alerts.length, 0); assert.equal(h.calls.enqueue.length, 0);
    assert.ok(h.render());
    if (decision === 'confirm') h.feedback.confirm.run();
    if (decision === 'cancel') h.feedback.dismiss();
    if (decision === 'logout') h.store.setState({ sessionToken: '' });
    await run;
    assert.equal(h.calls.enqueue.length, decision === 'confirm' ? 1 : 0);
    if (decision === 'confirm') {
      assert.match(h.calls.enqueue[0].items[0].confirmedDayKey, /^\d{4}-\d{2}-\d{2}$/);
      assert.equal(h.calls.enqueue[0].items[0].creationTimeMs, undefined);
    }
    assert.equal(h.listeners.size, 0);
  });
}

for (const [label, extra, expected] of [
  ['large 60 second 4K video', { fileSize: 201 * 1024 * 1024 }, /200 MB/],
  ['long video', { duration: 601000 }, /10 分钟/],
  ['invalid media', { type: undefined }, /无法识别/],
]) {
  test(label + ' has a visible validation reason before hashing', async () => {
    const h = harness({ result: { canceled: false, assets: [video(extra)] } });
    await h.api.launchEvidenceImport(); assert.match(h.feedback.message, expected);
    assert.equal(h.calls.hash.length, 0); assert.equal(h.calls.enqueue.length, 0);
  });
}

test('already imported files do not create a second task', async () => {
  const h = harness({ known: true }); await h.api.launchEvidenceImport();
  assert.match(h.feedback.title, /已导入|已经导入/); assert.equal(h.calls.enqueue.length, 0);
});

test('existing processing blocks a new picker before expensive work', async () => {
  const h = harness({ state: { pipelineTasks: [{ status: 'building_evidence' }] } });
  await h.api.launchEvidenceImport(); assert.equal(h.calls.picker.length, 0); assert.match(h.feedback.message, /当前导入/);
});

test('denied permission is visible and does not launch Photos', async () => {
  const h = harness({ permission: false }); await h.api.launchEvidenceImport();
  assert.equal(h.calls.picker.length, 0); assert.equal(h.feedback.kind, 'notice');
});

test('Android Done ends selection and submits the selected item', async () => {
  const h = harness({ platform: 'android' }); const run = h.api.launchEvidenceImport(); await tick();
  assert.equal(h.feedback.kind, 'confirm'); assert.equal(h.feedback.dismissLabel, '完成');
  h.feedback.dismiss(); await run; assert.equal(h.calls.enqueue.length, 1);
});
