import { appStrings } from '../../domain/strings';
import { showImportFailure } from '../../pipeline/importFailure';
import React, { useMemo } from 'react';
import { Alert, ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, spacing, type } from '../../theme';
import { ChapterBlock } from '../../components/ChapterBlock';
import { SmallMemory } from '../../components/SmallMemory';
import { TodayStatusBanner } from '../../components/TodayStatus';
import { MemoryCalendar } from '../../components/MemoryCalendar';
import { FigmaScreenHeader } from '../../components/FigmaScreenHeader';
import { SearchGlyph } from '../../components/SearchGlyph';
import { ShareGlyph } from '../../components/ShareGlyph';
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
import { buildDayFeed, buildEarlierFeed, historyDateKeys } from '../../diary/buildDiaryFeed';
import { DayPrepareBanner } from '../../components/DayPrepareBanner';
import { ShareDayReadinessSheet } from '../../components/ShareDayReadinessSheet';
import { CloudProcessingBanner } from '../../components/CloudProcessingBanner';
import { activePipelineTask } from '../../pipeline/pipelineActive';

type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DiaryHome'>;

export default function DiaryHomeScreen() {
  const navigation = useNavigation<Nav>();
  const language = useAppStore((s) => s.language);
  const strings = appStrings(language);
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
      smallMemoriesForDate(smallMemoriesByDate, todayKey), language,
    );
  }, [chapters, smallMemoriesByDate, isViewingToday, todayKey, language]);

  const selectedDayFeed = useMemo(() => {
    if (isViewingToday) return [];
    return buildDayFeed(
      selectedDateKey,
      todayKey,
      chapters,
      smallMemoriesForDate(smallMemoriesByDate, selectedDateKey), language,
    );
  }, [chapters, smallMemoriesByDate, isViewingToday, selectedDateKey, todayKey, language]);

  const earlierBlocks = useMemo(
    () => buildEarlierFeed(chapters, todayKey, historyVisibleCount, language, smallMemoriesByDate),
    [chapters, todayKey, historyVisibleCount, language, smallMemoriesByDate],
  );

  const hasMoreHistory =
    historyDateKeys(chapters, smallMemoriesByDate, todayKey).length > historyVisibleCount;

  const recapDateKey = isViewingToday ? todayKey : selectedDateKey;
  const recapHasChapters = chaptersForDate(chapters, recapDateKey).length > 0;

  const selectedPastDayEmpty =
    !isViewingToday
    && chaptersForDate(chapters, selectedDateKey).length === 0
    && smallMemoriesForDate(smallMemoriesByDate, selectedDateKey).length === 0;

  const renderFeed = (items: ReturnType<typeof buildDayFeed>, isTodaySection: boolean) =>
    items.map((item, index) => {
      if (item.kind === 'day_header') {
        const isToday = item.label === strings.today;
        return (
          <View key={`h-${index}`} style={[styles.dayHeader, isToday && styles.dayHeaderToday]}>
            <Text style={[styles.dayTitle, isToday ? styles.dayTitleToday : styles.dayTitlePast]}>
              {item.label}
            </Text>
            <View style={styles.dayHeaderTrailing}>
              {item.sub ? <Text style={styles.daySub}>{item.sub}</Text> : null}
              {isTodaySection && isToday && recapHasChapters ? (
                <Pressable
                  onPress={() => navigation.navigate('ShareDaySelector', { dateKey: recapDateKey })}
                  hitSlop={8}
                  accessibilityRole="button"
                  accessibilityLabel={strings.shareDay}
                  style={styles.shareHit}
                >
                  <ShareGlyph />
                </Pressable>
              ) : null}
            </View>
          </View>
        );
      }
      if (item.kind === 'small') {
        return <SmallMemory key={item.memory.id} text={item.memory.text} posterUri={item.memory.posterUri} />;
      }
      const c = item.chapter;
      return (
        <ChapterBlock
          key={c.id}
          title={c.title}
          dateLabel={c.dateLabel}
          weakTime={c.weakTime}
          aiStory={c.previewStory?.trim() || c.aiStory}
          tags={c.tags}
          heroUri={c.heroUri}
          showDateMeta={false}
          onPress={() => navigation.navigate('ChapterDetail', { chapterId: c.id })}
        />
      );
    });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.gutter}>
          <FigmaScreenHeader
            title={strings.tabDiary}
            rightAccessory={
              <Pressable
                onPress={() => navigation.navigate('Search', {})}
                hitSlop={8}
                accessibilityRole="button"
                accessibilityLabel={strings.searchMemories}
              >
                <SearchGlyph />
              </Pressable>
            }
          />

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

          <DayPrepareBanner visible={calendarDayPreparing} />

          {showTodayBanner ? (
            <TodayStatusBanner
              status={todayStatus}
              onSyncPress={() => {
                const link = useAppStore.getState().deviceLinkState;
                if (link === 'disconnected') {
                  Alert.alert(strings.deviceConnectionTitle, strings.hardwareUnavailable);
                  return;
                }
                void performDeviceSync();
              }}
            />
          ) : null}

          <View
            style={[styles.section, calendarDayPreparing ? styles.feedPreparing : undefined]}
            pointerEvents={calendarDayPreparing ? 'none' : 'auto'}
          >
            {isViewingToday && !todayHasMemories && (todayStatus === 'ZERO_CURATED' || todayStatus === 'NO_RECORDINGS') ? (
              <View style={styles.emptyBlock}>
                <Text style={styles.emptyToday}>
                  {todayStatus === 'NO_RECORDINGS'
                    ? strings.noToday
                    : strings.noCuratedToday}
                </Text>
                <Text style={styles.emptyHint}>
                  {strings.uploadLead}
                </Text>
                <Pressable
                  style={styles.uploadBtn}
                  accessibilityRole="button"
                  accessibilityLabel={strings.uploadMedia}
                  onPress={() =>
                    void import('../../pipeline/launchEvidenceImport').then((m) =>
                      m.launchEvidenceImportFromLibrary(),
                    ).catch((error) => showImportFailure(error, 'START'))
                  }
                >
                  <Text style={styles.uploadBtnLabel}>{strings.uploadMedia}</Text>
                </Pressable>
              </View>
            ) : null}

            {isViewingToday ? renderFeed(todayFeed, true) : renderFeed(selectedDayFeed, false)}

            {selectedPastDayEmpty ? (
              <Text style={styles.emptyToday}>{strings.emptyDay}</Text>
            ) : null}
          </View>

          {isViewingToday ? (
            <>
              {earlierBlocks.map((block) => (
                <View key={block.dateKey} style={styles.section}>
                  {renderFeed(block.items, false)}
                </View>
              ))}
              {historyLoadState === 'loading' ? (
                <Text style={styles.loadStatus}>{strings.loadingHistory}</Text>
              ) : null}
              {historyLoadState === 'failed' ? (
                <View style={styles.loadFailed}>
                  <Text style={styles.loadFailedText}>{strings.historyFailed}</Text>
                  <Pressable onPress={loadMoreHistory}>
                    <Text style={styles.tryAgain}>{strings.retry}</Text>
                  </Pressable>
                </View>
              ) : null}
              {hasMoreHistory && historyLoadState === 'idle' ? (
                <Pressable onPress={loadMoreHistory} style={styles.loadMore}>
                  <Text style={styles.loadMoreText}>{strings.loadHistory}</Text>
                </Pressable>
              ) : null}
            </>
          ) : null}
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
  scroll: {
    paddingBottom: layout.tabBarHeight + spacing.xxxl + spacing.lg,
  },
  gutter: {
    paddingHorizontal: layout.gutterDiary,
    gap: spacing.xxl,
  },
  section: {
    gap: spacing.xl,
    width: '100%',
  },
  dayHeader: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    minHeight: 32,
    width: '100%',
  },
  dayHeaderToday: { minHeight: 40 },
  dayHeaderTrailing: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: spacing.xs,
  },
  dayTitle: { color: colors.ink },
  dayTitleToday: { ...type.titleSection },
  dayTitlePast: { ...type.titleChapter },
  daySub: {
    ...type.caption,
    color: colors.tertiary,
    textAlign: 'right',
    minWidth: 80,
    marginBottom: 2,
  },
  shareHit: {
    width: layout.minTouch,
    height: layout.minTouch,
    marginBottom: -4,
  },
  loadMore: {
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.md,
  },
  loadMoreText: { ...type.captionEmphasis, color: colors.accent },
  loadStatus: {
    textAlign: 'center',
    ...type.caption,
    color: colors.secondary,
    marginTop: spacing.md,
  },
  loadFailed: { alignItems: 'center', marginTop: spacing.md, gap: spacing.sm },
  loadFailedText: { ...type.caption, color: colors.secondary },
  tryAgain: { ...type.captionEmphasis, color: colors.accent },
  emptyToday: {
    ...type.bodyStory,
    color: colors.secondary,
  },
  emptyBlock: { gap: spacing.sm },
  emptyHint: { ...type.caption, color: colors.tertiary, lineHeight: 20 },
  uploadBtn: {
    marginTop: spacing.xs,
    height: 52,
    borderRadius: 12,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadBtnLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.paper },
  feedPreparing: { opacity: 0.42 },
});
