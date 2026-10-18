/** Controlled vocabulary from Tag自建库方案.md. Preferences never create content tags. */
export type SurveyTag = { id: string; label: string; aliases: string[] };
const tag = (id: string, label: string, aliases: string[] = []): SurveyTag => ({ id, label, aliases });
export const SURVEY_TAGS: SurveyTag[] = [
  tag('activity.sport', 'Sports', ['运动']),
  tag('activity.hiking', 'Hiking', ['徒步', '登山']),
  tag('activity.running', 'Running', ['跑步', '越野跑']),
  tag('activity.cycling', 'Cycling', ['骑行']),
  tag('activity.skateboarding', 'Skateboarding', ['滑板']),
  tag('activity.travel', 'Travel', ['旅行', '观光']),
  tag('activity.city_walk', 'City walks', ['citywalk', 'city walk', '城市漫步']),
  tag('activity.cultural_exploration', 'Cultural experiences', ['文化体验']),
  tag('activity.parent_child_time', 'Parent-child time', ['亲子互动']),
  tag('activity.family_gathering', 'Family gatherings', ['家庭聚会']),
  tag('activity.cooking', 'Cooking', ['烹饪', '做饭', '烘焙', 'baking']),
  tag('activity.pet_activity', 'Pet activities', ['宠物活动', '遛狗', '遛宠']),
  tag('activity.diy', 'DIY', ['model-building', 'model building', '模型制作', '模型拼装', '手工制作', '拼图']),
  tag('activity.painting', 'Painting', ['绘画', '插画']),
  tag('activity.trade_work', 'Trade work', ['工匠作业', '木工', '维修']),
  tag('activity.gardening', 'Gardening', ['园艺', '种菜', '播种']),
  tag('activity.fishing', 'Fishing', ['钓鱼', '垂钓', 'angling']),
  tag('activity.technology_trial', 'Technology trials', ['科技产品体验', '设备测试', 'AI 工具体验']),
  tag('participant.family', 'Family', ['家人']),
  tag('participant.friend', 'Friends', ['朋友']),
  tag('participant.pet', 'Pets', ['宠物']),
  ...[
    ['landscape', 'Landscapes', '景色'], ['mountain', 'Mountain views', '山景'],
    ['forest_landscape', 'Forest views', '森林景观'], ['river_landscape', 'River views', '河流景观'],
    ['lake_view', 'Lake views', '湖景'], ['ocean_view', 'Ocean views', '海景'],
    ['sunset', 'Sunsets', '日落'], ['wildlife', 'Wildlife', '野生动物'],
    ['architecture', 'Architecture', '建筑'], ['landmark', 'Landmarks', '地标'],
    ['museum', 'Museums', '博物馆'], ['handmade_work', 'Handmade work', '手工作品'],
    ['artwork', 'Artwork', '画作'], ['dish', 'Dishes', '菜肴'], ['plant', 'Plants', '植物'],
    ['flower', 'Flowers', '花'], ['tree', 'Trees', '树'], ['vegetable', 'Vegetables', '蔬菜'],
    ['fish', 'Fish', '鱼'], ['device', 'Devices', '设备'], ['software', 'Software', '软件'],
  ].map(([id, label, alias]) => tag(`subject.${id}`, label, [alias])),
  tag('setting.outdoors', 'Outdoors', ['户外']),
  tag('setting.mountain_area', 'Mountain areas', ['山地']),
  tag('setting.forest', 'Forests', ['森林']),
  tag('setting.waterside', 'Waterside', ['by the water', 'by the sea', '水边', '海边', '河边', '湖边']),
  tag('setting.city_street', 'City streets', ['城市街景']),
  tag('setting.indoors', 'Indoors', ['室内']),
  tag('setting.kitchen', 'Kitchens', ['厨房']),
  tag('setting.yard_garden', 'Yards & gardens', ['庭院与花园', '庭院']),
  tag('setting.construction_site', 'Construction sites', ['施工现场']),
  ...[
    ['key_moment', 'Key milestones', '关键进展'], ['completed_result', 'Completed results', '完成成果'],
    ['unexpected_event', 'Unexpected moments', '突发瞬间'], ['change', 'Changes', '状态变化'],
    ['discovery', 'Discoveries', '新发现'], ['first_time', 'First times', '第一次'],
  ].map(([id, label, alias]) => tag(`moment.${id}`, label, [alias])),
];

export function surveyTagByLabel(label: string): SurveyTag | undefined {
  return SURVEY_TAGS.find(t => t.label === label || t.aliases.includes(label));
}

function containsTerm(text: string, term: string): boolean {
  if (/[\u3400-\u9fff]/.test(term)) return text.includes(term);
  const escaped = term.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(^|[^a-z])${escaped}([^a-z]|$)`, 'i').test(text);
}

/** Literal, conservative suggestions; unknown names/expressions stay private raw text. */
export function suggestSurveyTags(text: string): string[] {
  return SURVEY_TAGS.filter(t => [t.label, ...t.aliases].some(a => containsTerm(text, a)))
    .slice(0, 3).map(t => t.label);
}

export function searchSurveyTags(query: string): SurveyTag[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return SURVEY_TAGS.filter(t => [t.label, ...t.aliases].some(a => a.toLowerCase().includes(q))).slice(0, 8);
}
