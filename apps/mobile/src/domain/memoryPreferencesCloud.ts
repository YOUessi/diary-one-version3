import type { MemoryPreference } from '../model';

/** Serialize preferences for BFF / X02 `app_client_profile.memory_preferences`. */
export function memoryPreferencesForUpload(preferences: MemoryPreference[]): string[] {
  return preferences.map((p) => (p.title ? `${p.title}: ${p.text}` : p.text));
}
