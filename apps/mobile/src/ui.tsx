// Diary One — 共享展示组件（对应 Figma 六个核心组件的骨架版）
import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, spacing, radius, font, layout } from './theme';

export function Screen({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <SafeAreaView style={s.screen} edges={['top']}>
      <View style={s.header}>
        <Text style={s.headerTitle}>{title}</Text>
        {subtitle ? <Text style={s.headerSub}>{subtitle}</Text> : null}
      </View>
      <View style={s.body}>{children}</View>
    </SafeAreaView>
  );
}

export function SectionTitle({ children }: { children: React.ReactNode }) {
  return <Text style={s.sectionTitle}>{children}</Text>;
}

// C01 Tag —— 元数据，不是按钮：无按压态、无 chevron、不响应点击
export function Tag({ label }: { label: string }) {
  return (
    <View style={s.tag}>
      <Text style={s.tagText}>{label}</Text>
    </View>
  );
}

// C02 Chapter Card —— 用户侧即 memory 卡：标题 + AI Story 摘要 + 元数据 Tag + 媒体数
export function MemoryCard({
  title,
  date,
  aiStory,
  tags,
  mediaCount,
  onPress,
}: {
  title: string;
  date: string;
  aiStory: string;
  tags: string[];
  mediaCount: number;
  onPress?: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={s.card}>
      <View style={s.hero}>
        <Text style={s.heroHint}>封面 · 精选代表帧</Text>
      </View>
      <Text style={s.cardTitle}>{title}</Text>
      <Text style={s.cardDate}>{date}</Text>
      <Text style={s.cardStory} numberOfLines={2}>
        {aiStory}
      </Text>
      <View style={s.tagRow}>
        {tags.map((t) => (
          <Tag key={t} label={t} />
        ))}
      </View>
      <Text style={s.mediaHint}>{mediaCount} memories media</Text>
    </Pressable>
  );
}

// C06 Today Status —— 今日状态胶囊（不阻断历史浏览）
export function TodayStatusPill({ label, tone = 'neutral' }: { label: string; tone?: 'neutral' | 'warn' | 'ok' }) {
  const bg = tone === 'warn' ? colors.accentSoft : tone === 'ok' ? colors.accentSoft : colors.surface;
  const fg = tone === 'neutral' ? colors.secondary : colors.accent;
  return (
    <View style={[s.pill, { backgroundColor: bg }]}>
      <View style={[s.pillDot, { backgroundColor: tone === 'neutral' ? colors.tertiary : colors.accent }]} />
      <Text style={[s.pillText, { color: fg }]}>{label}</Text>
    </View>
  );
}

// 列表行（Account / Device 用）
export function InfoRow({ label, value, onPress }: { label: string; value?: string; onPress?: () => void }) {
  return (
    <Pressable onPress={onPress} style={s.row}>
      <Text style={s.rowLabel}>{label}</Text>
      <View style={s.rowRight}>
        {value ? <Text style={s.rowValue}>{value}</Text> : null}
        <Text style={s.rowChevron}>›</Text>
      </View>
    </Pressable>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.paper },
  header: { paddingHorizontal: layout.gutterDiary, paddingTop: spacing.md, paddingBottom: spacing.sm },
  headerTitle: { fontSize: font.title, fontWeight: '700', color: colors.ink, letterSpacing: 0.2 },
  headerSub: { fontSize: font.small, color: colors.secondary, marginTop: 2 },
  body: { flex: 1, paddingHorizontal: layout.gutterDiary, gap: spacing.md },
  sectionTitle: { fontSize: font.h2, fontWeight: '700', color: colors.ink, marginTop: spacing.xs },
  tag: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.pill,
    marginRight: 6,
  },
  tagText: { fontSize: font.micro, color: colors.secondary },
  card: { backgroundColor: colors.card, borderRadius: radius.card, padding: spacing.md, borderWidth: 1, borderColor: colors.divider },
  hero: {
    height: 132,
    borderRadius: radius.control,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  heroHint: { color: colors.tertiary, fontSize: font.small },
  cardTitle: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  cardDate: { fontSize: font.micro, color: colors.tertiary, marginTop: 2 },
  cardStory: { fontSize: font.body, color: colors.secondary, marginTop: spacing.sm, lineHeight: 21 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', marginTop: spacing.sm },
  mediaHint: { fontSize: font.micro, color: colors.tertiary, marginTop: spacing.xs },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: radius.pill,
  },
  pillDot: { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  pillText: { fontSize: font.small, fontWeight: '600' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  rowLabel: { fontSize: font.body, color: colors.ink },
  rowRight: { flexDirection: 'row', alignItems: 'center' },
  rowValue: { fontSize: font.small, color: colors.tertiary, marginRight: 6 },
  rowChevron: { fontSize: font.h2, color: colors.tertiary },
});
