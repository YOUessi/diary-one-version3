import type { LanguagePreference } from './appSettings';

const EN = {
  tabDiary: 'Diary',
  tabMemory: 'Memory',
  tabDevice: 'Device',
  tabAccount: 'Account',
};

const ZH: typeof EN = {
  tabDiary: '日记',
  tabMemory: '记忆',
  tabDevice: '设备',
  tabAccount: '账户',
};

export function appStrings(language: LanguagePreference) {
  if (language === 'zh-Hans') return ZH;
  return EN;
}
