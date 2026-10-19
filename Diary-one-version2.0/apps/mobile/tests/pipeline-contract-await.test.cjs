// Run the remote pipeline functions with a controlled async validator boundary.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function harness(options = {}) {
  const day = '2026-10-19', manifest = { bundle_version: 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04', assets: [] };
  const state = { sessionToken: 'account-a', productionApiBaseUrl: 'http://fixture.invalid', researchEndpoint: '',
    cloudProcessingTarget: 'production', cloudEvidenceConsent: true, capturedOriginals: [], chapters: [], smallMemoriesByDate: {},
    pipelineTasks: [{ id: 'task', dayKey: day, dayRevisionId: 'revision', status: 'cloud_processing', productionJobId: 'job',
      bundleDir: 'file:///fixture/', bundleJsonPath: 'file:///fixture/bundle.json' }] };
  const calls = { map: 0, attach: 0, commit: 0, delete: 0, build: 0, poll: 0, submit: 0 };
  const store = { getState: () => state, setState: patch => Object.assign(state, typeof patch === 'function' ? patch(state) : patch) };
  let release, enteredResolve; const pending = new Promise(resolve => { release = resolve; });
  const entered = new Promise(resolve => { enteredResolve = resolve; });
  const stubs = {
    'expo-file-system/legacy': { documentDirectory: 'file:///fixture/', readAsStringAsync: async () => JSON.stringify(manifest), deleteAsync: async () => calls.delete++ },
    'react-native': { Alert: { alert() {} } },
    './buildAppLibraryBundle': { buildAppLibraryBundle: async () => { calls.build++; return { bundle: manifest, jsonPath: 'file:///fixture/bundle.json', sourceUris: {} }; } },
    '../store/useAppStore': { useAppStore: store },
    '../cloud/researchClient': {}, '../backend/researchCloudService': {},
    '../backend/productionCloudService': {
      checkProductionHealth: async () => ({ allow_mock_preview: false }),
      submitProductionDayRevision: async () => { calls.submit++; if (options.conflict) throw Error('DAY_REVISION_CONFLICT:changed'); return { jobId: 'job' }; },
      pollProductionCloudJob: async () => { calls.poll++; if (options.switchDuringPoll) state.sessionToken = 'account-b';
        return options.paused ? { state: 'paused', message: 'network unavailable' } : { state: 'succeeded', result: {} }; } },
    '../cloud/mapPreviewResult': { mapPreviewToDiary: () => { calls.map++; return { chapters: [], smallMemories: [] }; } },
    '../cloud/validatePreviewResult': { validatePreviewResult: () => { enteredResolve(); return pending; } },
    '../store/hydrate': { flushPersist: async () => {}, commitDiaryBatch: async () => { if (options.diskFull) throw Error('SQLITE_FULL'); calls.commit++; } },
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

test('retrying an uploaded job reuses frozen evidence instead of extracting it again', async () => {
  const h = harness(); h.release({ ok: true });
  await h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]);
  assert.equal(h.calls.build, 0); assert.equal(h.calls.submit, 0); assert.equal(h.calls.commit, 1);
});

test('two simultaneous retries cannot duplicate extraction, polling or publication', async () => {
  const h = harness();
  const runs = [h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]), h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }])];
  await h.entered; h.release({ ok: true }); await Promise.all(runs);
  assert.equal(h.calls.poll, 1); assert.equal(h.calls.commit, 1);
});

test('account change during poll stops before reading or validating another account result', async () => {
  const h = harness({ switchDuringPoll: true }); h.release({ ok: true });
  await h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]);
  assert.equal(h.calls.commit, 0); assert.equal(h.calls.map, 0);
});

