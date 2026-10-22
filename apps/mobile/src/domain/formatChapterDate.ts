import type { LanguagePreference } from './appSettings';
import { appLocale } from './strings';

/** Figma search / list: Aug 16, 2026 */
export function formatChapterDateLong(dateKey: string, language: LanguagePreference = 'en'): string {
  const [y, m, d] = dateKey.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString(appLocale(language), { month: 'short', day: 'numeric', year: 'numeric' });
}
