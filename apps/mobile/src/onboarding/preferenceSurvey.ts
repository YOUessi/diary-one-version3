/** ACC03 / PREF02 — light onboarding survey (meeting 2026-09-23).
 * Skippable. Writes Memory Preferences + consent only — never invents day content.
 */

export type SurveyStepKind = 'single' | 'multi' | 'text' | 'consent';

export type SurveyOption = { id: string; label: string };

export type SurveyStep = {
  id: string;
  kind: SurveyStepKind;
  title: string;
  lead: string;
  options?: SurveyOption[];
  /** Maps selected option ids → preference text lines */
  preferenceLines?: Record<string, string>;
  maxLength?: number;
};

export const PREFERENCE_SURVEY_STEPS: SurveyStep[] = [
  {
    id: 'moments',
    kind: 'single',
    title: 'What should Diary keep more of?',
    lead: 'This only guides how existing recordings are chosen and worded — it never invents moments you did not capture.',
    options: [
      { id: 'outdoors', label: 'Outdoors and travel' },
      { id: 'people', label: 'Family and time with people' },
      { id: 'work', label: 'Work and everyday routines' },
      { id: 'any', label: 'Whatever the day actually held' },
    ],
    preferenceLines: {
      outdoors: 'Prefer outdoor and travel moments when they exist.',
      people: 'Prefer family and shared moments when they exist.',
      work: 'Prefer work and everyday routine moments when they exist.',
      any: 'Follow the day as recorded; no strong category preference.',
    },
  },
  {
    id: 'less',
    kind: 'multi',
    title: 'What would you rather see less of?',
    lead: 'Optional. Matches “few and true” — not a daily quota.',
    options: [
      { id: 'commute', label: 'Repeated commuting' },
      { id: 'scape', label: 'Empty landscapes with no people' },
      { id: 'meeting', label: 'Long indoor meetings' },
      { id: 'none', label: 'No preference for now' },
    ],
    preferenceLines: {
      commute: 'De-emphasize repeated commuting when other moments exist.',
      scape: 'De-emphasize empty landscapes when other moments exist.',
      meeting: 'De-emphasize long indoor meetings when other moments exist.',
    },
  },
  {
    id: 'count',
    kind: 'single',
    title: 'At the end of a day, how many main memories feel right?',
    lead: 'Research only. The app still follows what was actually recorded — this does not force a count.',
    options: [
      { id: 'few', label: 'Fewer (1–2)' },
      { id: 'mid', label: 'About 3–4' },
      { id: 'real', label: 'No target — stay true to the day' },
    ],
  },
  {
    id: 'people_clues',
    kind: 'single',
    title: 'Are you open to “who was with you” clues later?',
    lead: 'Default stays off. Face or voice features need a separate permission if we ever ship them.',
    options: [
      { id: 'yes', label: 'Open to it later (with separate consent)' },
      { id: 'no', label: 'Not for now' },
    ],
  },
  {
    id: 'share',
    kind: 'single',
    title: 'When you share, what do you use most?',
    lead: 'Helps product priority only. You can still share any way later.',
    options: [
      { id: 'original', label: 'Original clips' },
      { id: 'collage', label: 'Photo collage' },
      { id: 'recap', label: 'Daily Recap video' },
      { id: 'rare', label: 'I rarely share' },
    ],
  },
  {
    id: 'notify',
    kind: 'single',
    title: 'Notifications',
    lead: 'No marketing. You can change this anytime in Account.',
    options: [
      { id: 'memories', label: 'Only when memories are ready' },
      { id: 'device', label: 'Memories ready and important device alerts' },
      { id: 'none', label: 'Neither for now' },
    ],
  },
  {
    id: 'open',
    kind: 'text',
    title: 'One sentence for Diary',
    lead: 'Optional. Stored as a Memory Preference — the same place as Account → Preferences.',
    maxLength: 150,
  },
  {
    id: 'consent',
    kind: 'consent',
    title: 'Cloud processing consent',
    lead:
      'To generate memories, Diary One may upload the smallest visual evidence from media you choose. Signing in is not the same as this consent.',
    options: [
      { id: 'agree', label: 'Agree and continue' },
      { id: 'local', label: 'Browse on this device only for now' },
    ],
  },
];

export type SurveyAnswers = {
  selections: Record<string, string[]>;
  openText: string;
};

export const EMPTY_SURVEY_ANSWERS: SurveyAnswers = {
  selections: {},
  openText: '',
};

export const CLOUD_EVIDENCE_CONSENT_VERSION = 'DIARY_ONE_CLOUD_EVIDENCE_V01';
