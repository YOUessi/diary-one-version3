/**
 * Preference Questionnaire — Figma Questionnaire screens (2149:18).
 * fileKey 7NSDFSkyxO38CaELtAtayL · Copy mcPA0SAKRRJ3a1f6zwDO7Q 同帧。
 * Welcome → Moments → (optional custom) → Show less → Summary.
 * Never invents Topics or day content from preferences alone.
 */

import { suggestSurveyTags } from './surveyTagLibrary';

export type QuestionnaireStepId =
  | 'welcome'
  | 'moments'
  | 'custom'
  | 'custom_review'
  | 'show_less'
  | 'summary';

export type PrefOption = {
  id: string;
  label: string;
  description: string;
  /** Exclusive with other options in the same stage when selected. */
  exclusive?: boolean;
  /** Selecting this opens the optional custom-words path. */
  opensCustom?: boolean;
};

/** Figma 2149:19 — Moments to remember */
export const MOMENT_OPTIONS: PrefOption[] = [
  {
    id: 'people',
    label: 'People who matter',
    description: 'Time with family, friends, and people close to you',
  },
  {
    id: 'pets',
    label: 'Time with pets',
    description: 'The moments you share with your pets',
  },
  {
    id: 'travel',
    label: 'Travel & exploring',
    description: 'Trips, city walks, and places you discover',
  },
  {
    id: 'sports',
    label: 'Sports & movement',
    description: 'Hikes, runs, rides, and other active moments',
  },
  {
    id: 'creative',
    label: 'Creative activities',
    description: 'Making, painting, and working on projects',
  },
  {
    id: 'nature',
    label: 'Nature & living things',
    description: 'Landscapes, plants, and wildlife',
  },
  {
    id: 'something_else',
    label: 'Something else',
    description: 'Tell Diary in your own words',
    opensCustom: true,
  },
  {
    id: 'follow_day',
    label: 'No preference — follow my day',
    description: 'Let Diary decide based on what actually happened',
    exclusive: true,
  },
];

/** Figma 2149:95 — Show less often */
export const SHOW_LESS_OPTIONS: PrefOption[] = [
  {
    id: 'commutes',
    label: 'Repetitive commutes',
    description: 'The same route, day after day',
  },
  {
    id: 'meetings',
    label: 'Long work sessions or meetings',
    description: 'Lengthy moments with little change',
  },
  {
    id: 'similar',
    label: 'Too many similar moments',
    description: 'Keep only the highlights',
  },
  {
    id: 'meals',
    label: 'Everyday meals',
    description: 'Routine meals without much change',
  },
  {
    id: 'landscape',
    label: 'Landscape-only scenes',
    description: 'Scenery without an event',
  },
  {
    id: 'indoor',
    label: 'Repetitive indoor routines',
    description: 'Similar everyday indoor moments',
  },
  {
    id: 'rather_not',
    label: 'Something I’d rather not revisit',
    description: 'You don’t have to explain why',
  },
  {
    id: 'nothing',
    label: 'Nothing for now',
    description: 'No need to set this now',
    exclusive: true,
  },
];

export type SurveyAnswers = {
  momentIds: string[];
  showLessIds: string[];
  /** Free-text from Something else / optional custom step */
  customText: string;
  /** Local suggestions derived from customText (not claimed as facts) */
  suggestedLabels: string[];
  /** Suggestions already shown for these words; prevents restoring removed chips on Back. */
  reviewedText?: string;
  /** Explicit search choices survive edits to the free-text field. */
  searchedLabels?: string[];
};

export const EMPTY_SURVEY_ANSWERS: SurveyAnswers = {
  momentIds: [],
  showLessIds: [],
  customText: '',
  suggestedLabels: [],
};

export const CLOUD_EVIDENCE_CONSENT_VERSION = 'DIARY_ONE_CLOUD_EVIDENCE_V01';

export const SURVEY_OPEN_TEXT_MAX = 150;

export const INTRO_POINTS = [
  'Takes about 1–2 minutes',
  'You can skip this step',
  'You can change these preferences anytime',
] as const;

export function momentById(id: string): PrefOption | undefined {
  return MOMENT_OPTIONS.find((o) => o.id === id);
}

