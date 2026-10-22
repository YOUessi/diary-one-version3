const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(
  fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText, filename);
const { chapterSlides } = require('../src/domain/chapterSlides.ts');
const grass = { id: 'grass', label: '草地', posterUri: 'file:///grass.jpg', playbackUri: 'file:///grass.mp4' };
const train = { id: 'train', label: '火车', posterUri: 'file:///train.jpg', playbackUri: 'file:///train.mp4' };

test('train cover plays its matching second original, not the first grass clip', () => {
  const slides = chapterSlides({ heroUri: train.posterUri, moments: [grass, train] });
  assert.equal(slides[0].playbackUri, train.playbackUri);
  assert.equal(slides[0].title, train.label);
  assert.deepEqual(slides.map(s => s.posterUri), [train.posterUri, grass.posterUri]);
});
test('unmatched or ambiguously linked cover never plays an unrelated original', () => {
  assert.equal(chapterSlides({ heroUri: 'file:///other.jpg', moments: [grass, train] })[0].playbackUri, undefined);
  assert.equal(chapterSlides({ heroUri: train.posterUri, moments: [train, { ...grass, posterUri: train.posterUri }] })[0].playbackUri, undefined);
});
test('missing cover, photos, video-only and empty chapters remain usable', () => {
  assert.equal(chapterSlides({ moments: [grass, train] })[0].playbackUri, grass.playbackUri);
  assert.equal(chapterSlides({ heroUri: 'photo.jpg', moments: [{ id: 'p', label: '照片', posterUri: 'photo.jpg' }] })[0].playbackUri, undefined);
  assert.equal(chapterSlides({ moments: [{ id: 'v', label: '视频', playbackUri: 'clip.mp4' }] })[0].playbackUri, 'clip.mp4');
  assert.deepEqual(chapterSlides({ moments: [] }), []);
});
