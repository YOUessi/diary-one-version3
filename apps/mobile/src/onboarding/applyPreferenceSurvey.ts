import { useAppStore } from '../store/useAppStore';
import { flushPersist } from '../store/hydrate';
import { EMPTY_SURVEY_ANSWERS, type SurveyAnswers } from './preferenceSurvey';
import { buildSurveyProfile, mergeSurveyPreferences } from './surveyProfile';

export function buildPreferenceLines(answers: SurveyAnswers): { title: string; text: string }[] {
  return buildSurveyProfile(answers).preferences.map(({ title, text }) => ({ title, text }));
}

async function writeSurveyPreferences(answers: SurveyAnswers, finish: boolean) {
  const initial = useAppStore.getState();
  const profile = buildSurveyProfile(answers);
  const preferences = mergeSurveyPreferences(initial.preferences, profile.preferences);
  const sameAccount = () => {
    const now = useAppStore.getState();
    return now.sessionToken === initial.sessionToken && now.localProfile.email === initial.localProfile.email;
  };
  useAppStore.setState({ preferences, preferenceSurveyResponse: profile.response });
  try {
    await flushPersist();
    if (!sameAccount()) throw new Error('Account changed. Please reopen preferences.');
    const completion = finish ? { preferenceSurveyComplete: true as const, onboardingComplete: true as const }
      : { preferenceSurveyComplete: true as const };
    // Persist completion before the root navigator can unmount this screen.
    await flushPersist(completion);
    if (!sameAccount()) throw new Error('Account changed. Please reopen preferences.');
    useAppStore.setState(completion);
  } catch (error) {
    if (sameAccount() && useAppStore.getState().preferences === preferences) {
      useAppStore.setState({ preferences: initial.preferences,
        preferenceSurveyResponse: initial.preferenceSurveyResponse,
        preferenceSurveyComplete: initial.preferenceSurveyComplete });
    }
    throw error;
  }
}

export async function applyPreferenceSurveyAndFinish(answers: SurveyAnswers) {
  await writeSurveyPreferences(answers, true);
}

export async function applyPreferenceSurveyFromAccount(answers: SurveyAnswers) {
  await writeSurveyPreferences(answers, false);
}

export async function skipPreferenceSurveyAndFinish() {
  await writeSurveyPreferences(EMPTY_SURVEY_ANSWERS, true);
}

/** Cancelling a retake does not change existing preferences. */
export function skipPreferenceSurveyFromAccount() {}
