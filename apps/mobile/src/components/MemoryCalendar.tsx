import { appStrings, appLocale } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import React, { useMemo } from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import { colors, layout, spacing, type } from '../theme';

/** Figma calendar week starts Monday (M T W T F S S). */
const WEEKDAYS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

function parseDateKey(key: string) {
  const [y, m, d] = key.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function formatMonthLabel(date: Date, locale: string) {
  return date.toLocaleDateString(locale, { month: 'long', year: 'numeric' });
}

function buildMonthCells(anchor: Date) {
  const year = anchor.getFullYear();
  const month = anchor.getMonth();
  const first = new Date(year, month, 1);
  // JS Sun=0 → Mon-first pad
  const startPad = (first.getDay() + 6) % 7;
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

/** Figma D1/Mini Memory Calendar — collapsed: month + 8px heatmap. */
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
  const language = useAppStore((s) => s.language);
  const strings = appStrings(language);
  const locale = appLocale(language);
  const weekdays = locale === 'zh-CN' ? ['一', '二', '三', '四', '五', '六', '日'] : WEEKDAYS;
  const anchor = parseDateKey(selectedDateKey);
  const cells = useMemo(() => buildMonthCells(parseDateKey(selectedDateKey)), [selectedDateKey]);
  const weeks: (typeof cells)[] = [];
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));

  if (!expanded) {
    return (
      <Pressable
        onPress={onToggleExpanded}
        style={styles.mini}
        accessibilityRole="button"
        accessibilityState={{ expanded: false }}
        accessibilityLabel={`${formatMonthLabel(anchor, locale)} ${strings.calendar}`}
      >
        <Text style={styles.miniMonth}>{formatMonthLabel(anchor, locale)}</Text>
        <View style={styles.heat}>
          {weeks.map((week, wi) => (
            <View key={`w-${wi}`} style={styles.heatRow}>
              {week.map((cell, ci) => {
                if (!cell) {
                  return <View key={`e-${wi}-${ci}`} style={[styles.heatCell, styles.heatOutside]} />;
                }
                const marked = markedDays.has(cell.key);
                const selected = cell.key === selectedDateKey;
                const isToday = cell.key === todayKey;
                return (
                  <View
                    key={cell.key}
                    style={[
                      styles.heatCell,
                      selected || isToday
                        ? styles.heatAccent
                        : marked
                          ? styles.heatInk
                          : styles.heatEmpty,
                    ]}
                  />
                );
              })}
            </View>
          ))}
        </View>
      </Pressable>
    );
  }

  return (
    <View style={styles.wrap}>
      <Pressable
        onPress={onToggleExpanded}
        style={styles.header}
        accessibilityRole="button"
        accessibilityState={{ expanded: true }}
      >
        <Text style={styles.monthExpanded}>{formatMonthLabel(anchor, locale)}</Text>
        <Text style={styles.chevron}>▴</Text>
      </Pressable>
      <Pressable onPress={onJumpToday} style={styles.jumpToday} hitSlop={8}>
        <Text style={styles.jumpTodayText}>{strings.jumpToday}</Text>
      </Pressable>
      <View style={styles.grid}>
        <View style={styles.weekRow}>
          {weekdays.map((w, i) => (
            <Text key={`${w}-${i}`} style={styles.weekday}>
              {w}
            </Text>
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
    </View>
  );
}

const styles = StyleSheet.create({
  mini: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 64,
    width: '100%',
    marginBottom: 0,
  },
  miniMonth: {
    ...type.captionEmphasis,
    color: colors.ink,
    width: 150,
  },
  heat: {
    width: 80,
    gap: 3,
  },
  heatRow: {
    flexDirection: 'row',
    gap: 4,
    height: 8,
  },
  heatCell: {
    width: 8,
    height: 8,
  },
  heatOutside: { backgroundColor: colors.surface, opacity: 0 },
  heatEmpty: { backgroundColor: colors.surface },
  heatInk: { backgroundColor: colors.ink },
  heatAccent: { backgroundColor: colors.accent },
  wrap: { marginBottom: spacing.md },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: layout.minTouch,
  },
  /** Figma 131:1432 — month 22; cells ~47×44; selected r12; grid gap 4 */
  monthExpanded: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    color: colors.ink,
  },
  chevron: { fontSize: 17, color: colors.tertiary },
  jumpToday: { marginTop: spacing.xs, minHeight: 36, justifyContent: 'center' },
  jumpTodayText: { ...type.captionEmphasis, color: colors.secondary },
  grid: { marginTop: spacing.sm, rowGap: 4 },
  weekRow: { flexDirection: 'row', marginBottom: 4 },
  weekday: {
    width: `${100 / 7}%` as unknown as number,
    textAlign: 'center',
    ...type.metadata,
    color: colors.tertiary,
  },
  cell: {
    width: `${100 / 7}%` as unknown as number,
    aspectRatio: 47 / 44,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  cellSelected: { backgroundColor: colors.accentSoft, borderRadius: 12 },
  cellDisabled: { opacity: 0.35 },
  dayNum: { ...type.caption, color: colors.ink },
  dayNumSelected: { fontWeight: '700', color: colors.accent },
  dayNumDisabled: { color: colors.tertiary },
  dot: {
    width: 4,
    height: 4,
    borderRadius: 1,
    backgroundColor: colors.ink,
    marginTop: 3,
  },
  cellSpinner: { marginTop: 2, transform: [{ scale: 0.75 }] },
});
