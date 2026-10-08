import React from 'react';
import { ScrollView, Text, Pressable, StyleSheet, View } from 'react-native';
import { CommonActions, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { MemoryTag } from '../../components/MemoryTag';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';
import type { Chapter } from '../../model';
import { formatChapterDateLong } from '../../domain/formatChapterDate';

type Route = RouteProp<MemoryStackParamList, 'TopicDetail'>;

function TopicMemoryCard({
  chapter,
  onPress,
}: {
  chapter: Chapter;
  onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={styles.card}>
      <Text style={styles.cardTitle}>{chapter.title}</Text>
      <Text style={styles.cardMeta}>{formatChapterDateLong(chapter.dateKey)}</Text>
      <View style={styles.tagRow}>
        {chapter.tags.slice(0, 2).map((t) => (
          <MemoryTag key={t} label={t} tone="primary" />
        ))}
      </View>
      <Text style={styles.quote}>&ldquo;{chapter.aiStory}&rdquo;</Text>
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
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  /** Figma 67:1027 — title 28; chapter rows ~112 */
  title: {
    ...type.titleSection,
    color: colors.ink,
    marginBottom: spacing.xl,
  },
  card: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    minHeight: 112,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  cardTitle: { ...type.titleChapter, color: colors.ink, marginBottom: 4 },
  cardMeta: { ...type.caption, color: colors.tertiary, marginBottom: spacing.sm },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs, marginBottom: spacing.sm },
  quote: { ...type.bodyStory, color: colors.secondary },
  empty: { ...type.bodyStory, color: colors.secondary },
});
