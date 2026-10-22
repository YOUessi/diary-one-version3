const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const Module = require('node:module');
const ts = require('typescript');
// Test the production TypeScript domain and SQL without a Metro/native runtime.
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(
  fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText, filename);
const { groupMediaByDay } = require('../src/domain/importDays.ts');
const { mergeDiaryDay } = require('../src/domain/mergeDiaryDay.ts');
const { buildUserDataExport } = require('../src/domain/dataExport.ts');
const { scopeImportedMemories } = require('../src/domain/scopeImportedMemories.ts');
const { capturedImports } = require('../src/domain/capturedImports.ts');
const chapter = (id, batch, extra = {}) => ({ id, sourceBatchId: batch, dateKey: '2026-10-18',
  title: 'Park walk', tags: ['Park'], moments: [], aiStory: 'Walk', ...extra });
const state = (chapters = [], small = []) => ({ chapters, smallMemoriesByDate: { '2026-10-18': small } });
test('capture dates separate days; missing metadata requires an explicit user choice', () => {
  const items = [new Date(2026, 9, 17, 12).getTime(), new Date(2026, 9, 16, 12).getTime(), undefined, NaN, Infinity]
    .map((creationTimeMs, id) => ({ id, creationTimeMs, confirmedDayKey: '2026-10-18' }));
  const groups = groupMediaByDay(items, '2026-10-18');
  assert.deepEqual(groups.map(([day, rows]) => [day, rows.length]),
    [['2026-10-16', 1], ['2026-10-17', 1], ['2026-10-18', 3]]);
  assert.throws(() => groupMediaByDay([{ creationTimeMs: NaN }], '2026-10-18'), /Confirm/);
  assert.deepEqual(groupMediaByDay([{ captureDayKey: '2026-10-17',
    creationTimeMs: Date.parse('2026-10-17T23:45:00-07:00') }]).map(([day]) => day), ['2026-10-17']);
});
test('a second batch preserves existing memories, notes and other days', () => {
  const old = chapter('one', 'batch1', { yourStory: 'My note', yourStoryRevision: 2 });
  const other = chapter('other', 'b0', { dateKey: '2026-10-17' });
  const result = mergeDiaryDay(state([old, other]), '2026-10-18', [chapter('two')], [], { sourceBatchId: 'batch2' });
  assert.deepEqual(result.chapters.map(c => c.id), ['two', 'one', 'other']);
  assert.equal(result.chapters[1].yourStory, 'My note');
});
test('reused cloud ids in two batches cannot overwrite or inherit another memory note', () => {
  const first = scopeImportedMemories('batch1', [chapter('cloud-1')], [{ id: 'aha-1', text: 'One' }]);
  const second = scopeImportedMemories('batch2', [chapter('cloud-1')], [{ id: 'aha-1', text: 'Two' }]);
  first.chapters[0].yourStory = 'Only first';
  const result = mergeDiaryDay(state(first.chapters), '2026-10-18', second.chapters, second.smallMemories, { sourceBatchId: 'batch2' });
  assert.equal(result.chapters.length, 2);
  assert.equal(result.chapters[0].yourStory, undefined);
  assert.equal(result.chapters[1].yourStory, 'Only first');
  assert.notEqual(first.smallMemories[0].id, second.smallMemories[0].id);
  assert.equal(scopeImportedMemories('batch2', [chapter('cloud-1')], []).chapters[0].id, second.chapters[0].id);
});
test('same batch retry replaces AI output, preserves exact-id notes and orphan notes', () => {
  const before = state([chapter('one', 'batch1', { yourStory: 'Mine', yourStoryRevision: 3 }),
    chapter('orphan', 'batch1', { yourStory: 'Keep me' }), chapter('obsolete', 'batch1')]);
  const result = mergeDiaryDay(before, '2026-10-18', [chapter('one', undefined, { aiStory: 'Updated' })], [], { sourceBatchId: 'batch1' });
  assert.deepEqual(result.chapters.map(c => c.id), ['one', 'orphan']);
  assert.equal(result.chapters[0].yourStoryRevision, 3);
  assert.equal(result.chapters[0].aiStory, 'Updated');
});
test('honest empty cannot erase a ready day or small memories', () => {
  assert.deepEqual(mergeDiaryDay(state([chapter('one')]), '2026-10-18', [], [], { preservePriorIfIncomingEmpty: true }), {});
  assert.deepEqual(mergeDiaryDay(state([], [{ id: 'small', text: 'Keep' }]), '2026-10-18', [], [], { preservePriorIfIncomingEmpty: true }), {});
});
test('a fourth small memory preserves the previously published history', () => {
  const result = mergeDiaryDay(state([], [1, 2, 3].map(i => ({ id: String(i), text: 'Old', sourceBatchId: 'a' }))),
    '2026-10-18', [], [{ id: '4', text: 'New' }], { sourceBatchId: 'b' });
  assert.deepEqual(result.smallMemoriesByDate['2026-10-18'].map(m => m.id), ['1', '2', '3', '4']);
  const retry = mergeDiaryDay(result, '2026-10-18', [], [{ id: '4', text: 'Updated' }], { sourceBatchId: 'b' });
  assert.deepEqual(retry.smallMemoriesByDate['2026-10-18'].map(m => m.id), ['1', '2', '3', '4']);
  assert.equal(retry.smallMemoriesByDate['2026-10-18'][3].text, 'Updated');
});
test('public export omits all credentials and implementation settings', () => {
  const result = buildUserDataExport({ chapters: [], sessionToken: 'SECRET_A', productionApiToken: 'SECRET_B',
    researchToken: 'SECRET_C', productionApiBaseUrl: 'internal', pipelineTasks: [{ secret: 'private' }], localProfile: { nickname: 'Me' } });
  const output = JSON.stringify(result);
  assert(!/SECRET|internal|private/.test(output));
  assert.equal(result.localProfile.nickname, 'Me');
});
test('original gallery uses retained local sources, genuine frame paths and no invented capture time', () => {
  const originals = capturedImports('batch', '2026-10-18', 'file:///bundle/', {
    photo: { uri: 'file:///sources/photo.jpg', media_kind: 'PHOTO' },
    video: { uri: 'file:///sources/video.mov', media_kind: 'VIDEO', durationMs: 12000 },
  }, [{ asset_id: 'video', frames: [{ relative_path: 'frames/actual.jpg' }] }]);
  assert.equal(originals[0].playbackUri, 'file:///sources/photo.jpg');
  assert.equal(originals[0].capturedAtLabel, undefined);
  assert.equal(originals[1].posterUri, 'file:///bundle/frames/actual.jpg');
  assert.equal(originals[1].durationSec, 12);
  assert.equal(originals[1].intakeSource, 'PHOTO_LIBRARY_TEST');
});

