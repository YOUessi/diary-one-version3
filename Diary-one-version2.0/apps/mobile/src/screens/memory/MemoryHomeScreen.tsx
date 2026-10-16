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

/** Figma Memory Home strip shows ~4 tiles at 82×72. */
const PREVIEW_COUNT = 4;

export default function MemoryHomeScreen() {
  const navigation = useNavigation<Nav>();
  const topics = useAppStore((s) => s.topics);
  const captured = useAppStore((s) => s.capturedOriginals);
  const todayStatus = useAppStore((s) => s.todayStatus);
  const showTopics = topics.length > 0;
  const deviceLinkState = useAppStore((s) => s.deviceLinkState);
  const devicePendingRecordings = useAppStore((s) => s.devicePendingRecordings);
  // PRD DEV01 / DIA04 — Sync banner only when a real device link has pending recordings.
  const showUnsynced =
    deviceLinkState !== 'disconnected' &&
    devicePendingRecordings &&
    (todayStatus === 'UNSYNCED' || todayStatus === 'READY_NEW_RECORDINGS');
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
          <SearchGlyph size={22} />
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

        <View style={styles.section}>
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
          {preview.length > 0 ? (
            <View style={styles.previewStrip}>
              {preview.map((cell) => (
                <CapturedGridCell
                  key={cell.id}
                  item={cell}
                  variant="preview"
                  onPress={() => navigation.navigate('OriginalViewer', { captureId: cell.id })}
                />
              ))}
            </View>
          ) : null}
          <Text style={styles.counts}>
            {photoCount} photos · {videoCount} videos
          </Text>
        </View>

        {showTopics ? (
          <View style={styles.section}>
            <View style={styles.sectionRow}>
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
          </View>
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
    gap: spacing.xxl,
  },
  /** Figma 44:809 — white elevated field, r12, h48, no border */
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: colors.card,
    borderRadius: radius.card,
    paddingHorizontal: 14,
    height: layout.buttonHeight,
    overflow: 'hidden',
  },
  searchPlaceholder: { ...type.bodyStory, color: colors.tertiary, flex: 1 },
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radius.card,
    padding: spacing.md,
    minHeight: layout.minTouch,
  },
  bannerCopy: { flex: 1 },
  bannerTitle: { ...type.captionEmphasis, color: colors.ink },
  bannerSub: { ...type.metadata, color: colors.secondary, marginTop: 2 },
  bannerChevron: { ...type.titleChapter, color: colors.tertiary, fontWeight: '300' },
  section: { gap: 10, width: '100%' },
  sectionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 44,
  },
  sectionTitle: { ...type.titleChapter, color: colors.ink, flex: 1 },
  seeAllHit: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    minHeight: layout.minTouch,
    width: 74,
    justifyContent: 'flex-end',
  },
  /** Figma See all — secondary ink, not accent */
  seeAll: { ...type.captionEmphasis, color: colors.secondary, textAlign: 'right' },
  seeAllChevron: { ...type.captionEmphasis, color: colors.secondary },
  sectionSub: { ...type.caption, color: colors.secondary },
  counts: { ...type.caption, color: colors.tertiary },
  previewStrip: { flexDirection: 'row', gap: spacing.sm, height: layout.capturedPreviewH },
  topicGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  /** Neutral D1/Tag on Memory Home topics */
  topicChip: {
    height: 26,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  topicText: { ...type.captionEmphasis, color: colors.secondary },
});
