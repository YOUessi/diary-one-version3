import React, { useMemo } from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import { colors, font, layout, spacing } from '../theme';
import { formatShortDay } from '../domain/formatMedia';

const WEEKDAYS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

function parseDateKey(key: string) {
  const [y, m, d] = key.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function formatMonthLabel(date: Date) {
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

export function MemoryCalendar({
  expanded,
  selectedDateKey,
  todayKey,
  markedDays,
  onToggleExpanded,
  onSelectDate,
  onJumpToday,
  dayPreparing,
}: {
  expanded: boolean;
  selectedDateKey: string;
  todayKey: string;
  markedDays: Set<string>;
  onToggleExpanded: () => void;
  onSelectDate: (dateKey: string) => void;
  onJumpToday: () => void;
  dayPreparing?: boolean;
}) {
  const anchor = parseDateKey(selectedDateKey);
  const cells = useMemo(() => buildMonthCells(anchor), [anchor.getFullYear(), anchor.getMonth()]);
  const viewingToday = selectedDateKey === todayKey;

  return (
    <View style={styles.wrap}>
      <Pressable
        onPress={onToggleExpanded}
        style={styles.header}
        accessibilityRole="button"
        accessibilityState={{ expanded }}
      >
        <Text style={styles.month}>{formatMonthLabel(anchor)}</Text>
        <Text style={styles.chevron}>{expanded ? '▴' : '▾'}</Text>
      </Pressable>

      <View style={styles.todayRow}>
        <Pressable onPress={onJumpToday} style={styles.todayLeft}>
          <Text style={[styles.todayLabel, viewingToday && styles.todayLabelActive]}>Today</Text>
          <Text style={styles.todaySub}>{formatShortDay(todayKey)}</Text>
        </Pressable>
        <Pressable
          onPress={onJumpToday}
          hitSlop={12}
          accessibilityLabel="Jump to today"
          style={styles.jumpBtn}
        >
          <Text style={styles.jumpIcon}>↑</Text>
        </Pressable>
      </View>

      {expanded ? (
        <View style={styles.grid}>
          <View style={styles.weekRow}>
            {WEEKDAYS.map((w, i) => (
              <Text key={`${w}-${i}`} style={styles.weekday}>{w}</Text>
            ))}
          </View>
          {cells.map((cell, index) => {
            if (!cell) return <View key={`pad-${index}`} style={styles.cell} />;
            const key = cell.key;
            const selected = key === selectedDateKey;
            const marked = markedDays.has(key);
            const isFuture = cell.date > new Date();
            const preparing = Boolean(dayPreparing && selected);
            return (
              <Pressable
                key={key}
                disabled={isFuture || preparing}
                onPress={() => onSelectDate(key)}
                style={[styles.cell, selected && styles.cellSelected, isFuture && styles.cellDisabled]}
                accessibilityRole="button"
                accessibilityLabel={key}
                accessibilityState={{ selected, busy: preparing }}
              >
                <Text
                  style={[
                    styles.dayNum,
                    selected && styles.dayNumSelected,
                    isFuture && styles.dayNumDisabled,
                  ]}
                >
                  {cell.day}
                </Text>
                {preparing ? (
                  <ActivityIndicator size="small" color={colors.accent} style={styles.cellSpinner} />
                ) : marked ? (
                  <View style={styles.dot} />
                ) : null}
              </Pressable>
            );
          })}
        </View>
      ) : null}
    </View>
  );
}

function buildMonthCells(anchor: Date) {
  const year = anchor.getFullYear();
  const month = anchor.getMonth();
  const first = new Date(year, month, 1);
  const startPad = first.getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells: ({ key: string; day: number; date: Date } | null)[] = [];
  for (let i = 0; i < startPad; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(year, month, d);
    const key = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    cells.push({ key, day: d, date });
  }
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
}

const styles = StyleSheet.create({
  wrap: { marginBottom: spacing.md },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: layout.minTouch,
  },
  month: { fontSize: font.h2, fontWeight: '600', color: colors.ink },
  chevron: { fontSize: font.body, color: colors.tertiary },
  todayRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.xs,
    minHeight: 36,
  },
  todayLeft: { flexDirection: 'row', alignItems: 'baseline', gap: spacing.sm },
  todayLabel: { fontSize: font.body, fontWeight: '600', color: colors.secondary },
  todayLabelActive: { color: colors.ink },
  todaySub: { fontSize: font.small, color: colors.tertiary },
  jumpBtn: { minWidth: layout.minTouch, alignItems: 'flex-end', justifyContent: 'center' },
  jumpIcon: { fontSize: font.h2, color: colors.tertiary, fontWeight: '600' },
  grid: { marginTop: spacing.sm },
  weekRow: { flexDirection: 'row', marginBottom: 4 },
  weekday: {
    width: `${100 / 7}%`,
    textAlign: 'center',
    fontSize: font.micro,
    color: colors.tertiary,
  },
  cell: {
    width: `${100 / 7}%`,
    aspectRatio: 1,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 40,
  },
  cellSelected: { backgroundColor: colors.accentSoft, borderRadius: 20 },
  cellDisabled: { opacity: 0.35 },
  dayNum: { fontSize: font.small, color: colors.ink },
  dayNumSelected: { fontWeight: '700', color: colors.accent },
  dayNumDisabled: { color: colors.tertiary },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.accent,
    marginTop: 2,
  },
  cellSpinner: { marginTop: 2, transform: [{ scale: 0.75 }] },
});