test('disk full preserves prior ready data and job identity for save retry', async () => {
  const h = harness({ diskFull: true }); h.release({ ok: true });
  h.state.chapters = [{ id: 'prior', dateKey: '2026-10-19' }];
  await h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]);
  assert.equal(h.state.pipelineTasks[0].status, 'failed');
  assert.equal(h.state.pipelineTasks[0].productionJobId, 'job');
  assert.equal(h.state.chapters[0].id, 'prior'); assert.equal(h.state.todayStatus, 'READY');
});

test('revision conflict is visible, never silently creates a second billable revision', async () => {
  const h = harness({ conflict: true }); h.state.pipelineTasks[0].productionJobId = undefined; h.release({ ok: true });
  await h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]);
  assert.equal(h.calls.submit, 1); assert.equal(h.calls.commit, 0);
  assert.equal(h.state.pipelineTasks[0].dayRevisionId, 'revision');
});

test('temporary poll outage pauses without clearing the accepted job or prior content', async () => {
  const h = harness({ paused: true });
  await h.api.runPipeline('task', [{ uri: 'file:///fixture/source.mp4' }]);
  assert.equal(h.state.pipelineTasks[0].status, 'failed');
  assert.equal(h.state.pipelineTasks[0].productionJobId, 'job');
  assert.match(h.state.pipelineTasks[0].error, /CLOUD_JOB_PAUSED/);
  assert.equal(h.calls.commit, 0);
});

test('visible retry after lost submit acknowledgement uses saved evidence and the same revision', async () => {
  const h=harness();h.state.pipelineTasks[0].status='failed';h.state.pipelineTasks[0].productionJobId=undefined;
  h.api.retryStoredCloudResult('task');await h.entered;h.release({ok:true});await new Promise(resolve=>setImmediate(resolve));
  assert.equal(h.calls.build,0);assert.equal(h.calls.submit,1);assert.equal(h.calls.commit,1);
  assert.equal(h.state.pipelineTasks[0].dayRevisionId,'revision');assert.equal(h.state.pipelineTasks[0].productionJobId,'job');
});

for (const mode of ['new import', 'resume saved job']) {
  test(`session renewal during ${mode} resumes after the old runner releases ownership`, async () => {
    const h = harness();
    const run = mode === 'new import' ? h.api.runPipeline('task', []) : h.api.resumeInFlightCloudJobs();
    await h.entered;
    h.state.sessionToken = 'renewed-account-a';
    h.api.resumeInFlightCloudJobs();
    h.api.resumeInFlightCloudJobs();
    h.release({ ok: true });
    await run; await new Promise(resolve => setImmediate(resolve));
    assert.equal(h.calls.poll, 2);
    assert.equal(h.calls.commit, 1);
    assert.equal(h.calls.submit, 0);
    assert.equal(h.state.pipelineTasks[0].status, 'succeeded');
  });

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

test('queued session renewal is discarded if the user signs out before the old runner stops', async () => {
  const h = harness(); const run = h.api.runPipeline('task', []);
  await h.entered;
  h.state.sessionToken = 'renewed-account-a'; h.api.resumeInFlightCloudJobs();
  h.state.sessionToken = ''; h.release({ ok: true });
  await run; await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.calls.poll, 1); assert.equal(h.calls.commit, 0);
});

test('resume does not mark a currently running pre-upload task as interrupted', async () => {
  const h = harness(); h.state.pipelineTasks[0].productionJobId = undefined;
  const run = h.api.runPipeline('task', []);
  h.api.resumeInFlightCloudJobs();
  assert.equal(h.state.pipelineTasks[0].status, 'building_evidence');
  h.release({ ok: true }); await run;
  assert.equal(h.calls.commit, 1); assert.equal(h.calls.submit, 1);
});

test('resume request for the current session does not retry an active runner after a poll failure', async () => {
  const h = harness({ diskFull: true }); const run = h.api.runPipeline('task', []);
  await h.entered; h.api.resumeInFlightCloudJobs(); h.release({ ok: true });
  await run; await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.calls.poll, 1); assert.equal(h.state.pipelineTasks[0].status, 'failed');
});
