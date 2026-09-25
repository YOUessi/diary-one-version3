import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, Pressable, StyleSheet, FlatList } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { MemoryStackParamList } from '../../navigation/types';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing } from '../../theme';
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
      <Pressable onPress={() => navigation.goBack()} style={styles.back}>
        <Text style={styles.backText}>‹</Text>
      </Pressable>
      <Text style={styles.title}>Captured by You</Text>
      <Text style={styles.sub}>Photos and videos you chose to capture.</Text>

      <View style={styles.filters}>
        {(['all', 'photo', 'video'] as Filter[]).map((f) => (
          <Pressable
            key={f}
            onPress={() => setFilter(f)}
            style={[styles.chip, filter === f && styles.chipOn]}
          >
            <Text style={[styles.chipText, filter === f && styles.chipTextOn]}>
              {f === 'all' ? 'All' : f === 'photo' ? 'Photos' : 'Videos'}
            </Text>
          </Pressable>
        ))}
      </View>

      {captured.length === 0 ? (
        <View style={styles.emptyWrap}>
          <Text style={styles.emptyTitle}>No photos or videos yet.</Text>
          <Text style={styles.emptyBody}>Photos and videos you choose to capture will appear here.</Text>
        </View>
      ) : sections.length === 0 ? (
        <Text style={styles.emptyFilter}>No originals in this filter.</Text>
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
  back: {
    paddingHorizontal: layout.gutterDiary,
    minHeight: layout.minTouch,
    justifyContent: 'center',
    width: 48,
  },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300' },
  title: {
    fontSize: font.title,
    fontWeight: '700',
    color: colors.ink,
    paddingHorizontal: layout.gutterDiary,
  },
  sub: {
    fontSize: font.small,
    color: colors.secondary,
    paddingHorizontal: layout.gutterDiary,
    marginTop: spacing.xs,
    marginBottom: spacing.md,
  },
  filters: {
    flexDirection: 'row',
    gap: spacing.sm,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.divider,
    minHeight: 36,
    justifyContent: 'center',
  },
  chipOn: { backgroundColor: colors.ink, borderColor: colors.ink },
  chipText: { fontSize: font.small, color: colors.secondary, fontWeight: '600' },
  chipTextOn: { color: colors.paper },
  list: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  section: { marginBottom: spacing.lg },
  sectionTitle: { fontSize: font.small, fontWeight: '600', color: colors.secondary, marginBottom: spacing.sm },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  emptyWrap: {
    flex: 1,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.xl,
    alignItems: 'center',
  },
  emptyTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink, marginBottom: spacing.sm },
  emptyBody: { fontSize: font.small, color: colors.secondary, textAlign: 'center', lineHeight: 20 },
  emptyFilter: { padding: layout.gutterDiary, color: colors.tertiary, fontSize: font.body },
});
