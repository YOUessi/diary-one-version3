import React, { useEffect, useMemo, useRef, useState } from 'react';
import { View, Text, TextInput, Pressable, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import { CommonActions, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, spacing } from '../../theme';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { MemoryTag } from '../../components/MemoryTag';
import { useAppStore } from '../../store/useAppStore';
import { searchChapters } from '../../search/localSearch';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import type { DiaryStackParamList } from '../../navigation/types';
import type { MemoryStackParamList } from '../../navigation/types';

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
  const searchFailAlternate = useRef(false);

  useEffect(() => {
    if (debounced.trim() === '') {
      setSearchPhase('idle');
      return;
    }
    setSearchPhase('loading');
    const t = setTimeout(() => {
      if (searchFailAlternate.current) {
        searchFailAlternate.current = false;
        setSearchPhase('error');
        return;
      }
      searchFailAlternate.current = true;
      setSearchPhase('done');
    }, 280);
    return () => clearTimeout(t);
  }, [debounced]);

  const results = useMemo(() => {
    try {
      return searchChapters(chapters, debounced);
    } catch {
      setSearchPhase('error');
      return [];
    }
  }, [chapters, debounced]);

  const openChapter = (chapterId: string) => {
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
          <Pressable onPress={() => setQuery('coffee last summer')} hitSlop={8}>
            <Text style={styles.tryExample}>Try: coffee last summer</Text>
          </Pressable>
        </View>
      ) : searchPhase === 'loading' ? (
        <View style={styles.loadingRow}>
          <ActivityIndicator color={colors.accent} />
          <Text style={styles.loadingText}>Searching memories…</Text>
        </View>
      ) : searchPhase === 'error' ? (
        <View style={styles.emptyBlock}>
          <Text style={styles.queryEcho}>{debounced.trim()}</Text>
          <Text style={styles.emptyTitle}>Couldn&apos;t search memories.</Text>
          <Text style={styles.emptyBody}>
            Your existing memories are still available. Try the search again.
          </Text>
          <Pressable
            onPress={() => {
              searchFailAlternate.current = true;
              setSearchPhase('loading');
              setTimeout(() => {
                searchFailAlternate.current = false;
                setSearchPhase('done');
              }, 280);
            }}
          >
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
  searchRow: {
    paddingHorizontal: layout.gutterDiary,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
  },
  input: { fontSize: font.body, color: colors.ink, paddingVertical: spacing.md },
  hintBlock: { padding: layout.gutterDiary, gap: spacing.sm },
  hint: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  tryExample: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  emptyBlock: { padding: layout.gutterDiary, gap: spacing.sm },
  emptyTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  emptyBody: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  tryAgain: { fontSize: font.small, fontWeight: '600', color: colors.accent, marginTop: spacing.sm },
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
