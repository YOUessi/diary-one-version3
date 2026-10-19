// Run the remote pipeline functions with a controlled async validator boundary.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function harness() {
  const day = '2026-10-19', manifest = { bundle_version: 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04', assets: [] };
  const state = { sessionToken: 'account-a', productionApiBaseUrl: 'http://fixture.invalid', researchEndpoint: '',
    cloudProcessingTarget: 'production', cloudEvidenceConsent: true, capturedOriginals: [], chapters: [], smallMemoriesByDate: {},
    pipelineTasks: [{ id: 'task', dayKey: day, dayRevisionId: 'revision', status: 'cloud_processing', productionJobId: 'job',
      bundleDir: 'file:///fixture/', bundleJsonPath: 'file:///fixture/bundle.json' }] };
  const calls = { map: 0, attach: 0, commit: 0, delete: 0 };
  const store = { getState: () => state, setState: patch => Object.assign(state, typeof patch === 'function' ? patch(state) : patch) };
  let release, enteredResolve; const pending = new Promise(resolve => { release = resolve; });
  const entered = new Promise(resolve => { enteredResolve = resolve; });
  const stubs = {
    'expo-file-system/legacy': { documentDirectory: 'file:///fixture/', readAsStringAsync: async () => JSON.stringify(manifest), deleteAsync: async () => calls.delete++ },
    'react-native': { Alert: { alert() {} } },
    './buildAppLibraryBundle': { buildAppLibraryBundle: async () => ({ bundle: manifest, jsonPath: 'file:///fixture/bundle.json', sourceUris: {} }) },
    '../store/useAppStore': { useAppStore: store },
    '../cloud/researchClient': {}, '../backend/researchCloudService': {},
    '../backend/productionCloudService': { pollProductionCloudJob: async () => ({ state: 'succeeded', result: {} }) },
    '../cloud/mapPreviewResult': { mapPreviewToDiary: () => { calls.map++; return { chapters: [], smallMemories: [] }; } },
    '../cloud/validatePreviewResult': { validatePreviewResult: () => { enteredResolve(); return pending; } },
    '../store/hydrate': { commitDiaryBatch: async () => calls.commit++ },
    '../cloud/mapTodayStatus': { mapTodayStatusFromPreview: () => 'READY' },
    '../domain/dayKey': { diaryTodayKey: () => day }, '../domain/dayRevision': {}, '../domain/mediaIntake': {},
    './attachChapterMedia': { attachChapterMediaFromBundle: async () => { calls.attach++; return []; } },
    '../db/ledger': { rememberPipelineTask() {} }, '../db/assetLedger': { recordPipelineLedger() {} },
    '../backend/resolveProductionBearer': { resolveProductionBearer: () => state.sessionToken, requireProductionBearer: () => state.sessionToken },
    '../config/buildProfile': { isFormalConsumerApp: true, isLabToolsEnabled: false },
    '../domain/importDays': {}, '../domain/scopeImportedMemories': { scopeImportedMemories: (_id, chapters, smallMemories) => ({ chapters, smallMemories }) },
    '../domain/capturedImports': { capturedImports: () => [] }, './sha256File': { sha256SubmittedManifest: async () => 'f'.repeat(64) },
  };
  const filename = path.resolve(__dirname, '../src/pipeline/runPipeline.ts'), module = { exports: {} };
  const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, console, setTimeout, Date, Error,
    fetch: async () => ({ ok: true, json: async () => ({ allow_mock_preview: false }) }),
    require(name) { if (!Object.hasOwn(stubs, name)) throw Error('Unmocked pipeline dependency: ' + name); return stubs[name]; },
  }, { filename });
  return { api: module.exports, state, calls, entered, release };
}

for (const mode of ['new import', 'resume saved job']) {
  test(`account change during async contract verification stops ${mode} before mapping/attachment/persistence`, { timeout: 2000 }, async () => {
    const h = harness();
    const run = mode === 'new import' ? h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]) : h.api.resumeInFlightCloudJobs();
    await h.entered;
    h.state.sessionToken = 'account-b'; h.state.chapters = [{ id: 'account-b-private' }];
    h.release({ ok: true });
    await run; await new Promise(resolve => setImmediate(resolve));
    assert.deepEqual([h.calls.map, h.calls.attach, h.calls.commit], [0, 0, 0]);
    assert.deepEqual(h.state.chapters, [{ id: 'account-b-private' }]);
    assert.notEqual(h.state.pipelineTasks[0].status, 'succeeded');
  });
}
