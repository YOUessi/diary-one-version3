const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
require.extensions['.ts'] = (m, f) => m._compile(ts.transpileModule(fs.readFileSync(f, 'utf8'),
  { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, f);
const { buildDayFeed, buildEarlierFeed, historyDateKeys } = require('../src/diary/buildDiaryFeed.ts');
const { scopeImportedMemories } = require('../src/domain/scopeImportedMemories.ts');
const day = '2026-10-20', today = '2026-10-21';
const chapter = (id, extra = {}) => ({ id, dateKey: day, moments: [], ...extra });
const ids = feed => feed.filter(x => x.kind !== 'day_header').map(x => (x.chapter ?? x.memory).id);

test('history counts dates, includes Aha-only days, and does not omit their content', () => {
  const chapters = [chapter('c1'), chapter('c2')];
  const small = { '2026-10-19': [{ id: 'aha-only', text: 'A real small moment.' }],
    [day]: [{ id: 'same-day', text: 'Another real moment.' }], [today]: [{ id: 'today' }], '2026-10-18': [] };
  assert.deepEqual(historyDateKeys(chapters, small, today), [day, '2026-10-19']);
  const first = buildEarlierFeed(chapters, today, 1, 'zh-Hans', small);
  assert.deepEqual(ids(first[0].items), ['c1', 'c2', 'same-day']);
  const more = buildEarlierFeed(chapters, today, 2, 'zh-Hans', small);
  assert.deepEqual(ids(more[1].items), ['aha-only']);
  assert.equal(more[0].items[0].label, '昨天');
});

test('real capture times interleave Chapter and Aha across batches without mutating saved data', () => {
  const chapters = [chapter('late', { capturedAtMs: 3000, sourceBatchId: 'a' }),
    chapter('early', { capturedAtMs: 1000, sourceBatchId: 'b' })];
  const small = [{ id: 'middle', text: 'Exact original words', capturedAtMs: 2000, sourceBatchId: 'c' }];
  const before = JSON.stringify({ chapters, small });
  const feed = buildDayFeed(day, today, chapters, small);
  assert.deepEqual(ids(feed), ['early', 'middle', 'late']);
  assert.equal(feed[2].memory.text, 'Exact original words');
  assert.equal(JSON.stringify({ chapters, small }), before);
});

test('missing capture times use sequence only within the same import; legacy entries keep their positions', () => {
  const chapters = [chapter('first', { sourceBatchId: 'a', sourceSequenceIndex: 1 }),
    chapter('legacy'), chapter('last', { sourceBatchId: 'a', sourceSequenceIndex: 3 }),
    chapter('other-batch', { sourceBatchId: 'b', sourceSequenceIndex: 0 })];
  const small = [{ id: 'middle', sourceBatchId: 'a', sourceSequenceIndex: 2, text: 'same batch' }];
  assert.deepEqual(ids(buildDayFeed(day, today, chapters, small)), ['first', 'legacy', 'middle', 'other-batch', 'last']);
  assert.deepEqual(ids(buildDayFeed(day, today, [chapter('old')], [{ id: 'old-aha' }])), ['old', 'old-aha']);
});

test('nested highlight and playback identifiers cannot collide across imports', () => {
  const ch = chapter('c', { highlights: [{ id: 'h', text: 'keep', media: [{ id: 'clip', focusTimeSec: 4.5 }] }] });
  const a = scopeImportedMemories('a', [ch], [{ id: 's' }]);
  const b = scopeImportedMemories('b', [ch], [{ id: 's' }]);
  assert.equal(a.chapters[0].highlights[0].media[0].id, 'a:clip');
  assert.notEqual(a.chapters[0].highlights[0].id, b.chapters[0].highlights[0].id);
  assert.equal(ch.highlights[0].media[0].id, 'clip');
});

const { chapterMediaEntries } = require('../src/domain/chapterPresentation.ts');
test('highlight annotates its own selected frame once and keeps the original playback binding', () => {
  const main = { id: 'm', label: 'Moment 1', posterUri: 'frame.jpg', playbackUri: 'right.mp4' };
  const c = chapter('c', { moments: [main], highlights: [{ id: 'h', text: 'real detail',
    media: [{...main, id:'hm', focusTimeSec:4.5}] }, { id:'legacy',text:'older text' }] });
  const before=JSON.stringify(c),entries=chapterMediaEntries(c);
  assert.equal(entries.length,2);assert.equal(entries[0].media.playbackUri,'right.mp4');
  assert.equal(entries[0].media.focusTimeSec,4.5);assert.deepEqual(entries[0].texts,['real detail']);
  assert.equal(entries[1].media,undefined);assert.deepEqual(entries[1].texts,['older text']);
  assert.equal(JSON.stringify(c),before);
  c.highlights[0].media[0].posterUri='different-frame.jpg';
  assert.equal(chapterMediaEntries(c).filter(e=>e.media).length,2);
  c.highlights[0].media[0].posterUri='frame.jpg';c.highlights[0].media[0].playbackUri='different.mp4';
  assert.equal(chapterMediaEntries(c).filter(e=>e.media).length,2);
});
