/**
 * Diary One · Onboarding tag library
 * Categories → positive tags (命中 tag 库)；Avoid topics → 负向提示词。
 * Tags are declaration signals for select/wording only — never invent day content.
 */

export type TagCategoryId =
  | 'daily_life'
  | 'personal_growth'
  | 'emotional'
  | 'travel'
  | 'relationships'
  | 'work_study'
  | 'health'
  | 'hobbies';

export type TagCategory = {
  id: TagCategoryId;
  label: string;
  /** Simple glyph for Expo Go (no custom icon pack required). */
  glyph: string;
};

export type LibraryTag = {
  id: string;
  label: string;
  categoryId: TagCategoryId;
};

export type AvoidTopic = {
  id: string;
  label: string;
  /** Negative prompt fragment sent with memory preferences. */
  negativePrompt: string;
};

export type WritingStyle = {
  id: string;
  label: string;
  description: string;
};

export const TAG_CATEGORIES: TagCategory[] = [
  { id: 'daily_life', label: 'Daily life', glyph: '☕' },
  { id: 'personal_growth', label: 'Personal growth', glyph: '🌱' },
  { id: 'emotional', label: 'Emotional reflection', glyph: '💭' },
  { id: 'travel', label: 'Travel & adventure', glyph: '✈️' },
  { id: 'relationships', label: 'Relationships', glyph: '👥' },
  { id: 'work_study', label: 'Work & study', glyph: '💼' },
  { id: 'health', label: 'Health & fitness', glyph: '🏃' },
  { id: 'hobbies', label: 'Hobbies & creativity', glyph: '🎨' },
];

/** Closed vocabulary — survey options must hit these ids. */
export const LIBRARY_TAGS: LibraryTag[] = [
  // Daily life
  { id: 'citywalk', label: 'Citywalk', categoryId: 'daily_life' },
  { id: 'coffee', label: 'Coffee', categoryId: 'daily_life' },
  { id: 'home_moments', label: 'Home moments', categoryId: 'daily_life' },
  { id: 'meals', label: 'Meals', categoryId: 'daily_life' },
  { id: 'errands', label: 'Everyday errands', categoryId: 'daily_life' },
  { id: 'pets', label: 'Pets', categoryId: 'daily_life' },
  // Personal growth
  { id: 'learning', label: 'Learning', categoryId: 'personal_growth' },
  { id: 'habits', label: 'Habits', categoryId: 'personal_growth' },
  { id: 'goals', label: 'Goals', categoryId: 'personal_growth' },
  { id: 'mindfulness', label: 'Mindfulness', categoryId: 'personal_growth' },
  { id: 'journaling', label: 'Self-reflection', categoryId: 'personal_growth' },
  // Emotional
  { id: 'calm', label: 'Calm moments', categoryId: 'emotional' },
  { id: 'gratitude', label: 'Gratitude', categoryId: 'emotional' },
  { id: 'mood', label: 'Mood shifts', categoryId: 'emotional' },
  { id: 'alone_time', label: 'Quiet alone time', categoryId: 'emotional' },
  // Travel
  { id: 'trips', label: 'Trips', categoryId: 'travel' },
  { id: 'nature', label: 'Nature', categoryId: 'travel' },
  { id: 'street_scenes', label: 'Street scenes', categoryId: 'travel' },
  { id: 'local_exploring', label: 'Local exploring', categoryId: 'travel' },
  // Relationships
  { id: 'family', label: 'Family', categoryId: 'relationships' },
  { id: 'friends', label: 'Friends', categoryId: 'relationships' },
  { id: 'partner', label: 'Partner', categoryId: 'relationships' },
  { id: 'shared_meals', label: 'Shared meals', categoryId: 'relationships' },
  // Work & study
  { id: 'desk_work', label: 'Desk work', categoryId: 'work_study' },
  { id: 'meetings', label: 'Meetings', categoryId: 'work_study' },
  { id: 'study', label: 'Study', categoryId: 'work_study' },
  { id: 'side_projects', label: 'Side projects', categoryId: 'work_study' },
  // Health
  { id: 'workout', label: 'Workout', categoryId: 'health' },
  { id: 'walk', label: 'Walking', categoryId: 'health' },
  { id: 'sleep', label: 'Rest', categoryId: 'health' },
  { id: 'cooking_healthy', label: 'Healthy cooking', categoryId: 'health' },
  // Hobbies
  { id: 'music', label: 'Music', categoryId: 'hobbies' },
  { id: 'photo', label: 'Photography', categoryId: 'hobbies' },
  { id: 'making', label: 'Making things', categoryId: 'hobbies' },
  { id: 'reading', label: 'Reading', categoryId: 'hobbies' },
  { id: 'games', label: 'Games', categoryId: 'hobbies' },
];

