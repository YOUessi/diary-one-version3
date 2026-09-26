import { useAppStore } from '../store/useAppStore';
import {
  CLOUD_EVIDENCE_CONSENT_VERSION,
  PREFERENCE_SURVEY_STEPS,
  type SurveyAnswers,
} from './preferenceSurvey';
import type { NotificationSettings } from '../domain/appSettings';

/** Apply survey → Preferences + notifications + evidence consent, then enter Diary. */
export function applyPreferenceSurveyAndFinish(answers: SurveyAnswers) {
  const store = useAppStore.getState();
  const lines: { title: string; text: string }[] = [];

  for (const step of PREFERENCE_SURVEY_STEPS) {
    if (step.kind === 'text') {
      const t = answers.openText.trim();
      if (t) lines.push({ title: 'What matters most', text: t.slice(0, 150) });
      continue;
    }
    if (!step.preferenceLines) continue;
    const picked = answers.selections[step.id] ?? [];
    for (const id of picked) {
      const text = step.preferenceLines[id];
      if (text) lines.push({ title: 'From setup', text });
    }
  }

  if (lines.length > 0) {
    useAppStore.setState({
      preferences: lines.map((p, i) => ({
        id: `survey-${Date.now()}-${i}`,
        title: p.title,
        text: p.text,
      })),
    });
  }

  const notify = answers.selections.notify?.[0];
  let notificationSettings: NotificationSettings = {
    memoriesReady: true,
    deviceAlerts: false,
  };
  if (notify === 'memories') {
    notificationSettings = { memoriesReady: true, deviceAlerts: false };
  } else if (notify === 'device') {
    notificationSettings = { memoriesReady: true, deviceAlerts: true };
  } else if (notify === 'none') {
    notificationSettings = { memoriesReady: false, deviceAlerts: false };
  }

  const consent = answers.selections.consent?.[0];
  const cloudEvidenceConsent = consent === 'agree';
  const cloudEvidenceConsentVersion = cloudEvidenceConsent
    ? CLOUD_EVIDENCE_CONSENT_VERSION
    : null;

  store.setNotificationSettings(notificationSettings);
  useAppStore.setState({
    cloudEvidenceConsent,
    cloudEvidenceConsentVersion,
    preferenceSurveyComplete: true,
    onboardingComplete: true,
  });
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
