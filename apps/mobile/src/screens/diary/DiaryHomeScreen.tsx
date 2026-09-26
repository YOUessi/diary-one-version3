import React, { useMemo } from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, spacing } from '../../theme';
import { ChapterBlock } from '../../components/ChapterBlock';
import { SmallMemory } from '../../components/SmallMemory';
import { TodayStatusBanner } from '../../components/TodayStatus';
import { MemoryCalendar } from '../../components/MemoryCalendar';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { performDeviceSync } from '../../device/deviceSync';
import {
  useAppStore,
  chaptersForDate,
  smallMemoriesForDate,
} from '../../store/useAppStore';
import { daysWithContent } from '../../model';
import type { DiaryStackParamList } from '../../navigation/types';
import { TodayStatusDevPicker } from '../../dev/TodayStatusDevPicker';
import { diaryTodayKey } from '../../domain/dayKey';
import { buildDayFeed, buildEarlierFeed } from '../../diary/buildDiaryFeed';
import { DayPrepareBanner } from '../../components/DayPrepareBanner';
import { ShareDayReadinessSheet } from '../../components/ShareDayReadinessSheet';
import { CloudProcessingBanner } from '../../components/CloudProcessingBanner';
import { activePipelineTask } from '../../pipeline/pipelineActive';

type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DiaryHome'>;

