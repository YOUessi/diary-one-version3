const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function harness(failSave = false) {
  const state = {};
  const snapshot = { chapters: [{ id: 'kept', moments: [
    { id: 'm2', playbackUri: 'file:///actual-import/cycling.mp4' },
  ] }], preferences: [], smallMemoriesByDate: {},
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
    '../model': {}, '../domain/dayKey': { diaryTodayKey: () => '2026-10-20' },
    '../domain/formatChapterDate': {}, '../domain/localProfile': {}, '../domain/mediaIntake': {},
    '../config/applyDevCloudDefaults': { applyDevCloudDefaults() {} },
    './emptyCommercialState': {}, '../domain/mergeDiaryDay': {mergeDiaryDay: (_before, _day, chapters, smallMemories) => ({chapters, smallMemoriesByDate: {'2026-10-20': smallMemories}})}, '../domain/appSettings': {},
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

test('bootstrap preserves imported playback even when a moment id matches an old demo id', async () => {
  const h = harness();
  await h.api.bootstrapStore();
  assert.equal(h.state.chapters[0].moments[0].playbackUri, 'file:///actual-import/cycling.mp4');
  assert.equal(h.saved().chapters[0].moments[0].playbackUri, 'file:///actual-import/cycling.mp4');
});

for (const failSave of [false, true]) {
  test(`delivery warning and diary are committed atomically (disk failure: ${failSave})`, async () => {
    const h = harness(failSave);
    h.state.chapters = [{id: 'old'}]; h.state.smallMemoriesByDate = {};
    h.state.pipelineTasks = [{id: 'task', status: 'cloud_processing'}];
    const summary = {outcome: 'partial', savedMemoryCount: 1, reason: 'ITEMS_WITHHELD'};
    const write = h.api.commitDiaryBatch({taskId: 'task', dayKey: '2026-10-20', sourceBatchId: 'batch',
      chapters: [{id: 'new'}], smallMemories: [], preservePriorIfIncomingEmpty: false,
      deliverySummary: summary, todayStatus: 'PARTIAL', assets: [], assertCurrent() {}});
    if (failSave) {
      await assert.rejects(write, /SQLITE_FULL/);
      assert.equal(h.state.pipelineTasks[0].status, 'cloud_processing');
      assert.equal(h.state.pipelineTasks[0].deliverySummary, undefined);
      assert.equal(h.state.chapters[0].id, 'old');
    } else {
      await write;
      assert.deepEqual(h.saved().pipelineTasks[0].deliverySummary, summary);
      assert.equal(h.saved().chapters[0].id, 'new');
      assert.equal(h.state.pipelineTasks[0].deliverySummary.outcome, 'partial');
    }
  });
}