const { fromPickerAssets } = require('../src/pipeline/fromPicker.ts');
test('EXIF preserves the original calendar date, raw time and offset; invalid dates stay unknown', () => {
  const [offset, local, bad] = fromPickerAssets([
    { uri: 'a', exif: { DateTimeOriginal: '2026:10:17 23:45:00', OffsetTimeOriginal: '-07:00' } },
    { uri: 'b', exif: { DateTimeOriginal: '2026:10:17 23:45:00' } },
    { uri: 'c', exif: { DateTimeOriginal: '2026:13:40 23:45:00' } },
  ]);
  assert.equal(offset.captureDayKey, '2026-10-17');
  assert.equal(offset.captureUtcOffset, '-07:00');
  assert.equal(offset.creationTimeMs, Date.parse('2026-10-17T23:45:00-07:00'));
  assert.equal(local.captureTimeSource, 'EXIF_LOCAL');
  assert.equal(local.creationTimeMs, undefined);
  assert.equal(bad.captureTimeSource, 'UNKNOWN');
});

const { DatabaseSync } = require('node:sqlite');
const sql = new DatabaseSync(':memory:');
const adapter = {
  execAsync: async text => sql.exec(text),
  runAsync: async (text, ...params) => sql.prepare(text).run(...params),
  getFirstAsync: async (text, ...params) => sql.prepare(text).get(...params) ?? null,
  getAllAsync: async (text, ...params) => sql.prepare(text).all(...params),
  withExclusiveTransactionAsync: async work => {
    sql.exec('BEGIN IMMEDIATE');
    try { await work(adapter); sql.exec('COMMIT'); } catch (error) { sql.exec('ROLLBACK'); throw error; }
  },
};
const originalLoad = Module._load;
Module._load = function(name, ...args) {
  if (name === 'expo-file-system/legacy') return {};
  return name === 'expo-sqlite' ? { openDatabaseAsync: async () => adapter } : originalLoad.call(this, name, ...args);
};
const db = require('../src/db/sqlite.ts');
Module._load = originalLoad;
test('real SQLite: optimistic notes, tombstones, restart overlay and account isolation', async () => {
  await db.initDatabase();
  const snapshot = { ...db.emptySnapshot(), localProfile: { nickname: 'A', email: 'a@example.com' }, chapters: [chapter('one')] };
  await db.saveSnapshot(snapshot);
  const input = { owner: 'a@example.com', chapterId: 'one', expectedRevision: 0, text: 'Saved', assertCurrent() {} };
  assert.equal(await db.commitStoryRevision(input), 1);
  await assert.rejects(db.commitStoryRevision({ ...input, text: 'Stale' }), /changed/);
  assert.equal((await db.loadSnapshot()).chapters[0].yourStory, 'Saved');
  await db.commitStoryRevision({ ...input, expectedRevision: 1, text: undefined, previousText: 'Saved' });
  const removed = (await db.loadSnapshot()).chapters[0];
  assert.equal(removed.yourStory, undefined);
  assert.equal(removed.yourStoryRevision, 2);
  assert.equal(sql.prepare('SELECT previous_text FROM story_revisions WHERE revision=2').get().previous_text, 'Saved');
  await db.saveSnapshot({ ...snapshot, localProfile: { email: 'b@example.com' } });
  assert.equal((await db.loadSnapshot()).chapters[0].yourStoryRevision, undefined);
});
test('real SQLite: account guard failure rolls back the note transaction', async () => {
  await assert.rejects(db.commitStoryRevision({ owner: 'b@example.com', chapterId: 'one', expectedRevision: 0,
    text: 'Must roll back', assertCurrent() { throw new Error('Account changed'); } }), /Account changed/);
  assert.equal(sql.prepare("SELECT COUNT(*) AS n FROM story_revisions WHERE owner='b@example.com'").get().n, 0);
});

