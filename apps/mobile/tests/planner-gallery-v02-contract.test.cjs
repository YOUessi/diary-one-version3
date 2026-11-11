// Actual phone-side V02 contract, using a BFF-valid generated result.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const ts = require('typescript');

require.extensions['.ts'] = (module, filename) => module._compile(
  ts.transpileModule(fs.readFileSync(filename, 'utf8'),
    { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText,
  filename,
);

const { validateDirectVlmResult } = require('../src/cloud/validateDirectVlmResult.ts');
const { ALGORITHM_LOCK } = require('../src/config/algorithmLock.ts');
const fixtureDir = path.join(__dirname, 'fixtures/planner-gallery-v02');
const resultFixture = JSON.parse(fs.readFileSync(path.join(fixtureDir, 'result.json'), 'utf8'));
const manifestFixture = JSON.parse(fs.readFileSync(path.join(fixtureDir, 'manifest.json'), 'utf8'));

test('V02 schema hash matches the BFF publishing contract', () => {
  const p = path.resolve(__dirname, '../../../services/bff/shared/contracts/planner_gallery_chapter_v02.schema.json');
  const hash = crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  assert.equal(ALGORITHM_LOCK.resultContractSha256.DIARY_ONE_PLANNER_GALLERY_CHAPTER_V02, hash);
  assert.equal(ALGORITHM_LOCK.plannerGalleryPreviewSchema, 'DIARY_ONE_PLANNER_GALLERY_CHAPTER_V02');
});

test('real app validator accepts exact V02 JPEG, clip and model-call provenance', () => {
  const original = JSON.stringify(resultFixture);
  assert.doesNotThrow(() => validateDirectVlmResult(resultFixture, manifestFixture));
  assert.equal(JSON.stringify(resultFixture), original, 'Validation must not mutate AI result');
});

test('the phone rejects V02 cross-chapter image, boundary, ID and trace forgery', () => {
  const mutations = [
    r => { r.chapters[0].source_clip_end = 3; },
    r => { r.chapters[1].source_clip_start = 2; },
    r => { r.chapters[1].experience_frame_ids.pop(); },
    r => { r.chapters[0].selected_media[0].representative_frame_id = 'asset_04-w0-f0'; },
    r => { r.chapters[1].key_moments[0].frame_ids = ['asset_01-w0-f0']; },
    r => { r.decision_trace.chapter_clip_intervals[0].end_clip = 4; },
    r => { r.decision_trace.gallery_model_input_frames[0] = 0; },
    r => { r.decision_trace.clip_ownership = 'UNVERIFIED'; },
    r => { r.trace.model_calls = 2; },
    r => { r.trace.stage_metrics[2].request_id = 'fake-receipt'; },
    r => { r.editor_policy = 'DIRECT_VLM_GLOBAL_EDITOR_V01'; },
  ];
  mutations.forEach((patch, i) => {
    const r = structuredClone(resultFixture);
    patch(r);
    assert.throws(() => validateDirectVlmResult(r, manifestFixture), undefined, 'mutation ' + i);
  });
});

test('new V02 version cannot masquerade as V01, or reverse', () => {
  const r = structuredClone(resultFixture);
  r.schema_version = 'DIARY_ONE_DIRECT_VLM_CHAPTER_V01';
  assert.throws(() => validateDirectVlmResult(r, manifestFixture));
  const v = structuredClone(resultFixture);
  v.trace.pipeline_version = 'X02_DIRECT_VLM_CHAPTER_V01';
  assert.throws(() => validateDirectVlmResult(v, manifestFixture));
});
