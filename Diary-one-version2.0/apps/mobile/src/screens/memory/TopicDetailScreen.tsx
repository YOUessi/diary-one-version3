import React from 'react';
import { Image, ScrollView, Text, Pressable, StyleSheet, View } from 'react-native';
import { CommonActions, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { MemoryTag } from '../../components/MemoryTag';
import { colors, layout, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';
import type { Chapter } from '../../model';
import { formatChapterDateLong } from '../../domain/formatChapterDate';

type Route = RouteProp<MemoryStackParamList, 'TopicDetail'>;

/** Figma 67:1027 — 112 thumb + copy; Neutral tags; quote 13. */
function TopicMemoryCard({
  chapter,
  onPress,
}: {
  chapter: Chapter;
  onPress: () => void;
}) {
  const thumb = chapter.heroUri ?? chapter.moments[0]?.posterUri;
  const quote = chapter.aiStory.trim();

  return (
    <Pressable onPress={onPress} style={styles.card} accessibilityRole="button">
      <View style={styles.thumb}>
        {thumb ? (
          <Image source={{ uri: thumb }} style={styles.thumbImage} resizeMode="cover" />
        ) : (
          <>
            <View style={styles.thumbOrb} />
            <View style={styles.thumbWave} />
          </>
        )}
      </View>
      <View style={styles.copy}>
        <Text style={styles.cardTitle} numberOfLines={2}>
          {chapter.title}
        </Text>
        <Text style={styles.cardMeta}>{formatChapterDateLong(chapter.dateKey)}</Text>
        <View style={styles.tagRow}>
          {chapter.tags.slice(0, 2).map((t) => (
            <MemoryTag key={t} label={t} tone="neutral" />
          ))}
        </View>
        {quote ? (
          <Text style={styles.quote} numberOfLines={3}>
            &ldquo;{quote}&rdquo;
          </Text>
        ) : null}
      </View>
    </Pressable>
  );
}

export default function TopicDetailScreen() {
  const { topicId } = useRoute<Route>().params;
  const navigation = useNavigation();
  const topic = useAppStore((s) => s.topics.find((t) => t.id === topicId));
  const chapters = useAppStore((s) => s.chapters);
  const related = chapters
    .filter((c) => topic?.chapterIds.includes(c.id))
    .sort((a, b) => b.dateKey.localeCompare(a.dateKey));

  const openChapter = (chapterId: string) => {
    navigation.dispatch(
      CommonActions.navigate({
        name: 'DiaryTab',
        params: { screen: 'ChapterDetail', params: { chapterId } },
      }),
    );
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>{topic?.name ?? 'Topic'}</Text>
        {related.length === 0 ? (
          <Text style={styles.empty}>No memories in this topic yet.</Text>
        ) : (
          related.map((c) => (
            <TopicMemoryCard key={c.id} chapter={c} onPress={() => openChapter(c.id)} />
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: 120 },
  title: {
    ...type.titleSection,
    color: colors.ink,
    marginBottom: 24,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 14,
    marginBottom: 24,
  },
  thumb: {
    width: 112,
    height: 112,
    borderRadius: 12,
    backgroundColor: colors.surface,
    overflow: 'hidden',
  },
  thumbImage: { width: '100%', height: '100%' },
  thumbOrb: {
    position: 'absolute',
    top: '18%',
    right: '16%',
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.accentSoft,
  },
  thumbWave: {
    position: 'absolute',
    left: '-20%',
    right: '-20%',
    bottom: -24,
    height: 56,
    borderRadius: 999,
    backgroundColor: colors.card,
  },
  copy: { flex: 1, gap: 7, minWidth: 0 },
  cardTitle: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink },
  cardMeta: { fontSize: 13, lineHeight: 18, color: colors.tertiary },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  quote: { fontSize: 13, lineHeight: 18, color: colors.secondary },
  empty: { ...type.bodyStory, color: colors.secondary },
});
