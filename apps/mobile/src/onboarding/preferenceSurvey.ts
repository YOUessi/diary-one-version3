/**
 * ACC03 / PREF02 — Figma Preference Onboarding (node 2145-2).
 * Skippable. Hits closed tag library + negative prompts → Memory Preferences.
 * Never invents Topics or day content.
 */
import {
  AVOID_TOPICS,
  TAG_CATEGORIES,
  WRITING_STYLES,
  type TagCategoryId,
} from './tagLibrary';

export type SurveyStepKind =
  | 'intro'
  | 'category_grid'
  | 'text'
  | 'tag_chips'
  | 'style_list'
  | 'avoid_chips'
  | 'review'
  | 'consent';

export type SurveyStep = {
  id: string;
  kind: SurveyStepKind;
  title: string;
  lead?: string;
};

/** Copy locked to Figma 2145 + Expo Go test guide §2.5 (8-category tag library). */
export const PREFERENCE_SURVEY_STEPS: SurveyStep[] = [
  {
    id: 'intro',
    kind: 'intro',
    title: 'Help Diary get to know you',
    lead:
      'Choose the moments you would like to remember. Diary only works with what was actually captured and will not make up anything that did not happen.',
  },
  {
    id: 'categories',
    kind: 'category_grid',
    title: 'Which kind of content do you like Diary to write more?',
    lead: 'Choose as many as you like. You can change this anytime in Settings.',
  },
  {
    id: 'open',
    kind: 'text',
    title: 'Anything else you’d like Diary to write for?',
    lead: 'Optional — a person, project, or goal. Stored with your Memory Preferences.',
  },
  {
    id: 'tags',
    kind: 'tag_chips',
    title: 'Select tags that you are interested in',
    lead: 'These hit Diary’s closed tag library. Choose tags that match what you hope to keep when evidence exists.',
  },
  {
    id: 'style',
    kind: 'style_list',
    title: 'What style of content do you like most?',
    lead: 'One primary voice for memory copy. You can change preferences later in Account.',
  },
  {
    id: 'avoid',
    kind: 'avoid_chips',
    title: 'Select topics Diary will not write for you',
    lead: 'Diary will de-emphasize these when other moments exist. Optional.',
  },
  {
    id: 'review',
    kind: 'review',
    title: 'Review your preferences',
    lead: 'Confirm what Diary will use as declared preferences. Nothing here creates fake memories.',
  },
  {
    id: 'consent',
    kind: 'consent',
    title: 'Cloud processing consent',
    lead:
      'To generate memories, Diary One may upload the smallest visual evidence from media you choose. Signing in is not the same as this consent.',
  },
];

export type SurveyAnswers = {
  /** Category ids from TAG_CATEGORIES */
  categories: TagCategoryId[];
  /** Positive library tag ids */
  interestTags: string[];
  /** Avoid topic ids */
  avoidTopics: string[];
  /** Writing style id */
  styleId: string | null;
  openText: string;
  /** consent: agree | local */
  consent: 'agree' | 'local' | null;
};

export const EMPTY_SURVEY_ANSWERS: SurveyAnswers = {
  categories: [],
  interestTags: [],
  avoidTopics: [],
  styleId: null,
  openText: '',
  consent: null,
};

export const CLOUD_EVIDENCE_CONSENT_VERSION = 'DIARY_ONE_CLOUD_EVIDENCE_V01';

export const SURVEY_OPEN_TEXT_MAX = 150;

export { TAG_CATEGORIES, AVOID_TOPICS, WRITING_STYLES };
