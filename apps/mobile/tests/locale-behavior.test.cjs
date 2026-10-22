const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
require.extensions['.ts'] = (module, file) => module._compile(ts.transpileModule(
  fs.readFileSync(file, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText, file);
const { appStrings, momentLabel } = require('../src/domain/strings.ts');
const { buildDayFeed } = require('../src/diary/buildDiaryFeed.ts');
const { pipelineTaskLabel, pipelineTaskDetail } = require('../src/domain/pipelineCopy.ts');
const { DEFAULT_LANGUAGE } = require('../src/domain/appSettings.ts');

test('language changes derive display labels without translating authored content', () => {
  assert.equal(DEFAULT_LANGUAGE, 'zh-Hans');
  assert.equal(appStrings('en').play, 'Play');
  assert.equal(appStrings('zh-Hans').play, '播放');
  assert.equal(momentLabel('Moment 2 · Motion', 'zh-Hans'), '片段 2 · 视频');
  assert.equal(momentLabel('Moment 2 · Motion', 'en'), 'Moment 2 · Motion');
  assert.equal(momentLabel('Moment with my family', 'zh-Hans'), 'Moment with my family');
  const chapter = { id: '1', dateKey: '2026-10-20', aiStory: 'Keep my original words.' };
  const zh = buildDayFeed('2026-10-20', '2026-10-20', [chapter], [], 'zh-Hans');
  const en = buildDayFeed('2026-10-20', '2026-10-20', [chapter], [], 'en');
  assert.equal(zh[0].label, '今天');
  assert.equal(en[0].label, 'Today');
  assert.equal(zh[1].chapter, chapter);
  assert.equal(en[1].chapter, chapter);
});

test('a successful empty cloud result is never labelled as a newly saved memory', () => {
  assert.equal(pipelineTaskLabel({ status: 'succeeded', message: 'Cloud OK but 0 memories · prior day kept' }, 'zh-Hans'), '暂未生成新的记忆');
  assert.equal(pipelineTaskLabel({ status: 'succeeded', message: 'Diary updated · 1 memories' }, 'zh-Hans'), '已保存到日记');
  assert.equal(pipelineTaskLabel({ status: 'failed', message: 'Pipeline failed' }, 'zh-Hans'), '处理未完成');
});

const { summarizeDelivery } = require('../src/cloud/summarizeDelivery.ts');
const { mapTodayStatusFromPreview } = require('../src/cloud/mapTodayStatus.ts');
for (const delivery of ['READY_WITH_ITEM_BLOCKS', 'READY_WITH_GROUNDED_COPY_FALLBACK']) {
  test(`partial delivery remains visible with COMPLETE coverage and prior diary: ${delivery}`, () => {
    const result = { chapters: [], ahas: [{publication_status: 'STAGED_PREVIEW_VALIDATED'}],
      selected_memory_outcomes: [{visibility_state: 'VISIBLE_PREVIEW'}],
      delivery_state: delivery, coverage_status: 'COMPLETE' };
    const summary = summarizeDelivery(result);
    assert.equal(summary.outcome, 'partial');
    assert.equal(mapTodayStatusFromPreview(result, {preservedPriorReady: true}), 'PARTIAL');
    const task = {status: 'succeeded', message: 'Diary saved', deliverySummary: summary};
    assert.equal(pipelineTaskLabel(task, 'zh-Hans'), '部分内容已保存');
    assert.match(pipelineTaskDetail(task, 'zh-Hans'), /尚未全部完成/);
    assert.equal(pipelineTaskLabel(task, 'en'), 'Partially saved');
  });
}
test('empty failed delivery is distinguished from an honest empty result', () => {
  const result = {chapters: [], ahas: [], selected_memory_outcomes: [], delivery_state: 'NO_GROUNDED_MEMORY'};
  let task = {status: 'succeeded', message: 'Resumed · empty day · prior kept', deliverySummary: summarizeDelivery(result)};
  assert.equal(pipelineTaskLabel(task, 'zh-Hans'), '暂未生成新的记忆');
  result.coverage_status = 'PARTIAL_UNRESOLVED'; task.deliverySummary = summarizeDelivery(result);
  assert.equal(pipelineTaskLabel(task, 'zh-Hans'), '本次未能保存新记忆，仍有待处理项');
  assert.match(pipelineTaskDetail(task, 'zh-Hans'), /证据检查尚未完成/);
  assert.equal(mapTodayStatusFromPreview(result, {preservedPriorReady: true}), 'PARTIAL');
});
test('legacy task message still exposes partial status instead of saved', () => {
  assert.equal(pipelineTaskLabel({status: 'succeeded', message: 'Diary updated · READY_WITH_ITEM_BLOCKS'}, 'zh-Hans'), '部分记忆尚未完成。');
});


test('photo normalization failure is actionable in the selected language', () => {
  const task = {status: 'failed', error: 'CLOUD_JOB_FAILED:result_contract_rejected:evidence_format_or_dimensions_mismatch'};
  assert.match(pipelineTaskDetail(task, 'zh-Hans'), /图片未能转换/);
  assert.match(pipelineTaskDetail(task, 'en'), /image could not be converted/);
  assert.doesNotMatch(pipelineTaskDetail(task, 'zh-Hans'), /CLOUD_JOB|contract_rejected/);
  task.error = 'EVIDENCE_IMAGE_MODULE_MISSING';
  assert.match(pipelineTaskDetail(task, 'zh-Hans'), /更新/);
});

test('new photo encoding has a stable distinct revision while video identity remains unchanged', () => {
  const { selectionFingerprint } = require('../src/domain/dayRevision.ts');
  const media = {uri:'file:///same-selection.jpg',fileSize:90000};
  const old = selectionFingerprint([media]);
  const current = selectionFingerprint([{...media,mediaType:'image'}]);
  assert.notEqual(current,old);
  assert.equal(selectionFingerprint([{...media,mediaType:'image'}]),current);
  assert.equal(selectionFingerprint([{...media,mediaType:'video'}]),old);
});
