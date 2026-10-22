const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function harness(profile, initial = {}, envOverrides = {}, formal = true) {
  const env = { ...require('../eas.json').build[profile].env, ...envOverrides };
  const state = { productionApiBaseUrl: '', productionApiToken: '', cloudEvidenceConsent: null,
    sessionToken: 'owned-session', chapters: [{ id: 'kept' }], ...initial };
  const store = { getState: () => state, setState: patch => Object.assign(state, patch) };
  const modules = {};
  function load(relative) {
    const filename = path.resolve(__dirname, relative);
    if (modules[filename]) return modules[filename].exports;
    const module = { exports: {} }; modules[filename] = module;
    const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
      compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
    }).outputText;
    vm.runInNewContext(code, { module, exports: module.exports, process: { env },
      require(name) {
        if (name === '../store/useAppStore') return { useAppStore: store };
        if (name === '../onboarding/preferenceSurvey') return { CLOUD_EVIDENCE_CONSENT_VERSION: 'fixture' };
        if (name === './buildProfile') return { isStoreRelease: env.EXPO_PUBLIC_STORE_RELEASE === '1',
          isFormalConsumerApp: formal, isLabToolsEnabled: !formal };
        if (name === '../backend/bffUrl') return load('../src/backend/bffUrl.ts');
        throw Error('Unexpected import: ' + name);
      },
    }, { filename });
    return module.exports;
  }
  return { state, api: load('../src/config/applyDevCloudDefaults.ts') };
}

for (const profile of ['preview', 'production']) {
  test(`${profile}: a fresh install has its public BFF without silently accepting cloud upload`, () => {
    const h = harness(profile);
    h.api.applyDevCloudDefaults(); h.api.ensureDevCloudConsentForLab();
    assert.equal(h.state.productionApiBaseUrl, 'https://bff.diary.luxe');
    assert.equal(h.state.productionApiToken, '');
    assert.equal(h.state.cloudEvidenceConsent, null);
    assert.equal(h.state.sessionToken, 'owned-session');
    assert.equal(h.state.chapters[0].id, 'kept');
  });
  test(`${profile}: upgrading clears stale shared credentials and preserves an explicit refusal`, () => {
    const h = harness(profile, { productionApiBaseUrl: 'http://old.invalid', productionApiToken: 'old-shared',
      researchToken: 'old-research', researchEndpoint: 'http://old.invalid', cloudEvidenceConsent: false },
    { EXPO_PUBLIC_DEV_BFF_TOKEN: 'must-not-be-used' });
    h.api.applyDevCloudDefaults(); h.api.ensureDevCloudConsentForLab();
    assert.equal(h.state.productionApiBaseUrl, 'https://bff.diary.luxe');
    assert.equal(h.state.productionApiToken, '');
    assert.equal(h.state.researchToken, '');
    assert.equal(h.state.researchEndpoint, '');
    assert.equal(h.state.cloudEvidenceConsent, false);
    assert.equal(h.state.sessionToken, 'owned-session');
  });
}
test('a store build cannot enable shared credentials or auto-consent even if lab flags drift', () => {
  const h = harness('production', {}, { EXPO_PUBLIC_DEV_BFF_TOKEN: 'must-not-be-used' }, false);
  h.api.applyDevCloudDefaults(); h.api.ensureDevCloudConsentForLab();
  assert.equal(h.state.productionApiToken, '');
  assert.equal(h.state.cloudEvidenceConsent, null);
});
test('missing configuration does not overwrite a previously configured URL', () => {
  const h = harness('production', { productionApiBaseUrl: 'https://kept.invalid' },
    { EXPO_PUBLIC_DEV_BFF_URL: 'REPLACE_WITH_URL', EXPO_PUBLIC_BFF_BASE_URL: '' });
  h.api.applyDevCloudDefaults();
  assert.equal(h.state.productionApiBaseUrl, 'https://kept.invalid');
});
