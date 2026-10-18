const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const Module = require('node:module');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(
  fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } },
).outputText, filename);
const survey = require('../src/onboarding/preferenceSurvey.ts');
const tags = require('../src/onboarding/surveyTagLibrary.ts');
const { buildSurveyProfile, mergeSurveyPreferences } = require('../src/onboarding/surveyProfile.ts');
const draft = extra => ({ ...survey.EMPTY_SURVEY_ANSWERS, ...extra });

test('exclusive responses work in both directions for both questions', () => {
  for (const [options, first, exclusive] of [
    [survey.MOMENT_OPTIONS, 'people', 'follow_day'], [survey.SHOW_LESS_OPTIONS, 'commutes', 'nothing'],
  ]) {
    const select = (ids, id) => survey.togglePrefOption(ids, options.find(o => o.id === id), options);
    assert.deepEqual(select([first], exclusive), [exclusive]);
    assert.deepEqual(select([exclusive], first), [first]);
    assert.deepEqual(select([first], first), []);
  }
});
test('conditional paths include tag-only review and preserve themes when custom is skipped', () => {
  assert.equal(survey.nextQuestionnaireStep('moments', draft({ momentIds: ['people'] })), 'show_less');
  const custom = draft({ momentIds: ['people', 'something_else'], customText: 'Fishing', suggestedLabels: ['Fishing'] });
  assert.equal(survey.nextQuestionnaireStep('moments', custom), 'custom');
  assert.equal(survey.nextQuestionnaireStep('custom', draft({ suggestedLabels: ['Fishing'] })), 'custom_review');
  assert.equal(survey.nextQuestionnaireStep('custom', draft()), 'show_less');
  assert.deepEqual(survey.clearCustomAnswers(custom).momentIds, custom.momentIds);
  assert.equal(survey.clearCustomAnswers(custom).customText, '');
});
test('skipped, explicit no preference, Nothing for now and empty Something else remain distinct', () => {
  assert.equal(buildSurveyProfile(draft()).response.question_1_response, 'skipped');
  const none = buildSurveyProfile(draft({ momentIds: ['follow_day'], showLessIds: ['nothing'] }));
  assert.equal(none.response.question_1_response, 'no_preference');
  assert.equal(none.response.question_2_response, 'nothing_for_now');
  assert.deepEqual(none.preferences, []);
  assert.equal(survey.questionOneResponse(draft({ momentIds: ['something_else'] })), 'skipped');
});
test('themes never expand into concrete tags; entry/default choices produce no preference cards', () => {
  const profile = buildSurveyProfile(draft({ momentIds: ['people', 'sports', 'something_else'] }));
  assert.equal(profile.preferences.length, 2);
  assert(profile.preferences.every(p => p.survey.theme_id && !p.survey.tag_id));
  assert.equal(profile.response.question_1_response, 'selected');
});
test('literal matching uses standard IDs, has no substring guesses and keeps unknown names private', () => {
  assert.deepEqual(tags.suggestSurveyTags('I’d like to remember fishing by the water.'), ['Fishing', 'Waterside']);
  assert.deepEqual(tags.suggestSurveyTags('education research model citizens'), []);
  assert.deepEqual(tags.suggestSurveyTags('walks by the sea with Dou Dou'), ['Waterside']);
  assert.equal(tags.surveyTagByLabel('model-building').id, 'activity.diy');
  assert(tags.searchSurveyTags('钓').some(t => t.id === 'activity.fishing'));
  const raw = 'walks by the sea with Dou Dou';
  const profile = buildSurveyProfile(draft({ momentIds: ['something_else'], customText: raw, suggestedLabels: ['Waterside'] }));
  assert(profile.preferences.some(p => p.text === raw && !p.survey.tag_id));
  assert(!profile.preferences.some(p => p.survey.tag_id === 'participant.pet'));
});
test('negative reasons remain scoped soft preferences, including uncomfortable content without guessing why', () => {
  const profile = buildSurveyProfile(draft({ momentIds: ['nature'], showLessIds: ['landscape', 'rather_not', 'meals'] }));
  assert(profile.preferences.some(p => p.survey.theme_id === 'nature'));
  const avoid = profile.preferences.filter(p => p.survey.polarity === 'avoid');
  assert.equal(avoid.length, 3);
  assert(avoid.every(p => p.survey.preference_reason_id && !p.survey.tag_id));
  assert(avoid.find(p => p.survey.preference_reason_id === 'uncomfortable_content').text.includes('do not infer'));
});
test('retake replaces only questionnaire records, including when new response is empty', () => {
  const manual = { id: 'p-manual', title: 'Mine', text: 'My manually added preference' };
  const old = buildSurveyProfile(draft({ momentIds: ['people'] })).preferences;
  assert.deepEqual(mergeSurveyPreferences([manual, ...old, { id: 'survey-legacy', title: 'Old', text: 'Old' }], []), [manual]);
});

// Exercise actual save orchestration with an isolated account store and persistence adapter.
const originalLoad = Module._load;
let state;
let persist;
Module._load = function(name, ...args) {
  if (name === '../store/useAppStore') return { useAppStore: { getState: () => state,
    setState: patch => { state = { ...state, ...patch }; } } };
  if (name === '../store/hydrate') return { flushPersist: completion => persist(completion) };
  return originalLoad.call(this, name, ...args);
};
const apply = require('../src/onboarding/applyPreferenceSurvey.ts');
Module._load = originalLoad;
const initial = () => ({ sessionToken: 'a', localProfile: { email: 'a@example.com' }, preferences: [],
  preferenceSurveyResponse: null, preferenceSurveyComplete: false, onboardingComplete: false,
  cloudEvidenceConsent: null });
test('saving waits for storage and preserves privacy; failure restores previous preferences', async () => {
  state = initial();
  let calls = 0;
  persist = async completion => {
    calls++; assert.equal(state.onboardingComplete, false);
    if (calls === 2) assert.deepEqual(completion, { preferenceSurveyComplete: true, onboardingComplete: true });
  };
  await apply.applyPreferenceSurveyAndFinish(draft({ momentIds: ['people'] }));
  assert.equal(calls, 2);
  assert.equal(state.onboardingComplete, true);
  assert.equal(state.cloudEvidenceConsent, null);
  const before = state;
  persist = async () => { throw new Error('disk full'); };
  await assert.rejects(apply.applyPreferenceSurveyFromAccount(draft()), /disk full/);
  assert.equal(state.preferences, before.preferences);
  assert.equal(state.preferenceSurveyResponse, before.preferenceSurveyResponse);
});
test('account switch while saving never rolls questionnaire data into the new account', async () => {
  state = initial();
  persist = async () => { state = { ...initial(), sessionToken: 'b', localProfile: { email: 'b@example.com' } }; };
  await assert.rejects(apply.applyPreferenceSurveyAndFinish(draft({ momentIds: ['people'] })), /Account changed/);
  assert.deepEqual(state.preferences, []);
  assert.equal(state.onboardingComplete, false);
});
