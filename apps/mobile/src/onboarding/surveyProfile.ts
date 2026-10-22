import type { MemoryPreference, PreferenceSurveyResponse } from '../model';
import { MOMENT_OPTIONS, SHOW_LESS_OPTIONS, questionOneResponse, type SurveyAnswers } from './preferenceSurvey';
import { surveyTagByLabel } from './surveyTagLibrary';

const REASONS: Record<string, [string, string]> = {
  commutes: ['repetitive_commute', 'commute with repeated routes or similar clips over time'],
  meetings: ['long_low_density_work', 'work or meetings that are long with little action or scene change'],
  similar: ['similar_moments', 'visually or semantically similar moments repeatedly featured over time'],
  meals: ['routine_meals', 'repeated routine meals; preserve meaningful celebrations and achievements'],
  landscape: ['landscape_only', 'landscape-dominant scenes without significant action or events'],
  indoor: ['repetitive_indoor_routine', 'similar indoor routines with little change; do not infer home ownership'],
  rather_not: ['uncomfortable_content', 'only content the user explicitly identifies; do not infer the reason'],
};

export function buildSurveyProfile(answers: SurveyAnswers, updatedAt = new Date().toISOString()): {
  preferences: MemoryPreference[]; response: PreferenceSurveyResponse;
} {
  const preferences: MemoryPreference[] = [];
  const add = (key: string, title: string, text: string, scope: Omit<NonNullable<MemoryPreference['survey']>, 'source' | 'strength' | 'updated_at'>) => {
    preferences.push({ id: `survey-v15-${key}`, title, text,
      survey: { ...scope, source: 'preference_survey', strength: 1, updated_at: updatedAt } });
  };
  const response: PreferenceSurveyResponse = {
    question_1_response: questionOneResponse(answers),
    question_2_response: answers.showLessIds.includes('nothing') ? 'nothing_for_now' :
      answers.showLessIds.some(id => Boolean(REASONS[id])) ? 'selected' : 'skipped', updated_at: updatedAt,
  };
  if (response.question_1_response === 'selected') {
    for (const option of MOMENT_OPTIONS.filter(o => !o.exclusive && !o.opensCustom && answers.momentIds.includes(o.id))) {
      add(option.id, option.label, `Notice more ${option.label.toLowerCase()} when supported by captured content. This is a broad theme, not a declaration of every related activity or relationship.`,
        { polarity: 'like', theme_id: option.id, target_scope: `theme:${option.id}` });
    }
    if (answers.momentIds.includes('something_else')) {
      const raw = answers.customText.trim().slice(0, 150);
      if (raw) add('words', 'Your words', raw, { polarity: 'like', target_scope: 'private_expression' });
      for (const label of [...new Set(answers.suggestedLabels)]) {
        const tag = surveyTagByLabel(label);
        if (tag) add(tag.id, label, `Notice more ${label.toLowerCase()} only when evidence exists in captured content.`,
          { polarity: 'like', tag_id: tag.id, target_scope: `tag:${tag.id}` });
      }
    }
  }
  if (response.question_2_response === 'selected') {
    for (const id of [...new Set(answers.showLessIds)]) {
      const reason = REASONS[id];
      if (reason) add(id, SHOW_LESS_OPTIONS.find(o => o.id === id)!.label,
        `Show less often: ${reason[1]}. Lower featuring priority only; do not delete, block, or change capture settings.`,
        { polarity: 'avoid', preference_reason_id: reason[0], target_scope: reason[1] });
    }
  }
  return { preferences, response };
}

/** Replace questionnaire records only; hand-added preferences survive a retake. */
export function mergeSurveyPreferences(existing: MemoryPreference[], incoming: MemoryPreference[]): MemoryPreference[] {
  return [...existing.filter(p => !p.survey && !/^survey-/.test(p.id)), ...incoming];
}