export function showLessById(id: string): PrefOption | undefined {
  return SHOW_LESS_OPTIONS.find((o) => o.id === id);
}

/** Short labels for summary chips (Figma shortens some). */
export function showLessChipLabel(id: string): string {
  if (id === 'similar') return 'Similar moments';
  return showLessById(id)?.label ?? id;
}

/**
 * Lightweight local suggestions from the user’s own words.
 * Never invents diary content — only keyword chips for preference signals.
 */
export function suggestLabelsFromCustom(text: string): string[] {
  return suggestSurveyTags(text);
}

export function clearCustomAnswers(answers: SurveyAnswers): SurveyAnswers {
  return { ...answers, customText: '', suggestedLabels: [], searchedLabels: [], reviewedText: undefined };
}

/** Something else is an entry point, never a seventh theme. */
export function questionOneResponse(answers: SurveyAnswers): 'selected' | 'no_preference' | 'skipped' {
  if (answers.momentIds.includes('follow_day')) return 'no_preference';
  if (answers.momentIds.some(id => MOMENT_OPTIONS.some(o => o.id === id && !o.opensCustom && !o.exclusive)) ||
    (answers.momentIds.includes('something_else') && (answers.customText.trim() || answers.suggestedLabels.length))) return 'selected';
  return 'skipped';
}

export function surveyHasAnswers(answers: SurveyAnswers): boolean {
  return questionOneResponse(answers) !== 'skipped' || answers.showLessIds.length > 0;
}

export function togglePrefOption(
  selected: string[],
  option: PrefOption,
  all: PrefOption[],
): string[] {
  const on = selected.includes(option.id);
  if (on) return selected.filter((id) => id !== option.id);
  if (option.exclusive) return [option.id];
  const withoutExclusive = selected.filter(
    (id) => !all.find((o) => o.id === id)?.exclusive,
  );
  return [...withoutExclusive, option.id];
}

export function nextQuestionnaireStep(
  current: QuestionnaireStepId,
  answers: SurveyAnswers,
): QuestionnaireStepId | 'done' {
  switch (current) {
    case 'welcome':
      return 'moments';
    case 'moments':
      return answers.momentIds.includes('something_else') ? 'custom' : 'show_less';
    case 'custom':
      return answers.customText.trim() || answers.suggestedLabels.length ? 'custom_review' : 'show_less';
    case 'custom_review':
      return 'show_less';
    case 'show_less':
      return 'summary';
    case 'summary':
      return 'done';
    default:
      return 'done';
  }
}

export function stageMeta(step: QuestionnaireStepId): {
  stageLabel: string;
  filledSegments: number;
  showBack: boolean;
} {
  switch (step) {
    case 'welcome':
      return { stageLabel: '', filledSegments: 0, showBack: false };
    case 'moments':
      return { stageLabel: 'STAGE 1 OF 3', filledSegments: 1, showBack: true };
    case 'custom':
    case 'custom_review':
      return {
        stageLabel: 'STAGE 1 OF 3 · OPTIONAL',
        filledSegments: 1,
        showBack: true,
      };
    case 'show_less':
      return { stageLabel: 'STAGE 2 OF 3', filledSegments: 2, showBack: true };
    case 'summary':
      return {
        stageLabel: 'STAGE 3 OF 3 · REVIEW',
        filledSegments: 3,
        showBack: true,
      };
    default:
      return { stageLabel: '', filledSegments: 0, showBack: false };
  }
}

/** @deprecated Legacy 8-step index — map to questionnaire ids for old deep links. */
export function stepIndexToId(step: number): QuestionnaireStepId {
  const map: QuestionnaireStepId[] = [
    'welcome',
    'moments',
    'custom',
    'custom_review',
    'show_less',
    'summary',
  ];
  return map[Math.max(0, Math.min(map.length - 1, step))] ?? 'welcome';
}

export function stepIdToIndex(id: QuestionnaireStepId): number {
  const map: QuestionnaireStepId[] = [
    'welcome',
    'moments',
    'custom',
    'custom_review',
    'show_less',
    'summary',
  ];
  return Math.max(0, map.indexOf(id));
}
