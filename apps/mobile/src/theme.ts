// Diary One — D1 设计令牌（来源：Figma「02 Foundations」）
// 语义色优先，禁止在组件里写死十六进制；新颜色须先在令牌里登记。
export const colors = {
  paper: '#FAF9F6', // 背景（暖白）
  surface: '#F3F1EC', // 次级面 / 卡片内块
  card: '#FFFFFF', // 卡片
  ink: '#171717', // 主文字
  secondary: '#6B6B6B', // 次级文字
  tertiary: '#999999', // 三级 / 提示文字
  divider: '#E8E5DF', // 分隔线
  accent: '#C98245', // Warm Accent（强调，遵循 60/30/10）
  accentSoft: '#F1E4D6', // 强调色浅底
  headerBg: '#171717', // 顶部（品牌反白）
  ok: '#4C8C6A',
  warn: '#C98245',
} as const;

export const spacing = { xs: 4, sm: 8, md: 16, lg: 20, xl: 32 } as const;

export const layout = {
  gutterDiary: 20,
  minTouch: 44,
  buttonHeight: 48,
} as const;

export const radius = { control: 8, card: 12, sheet: 16, pill: 999 } as const;

export const font = {
  title: 26,
  h2: 19,
  body: 15,
  small: 13,
  micro: 11,
} as const;