export const AVOID_TOPICS: AvoidTopic[] = [
  {
    id: 'commute',
    label: 'Repeated commuting',
    negativePrompt: 'Avoid emphasizing repeated commuting when other moments exist.',
  },
  {
    id: 'empty_landscape',
    label: 'Empty landscapes',
    negativePrompt: 'Avoid empty landscapes with no people when other moments exist.',
  },
  {
    id: 'long_meetings',
    label: 'Long indoor meetings',
    negativePrompt: 'Avoid long indoor meetings when other moments exist.',
  },
  {
    id: 'screens',
    label: 'Phone / screen-only scenes',
    negativePrompt: 'Avoid phone or screen-only scenes when other moments exist.',
  },
  {
    id: 'work_stress',
    label: 'Work stress detail',
    negativePrompt: 'Avoid dwelling on work-stress detail unless clearly central to the day.',
  },
  {
    id: 'arguments',
    label: 'Conflict / arguments',
    negativePrompt: 'Avoid highlighting interpersonal conflict unless the user also asked for it.',
  },
  {
    id: 'politics',
    label: 'Politics / news',
    negativePrompt: 'Avoid politics and news framing in memory copy.',
  },
  {
    id: 'medical',
    label: 'Medical / illness detail',
    negativePrompt: 'Avoid medical or illness detail in memory copy.',
  },
];

export const WRITING_STYLES: WritingStyle[] = [
  {
    id: 'empathetic',
    label: 'Empathetic and warm',
    description: 'Gentle, caring, and emotionally attentive.',
  },
  {
    id: 'logical',
    label: 'Logical and clear',
    description: 'Straightforward, factual, and easy to follow.',
  },
  {
    id: 'poetic',
    label: 'Creative and poetic',
    description: 'Imagery-led, expressive, and lyrical.',
  },
  {
    id: 'direct',
    label: 'Direct and objective',
    description: 'Plainspoken and observational, low fluff.',
  },
  {
    id: 'playful',
    label: 'Playful and witty',
    description: 'Light, witty, and lightly humorous.',
  },
  {
    id: 'reflective',
    label: 'Philosophical and reflective',
    description: 'Thoughtful, contemplative, and meaning-seeking.',
  },
];

export function tagsForCategories(categoryIds: string[]): LibraryTag[] {
  if (!categoryIds.length) return LIBRARY_TAGS;
  const set = new Set(categoryIds);
  return LIBRARY_TAGS.filter((t) => set.has(t.categoryId));
}

export function categoryLabel(id: string): string {
  return TAG_CATEGORIES.find((c) => c.id === id)?.label ?? id;
}

export function tagById(id: string): LibraryTag | undefined {
  return LIBRARY_TAGS.find((t) => t.id === id);
}

export function avoidById(id: string): AvoidTopic | undefined {
  return AVOID_TOPICS.find((t) => t.id === id);
}

export function styleById(id: string): WritingStyle | undefined {
  return WRITING_STYLES.find((s) => s.id === id);
}