test('real SQLite: interrupted publication rolls back diary, task completion and all dedupe entries together', async () => {
  const before = { ...db.emptySnapshot(), chapters: [chapter('old')],
    pipelineTasks: [{ id: 'publishing', status: 'cloud_processing' }] };
  await db.saveSnapshot(before);
  const after = { ...before, chapters: [chapter('new')],
    pipelineTasks: [{ id: 'publishing', status: 'succeeded' }] };
  const assets = [{ asset_id: 'new-asset', original_sha256: 'atomic-publication-hash', media_kind: 'PHOTO' }];
  let guards = 0;
  await assert.rejects(db.saveSnapshot(after, () => {
    if (++guards === 2) throw new Error('Account changed during write');
  }, assets), /Account changed/);
  assert.equal((await db.loadSnapshot()).chapters[0].id, 'old');
  assert.equal((await db.loadSnapshot()).pipelineTasks[0].status, 'cloud_processing');
  assert.equal(sql.prepare("SELECT count(*) AS n FROM raw_assets WHERE original_sha256='atomic-publication-hash'").get().n, 0);
  await db.saveSnapshot(after, () => {}, assets);
  await db.saveSnapshot(after, () => {}, assets);
  assert.equal((await db.loadSnapshot()).chapters[0].id, 'new');
  assert.equal((await db.loadSnapshot()).pipelineTasks[0].status, 'succeeded');
  assert.equal(sql.prepare("SELECT use_count FROM raw_assets WHERE original_sha256='atomic-publication-hash'").get().use_count, 1);
});

test('real SQLite: failed profile persistence keeps the previously saved profile', async () => {
  const before = { ...db.emptySnapshot(), localProfile: { nickname: 'Before' } };
  await db.saveSnapshot(before);
  let guards = 0;
  await assert.rejects(db.saveSnapshot({ ...before, localProfile: { nickname: 'After' } }, () => {
    if (++guards === 2) throw new Error('Editing screen closed');
  }), /closed/);
  assert.equal((await db.loadSnapshot()).localProfile.nickname, 'Before');
});
test('cleanup receipt survives snapshot deletion and clears only after completion', async () => {
  await db.setLocalCleanupPending(true);
  sql.prepare('INSERT INTO raw_assets (original_sha256, asset_key, media_kind, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, ?)')
    .run('test-hash', 'asset1', 'PHOTO', 'today', 'today');
  await db.clearSnapshot();
  assert.equal(sql.prepare('SELECT COUNT(*) AS n FROM raw_assets').get().n, 0);
  assert.equal(await db.hasLocalCleanupPending(), true);
  assert.equal(await db.loadSnapshot(), null);
  await db.setLocalCleanupPending(false);
  assert.equal(await db.hasLocalCleanupPending(), false);
});

test('real SQLite: questionnaire scopes and skipped/default response survive reopening without content tags', async () => {
  const { buildSurveyProfile } = require('../src/onboarding/surveyProfile.ts');
  const { EMPTY_SURVEY_ANSWERS } = require('../src/onboarding/preferenceSurvey.ts');
  const result = buildSurveyProfile({ ...EMPTY_SURVEY_ANSWERS, momentIds: ['people', 'something_else'],
    customText: 'Fishing by the water', suggestedLabels: ['Fishing', 'Waterside'], showLessIds: ['similar'] });
  await db.saveSnapshot({ ...db.emptySnapshot(), preferences: result.preferences,
    preferenceSurveyResponse: result.response, preferenceSurveyComplete: true });
  const reopened = await db.loadSnapshot();
  assert.deepEqual(reopened.preferences, result.preferences);
  assert.deepEqual(reopened.preferenceSurveyResponse, result.response);
  assert.deepEqual(reopened.chapters, []);
  assert.deepEqual(reopened.topics, []);
  const skipped = buildSurveyProfile(EMPTY_SURVEY_ANSWERS);
  await db.saveSnapshot({ ...reopened, preferences: [], preferenceSurveyResponse: skipped.response });
  assert.equal((await db.loadSnapshot()).preferenceSurveyResponse.question_1_response, 'skipped');
});
