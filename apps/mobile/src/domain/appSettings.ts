export type NotificationSettings = {
  memoriesReady: boolean;
  deviceAlerts: boolean;
};

export type LanguagePreference = 'en' | 'zh-Hans' | 'system';

export type MemoryLanguagePreference = LanguagePreference | 'same_as_app';

export type AutomaticCaptureMode = 'standard' | 'high';

export const DEFAULT_NOTIFICATION_SETTINGS: NotificationSettings = {
  memoriesReady: true,
  deviceAlerts: false,
};

export const DEFAULT_LANGUAGE: LanguagePreference = 'en';

export const DEFAULT_MEMORY_LANGUAGE: MemoryLanguagePreference = 'same_as_app';

export const DEFAULT_AUTOMATIC_CAPTURE_MODE: AutomaticCaptureMode = 'standard';

export function memoryLanguageDisplayLabel(code: MemoryLanguagePreference): string {
  if (code === 'same_as_app') return 'Same as app';
  return languageDisplayLabel(code);
}

export function languageDisplayLabel(code: LanguagePreference): string {
  switch (code) {
    case 'en':
      return 'English';
    case 'zh-Hans':
      return '简体中文';
    case 'system':
      return 'System default';
    default:
      return 'English';
  }
}
