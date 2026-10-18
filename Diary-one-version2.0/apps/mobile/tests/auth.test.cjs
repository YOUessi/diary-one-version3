const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const Module = require('node:module');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'),
  { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, filename);
let state;
let resets;
const store = { getState: () => state, setState: patch => Object.assign(state, patch) };
const originalLoad = Module._load;
Module._load = function(name, ...args) {
  if (name === '../store/useAppStore') return { useAppStore: store };
  if (name === '../config/buildProfile') return { requireCloudAuth: true };
  if (name === './resolveProductionBearer') return { resolveProductionBearer: () => state.sessionToken };
  if (name === './bffUrl') return { resolveConfiguredBffUrl: () => 'https://example.invalid' };
  if (name === '../store/hydrate') return { resetLocalAppData: async () => {
    resets++;
    Object.assign(state, { sessionToken: '', localProfile: { nickname: 'Guest' }, chapters: [], cloudEvidenceConsent: null });
  }, flushPersist: async () => {} };
  return originalLoad.call(this, name, ...args);
};
const { verifyEmailOtpRemote, completeOAuthLogin } = require('../src/backend/authRemoteService.ts');
const beforeFetch = global.fetch;
test.after(() => { Module._load = originalLoad; global.fetch = beforeFetch; });
test.beforeEach(() => {
  resets = 0;
  state = { sessionToken: '', localProfile: { email: 'a@example.com', nickname: 'A' }, chapters: [{ id: 'private-a' }],
    onboardingComplete: true, cloudEvidenceConsent: true };
});
const respond = (email, session_token = 'new-token') => ({ ok: true, json: async () => ({ email, session_token }) });
test('a different email clears previous account content and consent before activating session', async () => {
  global.fetch = async () => respond('b@example.com');
  const result = await verifyEmailOtpRemote('b@example.com', '123456');
  assert.equal(result.ok, true);
  assert.equal(resets, 1);
  assert.deepEqual(state.chapters, []);
  assert.equal(state.cloudEvidenceConsent, null);
  assert.equal(state.localProfile.email, 'b@example.com');
  assert.equal(state.sessionToken, 'new-token');
});
test('same verified email preserves its own library when renewing an expired session', async () => {
  global.fetch = async () => respond('A@example.com');
  assert.equal((await verifyEmailOtpRemote('a@example.com', '123456')).ok, true);
  assert.equal(resets, 0);
  assert.equal(state.chapters[0].id, 'private-a');
});
test('late authentication response cannot overwrite a newer account session', async () => {
  global.fetch = async () => { state.sessionToken = 'already-switched'; return respond('b@example.com'); };
  assert.equal((await completeOAuthLogin('google', 'test-token')).ok, false);
  assert.equal(state.sessionToken, 'already-switched');
  assert.equal(resets, 0);
});
test('OAuth success without an actual session is rejected without changing local data', async () => {
  global.fetch = async () => respond('b@example.com', '');
  assert.equal((await completeOAuthLogin('apple', 'test-token')).ok, false);
  assert.equal(state.localProfile.email, 'a@example.com');
  assert.equal(resets, 0);
});
