import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, radius, spacing, type } from '../../theme';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { SearchGlyph } from '../../components/SearchGlyph';
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
      <View style={styles.gutter}>
        <FigmaScreenHeader title="Memory" />
      </View>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Pressable
          onPress={() => navigation.navigate('Search', {})}
          style={styles.searchBox}
          accessibilityRole="button"
          accessibilityLabel="Search your memories"
        >
          <SearchGlyph />
          <Text style={styles.searchPlaceholder}>Search your memories...</Text>
        </Pressable>

        {showUnsynced ? (
          <Pressable
            style={styles.banner}
            onPress={() => {
              const parent = navigation.getParent();
              parent?.navigate('DeviceTab');
            }}
            accessibilityRole="button"
            accessibilityLabel="New recordings on Diary One. Sync when you're ready"
          >
            <View style={styles.bannerCopy}>
              <Text style={styles.bannerTitle}>New recordings on Diary One</Text>
              <Text style={styles.bannerSub}>Sync when you&apos;re ready</Text>
            </View>
            <Text style={styles.bannerChevron}>›</Text>
          </Pressable>
        ) : null}

        <View style={styles.sectionRow}>
          <Text style={styles.sectionTitle}>Captured by You</Text>
          <Pressable
            onPress={() => navigation.navigate('CapturedByYou', { filter: 'all' })}
            hitSlop={8}
            style={styles.seeAllHit}
          >
            <Text style={styles.seeAll}>See all</Text>
            <Text style={styles.seeAllChevron}>›</Text>
          </Pressable>
        </View>
        <Text style={styles.sectionSub}>Photos and videos you chose to capture.</Text>
        <Text style={styles.counts}>
          {photoCount} photos · {videoCount} videos
        </Text>
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
            <View style={[styles.sectionRow, styles.topicsHead]}>
              <Text style={styles.sectionTitle}>Your Topics</Text>
              <Pressable
                onPress={() => navigation.navigate('TopicsList')}
                hitSlop={8}
                style={styles.seeAllHit}
              >
                <Text style={styles.seeAll}>See all</Text>
                <Text style={styles.seeAllChevron}>›</Text>
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
  gutter: { paddingHorizontal: layout.gutterDiary },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: layout.tabBarHeight + spacing.xxxl,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingRight: spacing.md,
    paddingLeft: 2,
    marginBottom: spacing.lg,
    minHeight: layout.minTouch,
  },
  searchPlaceholder: { ...type.bodyStory, color: colors.tertiary, flex: 1 },
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.lg,
    minHeight: layout.minTouch,
  },
  bannerCopy: { flex: 1 },
  bannerTitle: { ...type.captionEmphasis, color: colors.ink },
  bannerSub: { ...type.metadata, color: colors.secondary, marginTop: 2 },
  bannerChevron: { ...type.titleChapter, color: colors.tertiary, fontWeight: '300' },
  sectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  topicsHead: { marginTop: spacing.xl },
  sectionTitle: { ...type.titleChapter, color: colors.ink },
  seeAllHit: { flexDirection: 'row', alignItems: 'center', minHeight: layout.minTouch },
  seeAll: { ...type.captionEmphasis, color: colors.accent },
  seeAllChevron: { ...type.captionEmphasis, color: colors.accent, marginLeft: 2 },
  sectionSub: { ...type.caption, color: colors.secondary, marginTop: 4 },
  counts: { ...type.metadata, color: colors.tertiary, marginTop: spacing.xs, marginBottom: spacing.sm },
  previewGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.md },
  topicGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.sm },
  topicChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
  },
  topicText: { ...type.captionEmphasis, color: colors.ink },
});
