import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing } from '../../theme';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { CapturedGridCell } from '../../components/CapturedGridCell';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';

type Nav = NativeStackNavigationProp<MemoryStackParamList, 'MemoryHome'>;

const PREVIEW_COUNT = 6;

export default function MemoryHomeScreen() {
  const navigation = useNavigation<Nav>();
  const topics = useAppStore((s) => s.topics);
  const captured = useAppStore((s) => s.capturedOriginals);
  const todayStatus = useAppStore((s) => s.todayStatus);
  const showTopics = topics.length > 0;
  const showUnsynced = todayStatus === 'UNSYNCED' || todayStatus === 'READY_NEW_RECORDINGS';
  const photoCount = captured.filter((c) => c.kind === 'photo').length;
  const videoCount = captured.filter((c) => c.kind === 'video').length;
  const preview = captured.slice(0, PREVIEW_COUNT);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaScreenHeader title="Memory" />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {showUnsynced ? (
          <View style={styles.banner}>
            <Text style={styles.bannerTitle}>New recordings on Diary One</Text>
            <Text style={styles.bannerSub}>Sync when you&apos;re ready</Text>
          </View>
        ) : null}

        <Pressable
          onPress={() => navigation.navigate('Search', {})}
          style={styles.searchBox}
          accessibilityRole="button"
        >
          <Text style={styles.searchPlaceholder}>Search your memories...</Text>
        </Pressable>

        <View style={styles.sectionRow}>
          <Text style={styles.sectionTitle}>Captured by You</Text>
          <Pressable onPress={() => navigation.navigate('CapturedByYou', { filter: 'all' })}>
            <Text style={styles.seeAll}>See all ›</Text>
          </Pressable>
        </View>
        <Text style={styles.sectionSub}>Photos and videos you chose to capture.</Text>
        <View style={styles.countRow}>
          <Text style={styles.counts}>
            {photoCount} photos · {videoCount} videos
          </Text>
          <View style={styles.quickFilters}>
            <Pressable onPress={() => navigation.navigate('CapturedByYou', { filter: 'photo' })}>
              <Text style={styles.quickFilter}>Photos</Text>
            </Pressable>
            <Text style={styles.countSep}>·</Text>
            <Pressable onPress={() => navigation.navigate('CapturedByYou', { filter: 'video' })}>
              <Text style={styles.quickFilter}>Videos</Text>
            </Pressable>
          </View>
        </View>
        {preview.length > 0 ? (
          <View style={styles.previewGrid}>
            {preview.map((cell) => (
              <CapturedGridCell
                key={cell.id}
                item={cell}
                onPress={() => navigation.navigate('OriginalViewer', { captureId: cell.id })}
              />
            ))}
          </View>
        ) : null}

        {showTopics ? (
          <>
            <View style={styles.sectionRow}>
              <Text style={styles.sectionTitle}>Your Topics</Text>
              <Pressable onPress={() => navigation.navigate('TopicsList')}>
                <Text style={styles.seeAll}>See all ›</Text>
              </Pressable>
            </View>
            <Text style={styles.sectionSub}>Themes Diary One noticed in your memories.</Text>
            <View style={styles.topicGrid}>
              {topics.map((t) => (
                <Pressable
                  key={t.id}
                  style={styles.topicChip}
                  onPress={() => navigation.navigate('TopicDetail', { topicId: t.id })}
                >
                  <Text style={styles.topicText}>{t.name}</Text>
                </Pressable>
              ))}
            </View>
          </>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  banner: {
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  bannerTitle: { fontSize: font.small, fontWeight: '600', color: colors.ink },
  bannerSub: { fontSize: font.micro, color: colors.secondary, marginTop: 2 },
  searchBox: {
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    marginBottom: spacing.lg,
    minHeight: layout.minTouch,
    justifyContent: 'center',
  },
  searchPlaceholder: { fontSize: font.body, color: colors.tertiary },
  sectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.md,
  },
  sectionTitle: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  seeAll: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  sectionSub: { fontSize: font.small, color: colors.secondary, marginTop: 4 },
  countRow: { marginTop: spacing.xs, marginBottom: spacing.sm },
  counts: { fontSize: font.micro, color: colors.tertiary },
  quickFilters: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, marginTop: 4 },
  quickFilter: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  countSep: { color: colors.tertiary },
  previewGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.md },
  topicGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.sm },
  topicChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.divider,
  },
  topicText: { fontSize: font.small, color: colors.ink, fontWeight: '500' },
});