export default function DiaryHomeScreen() {
  const navigation = useNavigation<Nav>();
  const todayStatus = useAppStore((s) => s.todayStatus);
  const selectedDateKey = useAppStore((s) => s.selectedDateKey);
  const chapters = useAppStore((s) => s.chapters);
  const smallMemoriesByDate = useAppStore((s) => s.smallMemoriesByDate);
  const historyLoadState = useAppStore((s) => s.historyLoadState);
  const selectDateKeyWithPrepare = useAppStore((s) => s.selectDateKeyWithPrepare);
  const calendarDayPreparing = useAppStore((s) => s.calendarDayPreparing);
  const setTodayStatus = useAppStore((s) => s.setTodayStatus);
  const historyVisibleCount = useAppStore((s) => s.historyVisibleCount);
  const loadMoreHistory = useAppStore((s) => s.loadMoreHistory);
  const dailyRecapShareBlockedBanner = useAppStore((s) => s.dailyRecapShareBlockedBanner);
  const setDailyRecapShareBlockedBanner = useAppStore((s) => s.setDailyRecapShareBlockedBanner);
  const pipelineTasks = useAppStore((s) => s.pipelineTasks);
  const pipelineTask = activePipelineTask(pipelineTasks);

  const todayKey = diaryTodayKey();
  const marked = useMemo(
    () => daysWithContent(chapters, smallMemoriesByDate),
    [chapters, smallMemoriesByDate],
  );

  const isViewingToday = selectedDateKey === todayKey;
  const showTodayBanner = isViewingToday;
  const todayHasMemories = useMemo(() => {
    return (
      chaptersForDate(chapters, todayKey).length > 0
      || smallMemoriesForDate(smallMemoriesByDate, todayKey).length > 0
    );
  }, [chapters, smallMemoriesByDate, todayKey]);

  const todayFeed = useMemo(() => {
    if (!isViewingToday) return [];
    return buildDayFeed(
      todayKey,
      todayKey,
      chapters,
      smallMemoriesForDate(smallMemoriesByDate, todayKey),
    );
  }, [chapters, smallMemoriesByDate, isViewingToday, todayKey]);

  const selectedDayFeed = useMemo(() => {
    if (isViewingToday) return [];
    return buildDayFeed(
      selectedDateKey,
      todayKey,
      chapters,
      smallMemoriesForDate(smallMemoriesByDate, selectedDateKey),
    );
  }, [chapters, smallMemoriesByDate, isViewingToday, selectedDateKey, todayKey]);

  const earlierBlocks = useMemo(
    () => buildEarlierFeed(chapters, todayKey, historyVisibleCount),
    [chapters, todayKey, historyVisibleCount],
  );

  const hasMoreHistory =
    chapters.filter((c) => c.dateKey !== todayKey).length > historyVisibleCount;

  const recapDateKey = isViewingToday ? todayKey : selectedDateKey;
  const recapHasChapters = chaptersForDate(chapters, recapDateKey).length > 0;

  const selectedPastDayEmpty =
    !isViewingToday
    && chaptersForDate(chapters, selectedDateKey).length === 0
    && smallMemoriesForDate(smallMemoriesByDate, selectedDateKey).length === 0;

  const renderFeed = (items: ReturnType<typeof buildDayFeed>, showDateOnCard: boolean) =>
    items.map((item, index) => {
      if (item.kind === 'day_header') {
        return (
          <View key={`h-${index}`} style={styles.dayHeader}>
            <Text style={styles.dayTitle}>{item.label}</Text>
            {item.sub ? <Text style={styles.daySub}>{item.sub}</Text> : null}
          </View>
        );
      }
      if (item.kind === 'small') {
        return <SmallMemory key={item.memory.id} text={item.memory.text} />;
      }
      const c = item.chapter;
      return (
        <ChapterBlock
          key={c.id}
          title={c.title}
          dateLabel={c.dateLabel}
          weakTime={c.weakTime}
          aiStory={c.aiStory}
          tags={c.tags}
          heroUri={c.heroUri}
          showDateMeta={showDateOnCard}
          onPress={() => navigation.navigate('ChapterDetail', { chapterId: c.id })}
        />
      );
    });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaScreenHeader
        title="Diary"
        rightAccessory={
          <Pressable
            onPress={() => navigation.navigate('Search', {})}
            hitSlop={12}
            accessibilityRole="button"
            accessibilityLabel="Search memories"
          >
            <Text style={styles.searchLink}>Search</Text>
          </Pressable>
        }
      />
      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.gutter}>
          <MemoryCalendar
            expanded={false}
            selectedDateKey={selectedDateKey}
            todayKey={todayKey}
            markedDays={marked}
            dayPreparing={calendarDayPreparing}
            onToggleExpanded={() => navigation.navigate('CalendarExpanded')}
            onSelectDate={selectDateKeyWithPrepare}
            onJumpToday={() => selectDateKeyWithPrepare(todayKey)}
          />

          <TodayStatusDevPicker status={todayStatus} onChange={setTodayStatus} />

          {pipelineTask ? <CloudProcessingBanner task={pipelineTask} /> : null}

          <DayPrepareBanner
            visible={
              calendarDayPreparing
              || (isViewingToday && (todayStatus === 'PREPARING' || todayStatus === 'READY_PREPARING'))
            }
          />

          {showTodayBanner ? (
            <TodayStatusBanner
              status={todayStatus}
              onSyncPress={() => {
                void performDeviceSync();
              }}
            />
          ) : null}

          <View
            style={calendarDayPreparing ? styles.feedPreparing : undefined}
            pointerEvents={calendarDayPreparing ? 'none' : 'auto'}
          >
          {isViewingToday && !todayHasMemories && (todayStatus === 'ZERO_CURATED' || todayStatus === 'NO_RECORDINGS') ? (
            <Text style={styles.emptyToday}>
              {todayStatus === 'NO_RECORDINGS'
                ? 'No recordings today.'
                : 'No memories were created from today\'s recordings.'}
            </Text>
          ) : null}

          {recapHasChapters ? (
            <Pressable
              style={styles.recapRow}
              onPress={() => navigation.navigate('ShareDaySelector', { dateKey: recapDateKey })}
            >
              <Text style={styles.recapLabel}>Share day</Text>
              <Text style={styles.recapHint}>Daily Recap · photo collage</Text>
            </Pressable>
          ) : null}

          {isViewingToday ? renderFeed(todayFeed, false) : renderFeed(selectedDayFeed, true)}

          {selectedPastDayEmpty ? (
            <Text style={styles.emptyToday}>No memories for this day.</Text>
          ) : null}

          {isViewingToday ? (
            <>
              {earlierBlocks.map((block) => (
                <View key={block.dateKey}>{renderFeed(block.items, true)}</View>
              ))}
              {historyLoadState === 'loading' ? (
                <Text style={styles.loadStatus}>Loading earlier memories…</Text>
              ) : null}
              {historyLoadState === 'failed' ? (
                <View style={styles.loadFailed}>
                  <Text style={styles.loadFailedText}>Couldn&apos;t load earlier memories.</Text>
                  <Pressable onPress={loadMoreHistory}>
                    <Text style={styles.tryAgain}>Try Again</Text>
                  </Pressable>
                </View>
              ) : null}
              {hasMoreHistory && historyLoadState === 'idle' ? (
                <Pressable onPress={loadMoreHistory} style={styles.loadMore}>
                  <Text style={styles.loadMoreText}>Load earlier memories</Text>
                </Pressable>
              ) : null}
            </>
          ) : null}
          </View>
        </View>
      </ScrollView>
      <ShareDayReadinessSheet
        visible={dailyRecapShareBlockedBanner}
        onDismiss={() => setDailyRecapShareBlockedBanner(false)}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingBottom: spacing.xl },
  gutter: { paddingHorizontal: layout.gutterDiary },
  dayHeader: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: spacing.sm,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  dayTitle: { fontSize: font.h2, fontWeight: '700', color: colors.ink },
  daySub: { fontSize: font.small, color: colors.tertiary },
  loadMore: {
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.md,
  },
  loadMoreText: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  loadStatus: {
    textAlign: 'center',
    fontSize: font.small,
    color: colors.secondary,
    marginTop: spacing.md,
  },
  loadFailed: { alignItems: 'center', marginTop: spacing.md, gap: spacing.sm },
  loadFailedText: { fontSize: font.small, color: colors.secondary },
  tryAgain: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  searchLink: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  emptyToday: {
    fontSize: font.body,
    color: colors.secondary,
    marginBottom: spacing.md,
    lineHeight: 22,
  },
  recapRow: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  recapLabel: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  recapHint: { fontSize: font.micro, color: colors.tertiary, marginTop: 4 },
  feedPreparing: { opacity: 0.42 },
});
