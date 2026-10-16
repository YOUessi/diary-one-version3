import type { MemoryPreference } from '../model';
import { LIBRARY_TAGS, TAG_CATEGORIES, WRITING_STYLES, AVOID_TOPICS } from '../onboarding/tagLibrary';

/** Structured App → BFF → X02 preference contract (APP_CLIENT_PROFILE_V01). */
export type AppClientProfileV01 = {
  schema_version: 'APP_CLIENT_PROFILE_V01';
  memory_preferences: string[];
  boost_tags: string[];
  avoid_topics: string[];
  writing_style: string | null;
  preferred_categories: string[];
};

/** Serialize preferences for BFF / X02 `app_client_profile`. */
export function memoryPreferencesForUpload(preferences: MemoryPreference[]): string[] {
  return preferences.map((p) => (p.title ? `${p.title}: ${p.text}` : p.text));
}

export function buildAppClientProfile(preferences: MemoryPreference[]): AppClientProfileV01 {
  const memory_preferences = memoryPreferencesForUpload(preferences);
  const boost_tags: string[] = [];
  const avoid_topics: string[] = [];
  const preferred_categories: string[] = [];
  let writing_style: string | null = null;

  const tagLabelByLower = new Map(LIBRARY_TAGS.map((t) => [t.label.toLowerCase(), t.label]));
  const categoryByLower = new Map(TAG_CATEGORIES.map((c) => [c.label.toLowerCase(), c.label]));
  const styleByLower = new Map(WRITING_STYLES.map((s) => [s.label.toLowerCase(), s.label]));
  const avoidByLower = new Map(AVOID_TOPICS.map((a) => [a.label.toLowerCase(), a.label]));

  for (const pref of preferences) {
    const title = (pref.title || '').trim();
    const text = (pref.text || '').trim();
    const blob = `${title}\n${text}`;
    const lower = blob.toLowerCase();

    if (/writing style/i.test(title) || /writing style:/i.test(text)) {
      const m = blob.match(/writing style:\s*([^.\n]+)/i);
      if (m) {
        const hit = styleByLower.get(m[1].trim().toLowerCase());
        writing_style = hit ?? m[1].trim();
      }
    }

    if (/preferred content/i.test(title) || /prefer writing about:/i.test(text)) {
      const m = blob.match(/prefer writing about:\s*(.+)$/im);
      const chunk = m?.[1] ?? '';
      for (const part of chunk.split(',')) {
        const label = part.trim().replace(/\.$/, '');
        const hit = categoryByLower.get(label.toLowerCase());
        if (hit && !preferred_categories.includes(hit)) preferred_categories.push(hit);
        else if (label && !preferred_categories.includes(label)) preferred_categories.push(label);
      }
    }

    if (/interest tags/i.test(title) || /boost these tags/i.test(text)) {
      const m = blob.match(/boost these tags when evidence exists:\s*(.+)$/im);
      const chunk = m?.[1] ?? '';
      for (const part of chunk.split(',')) {
        const label = part.trim().replace(/\.$/, '');
        const hit = tagLabelByLower.get(label.toLowerCase());
        if (hit && !boost_tags.includes(hit)) boost_tags.push(hit);
        else if (label && !boost_tags.includes(label)) boost_tags.push(label);
      }
    }

    if (/^avoid:/i.test(title) || /avoid:/i.test(title) || /do not emphasize/i.test(text)) {
      const fromTitle = title.replace(/^avoid:\s*/i, '').trim();
      const hit = avoidByLower.get(fromTitle.toLowerCase());
      const label = hit ?? fromTitle;
      if (label && !avoid_topics.includes(label)) avoid_topics.push(label);
      else {
        for (const a of AVOID_TOPICS) {
          if (lower.includes(a.label.toLowerCase()) && !avoid_topics.includes(a.label)) {
            avoid_topics.push(a.label);
          }
        }
      }
    }
  }

  return {
    schema_version: 'APP_CLIENT_PROFILE_V01',
    memory_preferences,
    boost_tags,
    avoid_topics,
    writing_style,
    preferred_categories,
  };
}

export function profileHasSignals(profile: AppClientProfileV01): boolean {
  return (
    profile.memory_preferences.length > 0 ||
    profile.boost_tags.length > 0 ||
    profile.avoid_topics.length > 0 ||
    Boolean(profile.writing_style) ||
    profile.preferred_categories.length > 0
  );
}
