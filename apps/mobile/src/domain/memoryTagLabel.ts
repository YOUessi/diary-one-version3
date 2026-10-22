import type { LanguagePreference } from './appSettings';

// Presentation labels for the cloud's frozen concept registry. Keep canonical
// IDs in saved data so language changes do not break search or topic grouping.
const LABELS: Record<string, readonly [string, string]> = {
  'ACTIVITY.WALKING': ['Walking', '步行'],
  'ACTIVITY.CITY_WALK': ['Citywalk', '城市漫步'],
  'ACTIVITY.CRAFT': ['Crafts', '手作'],
  'ACTIVITY.POTTERY': ['Pottery', '陶艺'],
  'ACTIVITY.SHARED_MEAL': ['Shared meal', '一起用餐'],
  'SETTING.TRADITIONAL_HISTORIC_DISTRICT': ['Historic district', '古镇街区'],
  'SETTING.CAFE_OR_TEA_SHOP': ['Café or tea shop', '咖啡茶饮店'],
  'SETTING.HOME': ['Home', '家中'],
  'SETTING.OUTDOOR_NATURE': ['Outdoors', '自然户外'],
  'SETTING.WORKPLACE': ['Workplace', '工作场所'],
  'CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE': ['Historic architecture', '传统建筑'],
  'CENTRAL_SUBJECT.CAT': ['Cats', '猫咪'],
  'CENTRAL_SUBJECT.DOG': ['Dogs', '狗狗'],
  'CENTRAL_SUBJECT.FOOD_OR_DESSERT': ['Food and dessert', '食物甜点'],
  'CENTRAL_SUBJECT.CRAFT_OBJECT': ['Handmade objects', '手作作品'],
  'OCCASION.TRAVEL_OUTING': ['Outing', '旅行出游'],
  'OCCASION.BIRTHDAY': ['Birthday', '生日'],
  'OCCASION.FAMILY_GATHERING': ['Family gathering', '家庭相聚'],
};

export function memoryTagLabel(label: string, language: LanguagePreference): string | null {
  const canonical = label.trim();
  const known = Object.hasOwn(LABELS, canonical) ? LABELS[canonical] : undefined;
  // Follow the current app's language fallback (system defaults to English).
  if (known) return known[language === 'zh-Hans' ? 1 : 0];
  if (/^[A-Z][A-Z_]*\.[A-Z][A-Z0-9_]*$/.test(canonical)) return null;
  return canonical || null;
}
