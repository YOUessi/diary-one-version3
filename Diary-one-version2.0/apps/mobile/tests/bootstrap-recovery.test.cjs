const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function harness(failSave = false) {
  const state = {};
  const snapshot = { chapters: [{ id: 'kept' }], preferences: [], smallMemoriesByDate: {},
    sessionToken: 'expired-local-fixture', productionApiBaseUrl: 'http://fixture.invalid',
    todayStatus: 'PREPARING', pipelineTasks: [{ id: 'task', status: 'building_evidence' }] };
  let saved;
  const stubs = {
    'react-native': { Alert: { alert() {} } },
    '../db/sqlite': { initDatabase: async () => {}, hasLocalCleanupPending: async () => false,
      loadSnapshot: async () => snapshot,
      saveSnapshot: async (value) => { if (failSave) throw Error('SQLITE_FULL'); saved = structuredClone(value); } },
    '../db/assetLedger': { hydrateAssetLedger() {}, serializeAssetLedger: () => [] },
    '../domain/localDataFiles': {},
    './useAppStore': { useAppStore: { getState: () => state, setState: patch => Object.assign(state, patch) }, buildPersistedSlice: s => s },
    '../assets/motionAssets': { applyBundledMotion: async chapters => chapters },
    '../model': {}, '../domain/dayKey': { diaryTodayKey: () => '2026-10-20' },
    '../domain/formatChapterDate': {}, '../domain/localProfile': {}, '../domain/mediaIntake': {},
    '../config/applyDevCloudDefaults': { applyDevCloudDefaults() {} },
    './emptyCommercialState': {}, '../domain/mergeDiaryDay': {}, '../domain/appSettings': {},
    '../config/buildProfile': { isInternalBetaBuild: true, isFormalConsumerApp: true },
    '../backend/productionCloudService': { probeProductionSession: async () => false },
    '../pipeline/runPipeline': { resumeInFlightCloudJobs() {
      state.pipelineTasks = [{ id: 'task', status: 'failed', error: 'stale_local_pipeline_state' }];
      state.todayStatus = 'PARTIAL';
    } },
  };
  const filename = path.resolve(__dirname, '../src/store/hydrate.ts');
  const module = { exports: {} };
  const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, console, setTimeout, clearTimeout,
    require(name) { assert(Object.hasOwn(stubs, name), name); return stubs[name]; } }, { filename });
  return { api: module.exports, state, saved: () => saved };
}

test('bootstrap durably saves expired-session and interrupted-task recovery without a subscription', async () => {
  const h = harness(); await h.api.bootstrapStore();
  assert.equal(h.saved().sessionToken, '');
  assert.equal(h.saved().pipelineTasks[0].status, 'failed');
  assert.equal(h.saved().todayStatus, 'PARTIAL');
  assert.equal(h.saved().chapters[0].id, 'kept');
});

test('bootstrap storage failure reaches the retry screen instead of pretending recovery was saved', async () => {
  const h = harness(true);
  await assert.rejects(h.api.bootstrapStore(), /SQLITE_FULL/);
  assert.equal(h.state.chapters[0].id, 'kept');
});
