import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, Pressable, StyleSheet, FlatList } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { MemoryStackParamList } from '../../navigation/types';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { CapturedOriginal } from '../../model';
import { CapturedGridCell } from '../../components/CapturedGridCell';
import { formatCapturedDateHeader } from '../../domain/formatMedia';

type Nav = NativeStackNavigationProp<MemoryStackParamList, 'CapturedByYou'>;
type CapturedRoute = RouteProp<MemoryStackParamList, 'CapturedByYou'>;

type Filter = 'all' | 'photo' | 'video';

function groupByDate(items: CapturedOriginal[]) {
  const map = new Map<string, CapturedOriginal[]>();
  for (const item of items) {
    const list = map.get(item.dateKey) ?? [];
    list.push(item);
    map.set(item.dateKey, list);
  }
  return [...map.entries()].sort((a, b) => b[0].localeCompare(a[0]));
}

/** Figma 65:913 — text filters (not pills), scalloped grid cells. */
export default function CapturedByYouScreen() {
  const navigation = useNavigation<Nav>();
  const route = useRoute<CapturedRoute>();
  const initial = route.params?.filter ?? 'all';
  const captured = useAppStore((s) => s.capturedOriginals);
  const [filter, setFilter] = useState<Filter>(initial);

  useEffect(() => {
    if (route.params?.filter) setFilter(route.params.filter);
  }, [route.params?.filter]);

  const filtered = useMemo(() => {
    if (filter === 'all') return captured;
    return captured.filter((c) => c.kind === filter);
  }, [captured, filter]);

  const sections = useMemo(() => groupByDate(filtered), [filtered]);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <Text style={styles.title}>Captured by You</Text>
      {captured.length > 0 ? (
        <Text style={styles.sub}>Photos and videos you chose to capture.</Text>
      ) : null}

      <View style={styles.filters}>
        {(['all', 'photo', 'video'] as Filter[]).map((f) => {
          const on = filter === f;
          return (
            <Pressable key={f} onPress={() => setFilter(f)} style={styles.filterHit} hitSlop={8}>
              <Text style={[styles.filterText, on && styles.filterTextOn]}>
                {f === 'all' ? 'All' : f === 'photo' ? 'Photos' : 'Videos'}
              </Text>
            </Pressable>
          );
        })}
      </View>

      {captured.length === 0 ? (
        <View style={styles.emptyWrap}>
          <Text style={styles.emptyTitle}>No photos or videos yet.</Text>
          <Text style={styles.emptyBody}>
            Photos and videos you choose to capture will appear here.
          </Text>
        </View>
      ) : sections.length === 0 ? (
        <View style={styles.emptyWrap}>
          <Text style={styles.emptyTitle}>No photos or videos yet.</Text>
          <Text style={styles.emptyBody}>
            Photos and videos you choose to capture will appear here.
          </Text>
        </View>
      ) : (
        <FlatList
          data={sections}
          keyExtractor={([dateKey]) => dateKey}
          contentContainerStyle={styles.list}
          renderItem={({ item: [dateKey, cells] }) => (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>{formatCapturedDateHeader(dateKey)}</Text>
              <View style={styles.grid}>
                {cells.map((cell) => (
                  <CapturedGridCell
                    key={cell.id}
                    item={cell}
                    onPress={() => navigation.navigate('OriginalViewer', { captureId: cell.id })}
                  />
                ))}
              </View>
            </View>
          )}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  title: {
    ...type.titleLarge,
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
  },
  sub: {
    ...type.caption,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
  },
  /** Figma 65:913 — filter row h44 gap16; date 13 secondary; grid gap10 */
  filters: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    minHeight: 44,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  filterHit: { minHeight: 44, justifyContent: 'center' },
  filterText: { fontSize: 13, lineHeight: 18, color: colors.secondary, fontWeight: '400' },
  filterTextOn: { color: colors.ink, fontWeight: '500' },
  list: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  section: { marginBottom: 18 },
  sectionTitle: {
    fontSize: 13,
    lineHeight: 18,
    color: colors.secondary,
    marginBottom: spacing.sm,
  },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  emptyWrap: {
    flex: 1,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.xl,
    alignItems: 'center',
  },
  emptyTitle: { ...type.bodyStory, fontWeight: '600', color: colors.ink, marginBottom: spacing.sm },
  emptyBody: { ...type.caption, color: colors.secondary, textAlign: 'center', lineHeight: 20 },
});
