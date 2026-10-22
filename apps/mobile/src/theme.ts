// Diary One — D1 tokens locked to Figma Copy Foundations
// fileKey: mcPA0SAKRRJ3a1f6zwDO7Q (04 Screens / Design System 0916 Copy)
export const colors = {
  paper: '#FAF9F6', // --d1-color-background-base
  surface: '#ECE9E3', // --d1-color-background-subtle / media-placeholder
  card: '#FFFFFF', // --d1-color-background-elevated
  ink: '#171717', // --d1-color-text-primary / icon-primary
  secondary: '#6B6B6B', // --d1-color-text-secondary / icon-secondary
  tertiary: '#999999', // --d1-color-text-tertiary
  divider: '#E8E5DF', // --d1-color-border-subtle
  accent: '#C98245', // --d1-color-accent-fill
  accentSoft: '#F3E6D8', // --d1-color-accent-subtle
  headerBg: '#171717',
  ok: '#4C8C6A',
  warn: '#C98245',
  shadow: '#00000014',
} as const;

export const spacing = {
  xs: 4, // micro-gap
  sm: 8, // compact-gap
  md: 16, // content-gap
  lg: 20, // screen gutter
  xl: 24, // section gap (Today block)
  xxl: 28, // feed column gap
  xxxl: 32,
} as const;

export const layout = {
  gutterDiary: 20,
  contentWidth: 353,
  minTouch: 44,
  buttonHeight: 48,
  tabBarHeight: 64,
  heroHome: 198,
  heroDetail: 224,
  capturedPreviewW: 82,
  capturedPreviewH: 72,
} as const;

/** Elevation/Floating — Figma drop-shadow #00000014, y=4, blur=16 */
export const elevation = {
  floating: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 8,
  },
} as const;

export const radius = {
  control: 8,
  media: 12, // --d1-radius-media
  card: 12, // --d1-radius-card (Memory search)
  sheet: 16, // --d1-radius-sheet (Account profile card)
  pill: 999,
} as const;

/** Type ramp — sizes match Figma text styles */
export const font = {
  titleLarge: 34, // Title/Large — Diary header
  titleSection: 28, // Title/Section — Today / Chapter title on detail
  titleChapter: 22, // Title/Chapter — chapter card + section headers
  bodyStory: 17, // Body/Story
  bodyFragment: 16, // Body/Fragment — small memory
  caption: 13, // Caption/Primary + Emphasis
  metadata: 11, // Metadata/Small
  // aliases kept for existing screens
  title: 34,
  h2: 22,
  body: 17,
  small: 13,
  micro: 11,
} as const;

export const type = {
  titleLarge: { fontSize: 34, lineHeight: 40, fontWeight: '700' as const, letterSpacing: -0.3 },
  titleSection: { fontSize: 28, lineHeight: 34, fontWeight: '600' as const, letterSpacing: -0.2 },
  titleChapter: { fontSize: 22, lineHeight: 28, fontWeight: '600' as const, letterSpacing: -0.1 },
  bodyStory: { fontSize: 17, lineHeight: 24, fontWeight: '400' as const },
  bodyEmphasis: { fontSize: 17, lineHeight: 24, fontWeight: '500' as const },
  bodyFragment: { fontSize: 16, lineHeight: 23, fontWeight: '400' as const },
  caption: { fontSize: 13, lineHeight: 18, fontWeight: '400' as const },
  captionEmphasis: { fontSize: 13, lineHeight: 18, fontWeight: '500' as const },
  metadata: { fontSize: 11, lineHeight: 14, fontWeight: '400' as const, letterSpacing: 0.1 },
} as const;
