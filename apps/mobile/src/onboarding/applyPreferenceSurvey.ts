import { useAppStore } from '../store/useAppStore';
import {
  CLOUD_EVIDENCE_CONSENT_VERSION,
  type SurveyAnswers,
} from './preferenceSurvey';
import { avoidById, categoryLabel, styleById, tagById } from './tagLibrary';

export function buildPreferenceLines(answers: SurveyAnswers): { title: string; text: string }[] {
  const lines: { title: string; text: string }[] = [];

  if (answers.categories.length) {
    lines.push({
      title: 'Preferred content',
      text: `Prefer writing about: ${answers.categories.map(categoryLabel).join(', ')}.`,
    });
  }

  const tagLabels = answers.interestTags
    .map((id) => tagById(id)?.label)
    .filter((x): x is string => Boolean(x));
  if (tagLabels.length) {
    lines.push({
      title: 'Interest tags',
      text: `Boost these tags when evidence exists: ${tagLabels.join(', ')}.`,
    });
  }

  const style = answers.styleId ? styleById(answers.styleId) : undefined;
  if (style) {
    lines.push({
      title: 'Writing style',
      text: `Writing style: ${style.label}. ${style.description}`,
    });
  }

  for (const id of answers.avoidTopics) {
    const avoid = avoidById(id);
    if (avoid) {
      lines.push({
        title: `Avoid: ${avoid.label}`,
        text: avoid.negativePrompt,
      });
    }
  }

  const open = answers.openText.trim();
  if (open) {
    lines.push({
      title: 'What matters most',
      text: open.slice(0, 150),
    });
  }

  return lines;
}

function writeSurveyPreferences(answers: SurveyAnswers) {
  const lines = buildPreferenceLines(answers);
  if (lines.length > 0) {
    useAppStore.setState({
      preferences: lines.map((p, i) => ({
        id: `survey-${Date.now()}-${i}`,
        title: p.title,
        text: p.text,
      })),
    });
  }

  const cloudEvidenceConsent = answers.consent === 'agree';
  useAppStore.setState({
    cloudEvidenceConsent,
    cloudEvidenceConsentVersion: cloudEvidenceConsent ? CLOUD_EVIDENCE_CONSENT_VERSION : null,
    preferenceSurveyComplete: true,
  });
}

/** Apply survey from onboarding → Preferences + consent, then enter Diary. */
export function applyPreferenceSurveyAndFinish(answers: SurveyAnswers) {
  writeSurveyPreferences(answers);
  useAppStore.setState({
    onboardingComplete: true,
  });
}

/** Apply survey from Account retake — stay in Account, do not re-toggle onboarding. */
export function applyPreferenceSurveyFromAccount(answers: SurveyAnswers) {
  writeSurveyPreferences(answers);
}

export function skipPreferenceSurveyAndFinish() {
  useAppStore.setState({
    preferenceSurveyComplete: true,
    onboardingComplete: true,
  });
}

export function goToPreferenceSurveyOrFinish(
  navigate: (name: 'PreferenceSurvey', params: { step: number }) => void,
) {
  navigate('PreferenceSurvey', { step: 0 });
}
