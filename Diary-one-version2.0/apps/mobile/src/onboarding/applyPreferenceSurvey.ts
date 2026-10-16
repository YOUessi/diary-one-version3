import { useAppStore } from '../store/useAppStore';
import {
  momentById,
  showLessById,
  showLessChipLabel,
  type SurveyAnswers,
} from './preferenceSurvey';

export function buildPreferenceLines(answers: SurveyAnswers): { title: string; text: string }[] {
  const lines: { title: string; text: string }[] = [];

  const momentLabels = answers.momentIds
    .map((id) => momentById(id)?.label)
    .filter((x): x is string => Boolean(x));
  if (momentLabels.length) {
    lines.push({
      title: 'Notice more',
      text: `Prefer featuring: ${momentLabels.join(', ')}.`,
    });
  }

  const custom = answers.customText.trim();
  if (custom) {
    lines.push({
      title: 'Your words',
      text: custom.slice(0, 150),
    });
  }

  if (answers.suggestedLabels.length) {
    lines.push({
      title: 'Suggested preferences',
      text: `Boost when evidence exists: ${answers.suggestedLabels.join(', ')}.`,
    });
  }

  const lessLabels = answers.showLessIds
    .filter((id) => id !== 'nothing')
    .map((id) => showLessChipLabel(id) || showLessById(id)?.label)
    .filter((x): x is string => Boolean(x));
  if (lessLabels.length) {
    lines.push({
      title: 'Show less often',
      text: `De-emphasize when other moments exist: ${lessLabels.join(', ')}.`,
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

  useAppStore.setState({
    preferenceSurveyComplete: true,
  });
}

/** Apply survey from onboarding → Preferences, then enter Diary. */
export function applyPreferenceSurveyAndFinish(answers: SurveyAnswers) {
  writeSurveyPreferences(answers);
  useAppStore.setState({
    onboardingComplete: true,
  });
}

/** Apply survey from Account retake — stay in Account. */
export function applyPreferenceSurveyFromAccount(answers: SurveyAnswers) {
  writeSurveyPreferences(answers);
}

export function skipPreferenceSurveyAndFinish() {
  useAppStore.setState({
    preferenceSurveyComplete: true,
    onboardingComplete: true,
  });
}

/** Account retake skip — record completion without inventing preferences. */
export function skipPreferenceSurveyFromAccount() {
  useAppStore.setState({
    preferenceSurveyComplete: true,
  });
}
