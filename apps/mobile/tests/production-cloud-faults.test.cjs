const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function harness({ status = 200, body = { job_id: 'job', status: 'succeeded', result: {} }, network, malformed, stalled, switched = false } = {}) {
  const state = { sessionToken: 'account-a', preferences: {}, setSessionToken(value) { this.sessionToken = value; } };
  const files = new Map(), profiles = [];
  const response = async () => {
    if (stalled) return new Promise(() => {});
    if (switched) state.sessionToken = 'account-b';
    if (network) throw Error('offline');
    return { ok: status >= 200 && status < 300, status, text: async () => malformed ? 'not JSON' : JSON.stringify(body),
      json: async () => { if (malformed) throw Error('bad JSON'); return body; } };
  };
  const stubs = {
    'expo-file-system/legacy': { readAsStringAsync: async uri => files.get(uri) ?? '{}', getInfoAsync: async uri => ({ exists: files.has(uri) }), writeAsStringAsync: async (uri,text) => files.set(uri,text) },
    '../cloud/researchClient': { buildBundleMultipartForm: async (_dir,_manifest,profile) => { profiles.push(profile); return {}; } },
    '../cloud/rnFormData': { postMultipartText: async () => { const r = await response(); return { ...r, text: await r.text() }; } },
    './resolveProductionBearer': { resolveProductionBearer: () => state.sessionToken, requireProductionBearer: () => state.sessionToken },
    '../store/useAppStore': { useAppStore: { getState: () => state } },
    '../domain/memoryPreferencesCloud': { buildAppClientProfile: preferences => ({ memory_preferences: preferences }) },
  };
  const filename = path.resolve(__dirname, '../src/backend/productionCloudService.ts'), module = { exports: {} };
  const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, fetch: response, AbortController,
    setTimeout: stalled ? callback => setImmediate(callback) : setTimeout, clearTimeout: stalled ? clearImmediate : clearTimeout,
    process: { env: { EXPO_PUBLIC_UPLOAD_MEMORY_PREFERENCES: '1' } }, Error,
    require(name) { if (!Object.hasOwn(stubs, name)) throw Error('Unexpected dependency ' + name); return stubs[name]; } }, { filename });
  return { state, files, profiles, api: module.exports };
}

for (const opts of [{ network: true }, { status: 500 }, { status: 503 }, { status: 429 }, { malformed: true },
  { body: { job_id: 'other-job', status: 'succeeded', result: {} } },
  { body: { job_id: 'job', status: 'succeeded' } }, { body: { job_id: 'job', status: 'surprise' } }]) {
  test('uncertain poll preserves retryable job: ' + JSON.stringify(opts), async () => {
    const h = harness(opts);
    const result = await h.api.pollProductionCloudJob('http://fixture.invalid', 'account-a', 'job');
    assert.equal(result.state, 'paused');
    assert.equal(h.state.sessionToken, 'account-a');
  });
}
for (const status of [401, 403]) for (const method of ['poll', 'submit']) {
  test(`late ${status} during ${method} cannot sign out a newer account`, async () => {
    const h = harness({ status, switched: true });
    if (method === 'poll') await h.api.pollProductionCloudJob('http://fixture.invalid', 'account-a', 'job');
    else await assert.rejects(h.api.submitProductionDayRevision('http://fixture.invalid', 'account-a', 'revision', 'file:///bundle/', 'file:///bundle/bundle.json'));
    assert.equal(h.state.sessionToken, 'account-b');
  });
}
for (const opts of [{ status: 404 }, { body: { job_id: 'job', status: 'failed', message: 'model unavailable' } }]) {
  test('definitive job failure: ' + JSON.stringify(opts), async () => {
    assert.equal((await harness(opts).api.pollProductionCloudJob('http://fixture.invalid', 'account-a', 'job')).state, 'failed');
  });
}
for (const job_id of [17, {}, ' ']) test('reject malformed submit identity ' + JSON.stringify(job_id), async () => {
  await assert.rejects(harness({ body: { job_id } }).api.submitProductionDayRevision('http://fixture.invalid', 'account-a', 'revision', 'file:///bundle/', 'file:///bundle/bundle.json'));
});
test('matching success and pending responses remain usable', async () => {
  assert.equal((await harness().api.pollProductionCloudJob('http://fixture.invalid', 'account-a', 'job')).state, 'succeeded');
  for (const status of ['queued', 'running', 'pending', 'processing']) assert.equal((await harness({ body: { job_id: 'job', status } }).api.pollProductionCloudJob('http://fixture.invalid', 'account-a', 'job')).state, 'pending');
});
test('a stalled request has a finite timeout and keeps original job retryable', {timeout: 1000}, async () => {
  assert.equal((await harness({stalled:true}).api.pollProductionCloudJob('http://fixture.invalid','account-a','job')).state,'paused');
});
test('lost POST acknowledgement retries frozen preferences even after settings change', async () => {
  const h=harness({network:true});h.state.preferences=['cycling'];
  await assert.rejects(h.api.submitProductionDayRevision('http://fixture.invalid','account-a','revision','file:///bundle/','file:///bundle/bundle.json'));
  h.state.preferences=['museum'];
  await assert.rejects(h.api.submitProductionDayRevision('http://fixture.invalid','account-a','revision','file:///bundle/','file:///bundle/bundle.json'));
  assert.equal(JSON.stringify(h.profiles[0]),JSON.stringify(h.profiles[1]));assert.match(JSON.stringify(h.profiles[1]),/cycling/);
});
