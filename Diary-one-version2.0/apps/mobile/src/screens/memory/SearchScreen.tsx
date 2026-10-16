import React, { useEffect, useMemo, useRef, useState } from 'react';
import { View, Text, TextInput, Pressable, FlatList, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import { CommonActions, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing, type } from '../../theme';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { SearchGlyph } from '../../components/SearchGlyph';
import { MemoryTag } from '../../components/MemoryTag';
import { useAppStore } from '../../store/useAppStore';
import { searchChapters } from '../../search/localSearch';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import type { DiaryStackParamList } from '../../navigation/types';
import type { MemoryStackParamList } from '../../navigation/types';
import { isDevFailSimulationEnabled } from '../../config/devFailSimulation';

type DiaryRoute = RouteProp<DiaryStackParamList, 'Search'>;
type MemoryRoute = RouteProp<MemoryStackParamList, 'Search'>;

function useDebounced(value: string, ms: number) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return debounced;
}

export default function SearchScreen() {
  const navigation = useNavigation();
  const route = useRoute<DiaryRoute | MemoryRoute>();
  const initial = route.params?.initialQuery ?? '';
  const chapters = useAppStore((s) => s.chapters);
  const [query, setQuery] = useState(initial);
  const debounced = useDebounced(query, 280);
  const [searchPhase, setSearchPhase] = useState<'idle' | 'loading' | 'done' | 'error'>('idle');
  const [retryNonce, setRetryNonce] = useState(0);
  const searchFailAlternate = useRef(false);

  useEffect(() => {
    if (debounced.trim() === '') {
      setSearchPhase('idle');
      return;
    }
    setSearchPhase('loading');
    const t = setTimeout(() => {
      if (isDevFailSimulationEnabled() && searchFailAlternate.current) {
        searchFailAlternate.current = false;
        setSearchPhase('error');
        return;
      }
      if (isDevFailSimulationEnabled()) searchFailAlternate.current = true;
      setSearchPhase('done');
    }, 280);
    return () => clearTimeout(t);
  }, [debounced, retryNonce]);

  const results = useMemo(() => {
    try {
      return searchChapters(chapters, debounced);
    } catch {
      setSearchPhase('error');
      return [];
    }
  }, [chapters, debounced]);

  const openChapter = (chapterId: string) => {
    // PRD SEA03 — re-validate before opening; stale hits must not open another scope.
    const still = useAppStore.getState().chapters.some((c) => c.id === chapterId);
    if (!still) {
      Alert.alert('Memory unavailable', 'This result is no longer available. Search again.');
      setRetryNonce((n) => n + 1);
      return;
    }
    navigation.dispatch(
      CommonActions.navigate({
        name: 'DiaryTab',
        params: {
          screen: 'ChapterDetail',
          params: { chapterId },
        },
      }),
    );
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.topRow}>
        <Pressable onPress={() => navigation.goBack()} style={styles.back}>
          <Text style={styles.backText}>‹</Text>
        </Pressable>
        <View style={styles.headerWrap}>
          <FigmaScreenHeader title="Memory" />
        </View>
      </View>
      <View style={styles.searchRow}>
        <SearchGlyph size={22} />
        <TextInput
          autoFocus
          value={query}
          onChangeText={setQuery}
          placeholder="Search your memories..."
          placeholderTextColor={colors.tertiary}
          style={styles.input}
          returnKeyType="search"
        />
      </View>
      {query.trim() === '' ? (
        <View style={styles.hintBlock}>
          <Text style={styles.hint}>
            Search by person, activity, season, or anything you remember.
          </Text>
          <Pressable onPress={() => setQuery('coffee')} hitSlop={8}>
            <Text style={styles.tryExample}>Try: coffee (word match in titles, stories, notes, tags)</Text>
          </Pressable>
        </View>
      ) : searchPhase === 'loading' ? (
        <View style={styles.emptyBlock}>
          <Text style={styles.queryEcho}>{debounced.trim()}</Text>
          <View style={styles.loadingRow}>
            <ActivityIndicator color={colors.accent} />
            <Text style={styles.loadingText}>Searching memories…</Text>
          </View>
        </View>
      ) : searchPhase === 'error' ? (
        <View style={styles.emptyBlock}>
          <Text style={styles.queryEcho}>{debounced.trim()}</Text>
          <Text style={styles.emptyTitle}>Couldn&apos;t search memories.</Text>
          <Text style={styles.emptyBody}>
            Your existing memories are still available. Try the search again.
          </Text>
          <Pressable onPress={() => setRetryNonce((n) => n + 1)}>
            <Text style={styles.tryAgain}>Try Again</Text>
          </Pressable>
        </View>
      ) : results.length === 0 ? (
        <View style={styles.emptyBlock}>
          <Text style={styles.queryEcho}>{debounced.trim()}</Text>
          <Text style={styles.emptyTitle}>No memories found for this search.</Text>
          <Text style={styles.emptyBody}>
            Try a different person, topic, season, or activity.
          </Text>
        </View>
      ) : (
        <>
          <Text style={styles.queryEcho}>{debounced.trim()}</Text>
          <Text style={styles.resultCount}>
            {results.length} {results.length === 1 ? 'memory' : 'memories'}
          </Text>
          {/* Figma Search Results: chapter list only — no conversational agent card */}
          <FlatList
            data={results}
            keyExtractor={(item) => item.chapter.id}
            contentContainerStyle={styles.list}
            keyboardShouldPersistTaps="handled"
            renderItem={({ item }) => (
              <Pressable onPress={() => openChapter(item.chapter.id)} style={styles.row}>
                <Text style={styles.rowTitle}>{item.chapter.title}</Text>
                <Text style={styles.rowMeta}>{formatChapterDateLong(item.chapter.dateKey)}</Text>
                <View style={styles.tagRow}>
                  {item.chapter.tags.slice(0, 2).map((t) => (
                    <MemoryTag key={t} label={t} tone="primary" />
                  ))}
                </View>
                <Text style={styles.rowSub} numberOfLines={2}>
                  {item.snippet ?? item.chapter.aiStory}
                </Text>
              </Pressable>
            )}
          />
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  topRow: { flexDirection: 'row', alignItems: 'flex-start' },
  back: {
    paddingLeft: layout.gutterDiary,
    paddingTop: spacing.md,
    minWidth: 36,
    minHeight: layout.minTouch,
  },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300' },
  headerWrap: { flex: 1, marginLeft: -spacing.sm },
  /** Figma 174:1921 — white elevated field h48 r12 */
  searchRow: {
    marginHorizontal: layout.gutterDiary,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: radius.card,
    height: 48,
    paddingHorizontal: 14,
    marginBottom: spacing.lg,
    gap: 10,
  },
  input: { flex: 1, ...type.bodyStory, color: colors.ink, paddingVertical: 0 },
  hintBlock: { paddingHorizontal: layout.gutterDiary, gap: spacing.sm },
  hint: { ...type.bodyStory, color: colors.secondary, lineHeight: 24 },
  tryExample: { ...type.captionEmphasis, color: colors.secondary },
  emptyBlock: { padding: layout.gutterDiary, gap: spacing.sm },
  emptyTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  emptyBody: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  /** Figma Search Failed — text link 13/510, not filled CTA */
  tryAgain: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.secondary,
    marginTop: spacing.sm,
    minHeight: 44,
    textAlignVertical: 'center',
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    padding: layout.gutterDiary,
  },
  loadingText: { fontSize: font.small, color: colors.secondary },
  queryEcho: {
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.sm,
    fontSize: font.body,
    fontWeight: '600',
    color: colors.ink,
  },
  resultCount: {
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.xs,
    fontSize: font.small,
    fontWeight: '600',
    color: colors.secondary,
  },
  agentCard: {
    marginHorizontal: layout.gutterDiary,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.card,
    gap: 4,
  },
  agentEyebrow: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.tertiary,
    letterSpacing: 0.4,
    textTransform: 'uppercase',
  },
  agentHeadline: { fontSize: font.body, fontWeight: '700', color: colors.ink, marginTop: 2 },
  agentBullet: { fontSize: font.small, color: colors.secondary, lineHeight: 18 },
  list: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  row: {
    paddingVertical: spacing.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
    minHeight: layout.minTouch,
  },
  rowTitle: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  rowMeta: { fontSize: font.small, color: colors.tertiary, marginTop: 2 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', marginTop: spacing.xs },
  rowSub: { fontSize: font.body, color: colors.secondary, marginTop: spacing.sm, lineHeight: 22 },
});
