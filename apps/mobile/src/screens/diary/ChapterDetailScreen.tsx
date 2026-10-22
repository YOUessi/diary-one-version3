import { appStrings, momentLabel } from '../../domain/strings';
import React, { useCallback, useState } from 'react';
import {
  ScrollView,
  View,
  Text,
  Pressable,
  StyleSheet,
} from 'react-native';
import { useFocusEffect, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MemoryTag } from '../../components/MemoryTag';
import { MomentMedia } from '../../components/MomentMedia';
import { SmallMemory } from '../../components/SmallMemory';
import { HeroLiveCarousel } from '../../components/HeroLiveCarousel';
import { YourStorySheet, type YourStorySaveState } from '../../components/YourStorySheet';
import { ShareGlyph } from '../../components/ShareGlyph';
import { useAppBackgroundPause } from '../../hooks/useAppBackgroundPause';
import { colors, layout, radius, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { saveYourStory } from '../../backend/storyRepository';
import { isDevFailSimulationEnabled } from '../../config/devFailSimulation';
import { chapterSlides } from '../../domain/chapterSlides';
import { chapterMediaEntries } from '../../domain/chapterPresentation';

type Route = RouteProp<DiaryStackParamList, 'ChapterDetail'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ChapterDetail'>;



export default function ChapterDetailScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const language = useAppStore((s) => s.language);
  const strings = appStrings(language);
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const editorRevision = React.useRef(0);
  const saving = React.useRef(false);

  const [sheetOpen, setSheetOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [dirty, setDirty] = useState(false);
  const [playingMomentId, setPlayingMomentId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<YourStorySaveState>('idle');
  const storySaveFailAlternate = React.useRef(false); // used only when Lab fail-sim is on

  const stopPlayback = useCallback(() => setPlayingMomentId(null), []);
  useFocusEffect(useCallback(() => () => stopPlayback(), [stopPlayback]));

  useAppBackgroundPause(stopPlayback);

  if (!chapter) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.missing}>{strings.memoryUnavailable}</Text>
        <Pressable onPress={() => navigation.goBack()}>
          <Text style={styles.back}>{strings.back}</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  const openEditor = () => {
    stopPlayback();
    editorRevision.current = chapter.yourStoryRevision ?? 0;
    setDraft(chapter.yourStory ?? '');
    setDirty(false);
    setSheetOpen(true);
  };

  const saveStory = async () => {
    const trimmed = draft.trim();
    if (!trimmed || saving.current) return;
    saving.current = true;
    setSaveState('saving');
    try {
      if (isDevFailSimulationEnabled() && storySaveFailAlternate.current) {
        storySaveFailAlternate.current = false;
        throw new Error('Simulated write failure');
      }
      await saveYourStory(chapterId, trimmed, editorRevision.current);
      if (isDevFailSimulationEnabled()) storySaveFailAlternate.current = true;
      setDirty(false);
      setSaveState('idle');
      setSheetOpen(false);
    } catch {
      setSaveState('failed');
    } finally {
      saving.current = false;
    }
  };

  /** Discard confirm lives in YourStorySheet (Figma card, not system Alert). */
  const closeSheet = () => {
    setDirty(false);
    setSaveState('idle');
    setSheetOpen(false);
  };

  const playMoment = (momentId: string) => {
    setPlayingMomentId(momentId);
  };
  const mediaEntries = chapterMediaEntries(chapter);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.nav}>
        <Pressable
          onPress={() => navigation.goBack()}
          style={styles.navBtn}
          hitSlop={8}
          accessibilityRole="button"
          accessibilityLabel={strings.back}
        >
          <Text style={styles.backChevron}>‹</Text>
        </Pressable>
        <Pressable
          onPress={() => { stopPlayback(); navigation.navigate('ShareMemorySelector', { chapterId }); }}
          style={styles.navBtn}
          hitSlop={8}
          accessibilityRole="button"
          accessibilityLabel={strings.shareMemory}
        >
          <ShareGlyph />
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false} onScrollBeginDrag={stopPlayback}>
        <HeroLiveCarousel
          key={chapterId}
          playbackScope={chapterId}
          activePlaybackId={playingMomentId}
          onPlay={setPlayingMomentId}
          onStop={stopPlayback}
          slides={chapterSlides(chapter).map((slide) => ({ ...slide, title: momentLabel(slide.title, language) }))}
        />

        <View style={styles.intro}>
          <Text style={styles.title}>{chapter.title}</Text>
          <Text style={styles.meta}>
            {[formatChapterDateLong(chapter.dateKey, language), chapter.weakTime].filter(Boolean).join(' · ')}
          </Text>
          {chapter.tags.length > 0 ? <View style={styles.tagRow} pointerEvents="none">
            {chapter.tags.slice(0, 2).map((t) => (
              <MemoryTag key={t} label={t} tone="primary" />
            ))}
          </View> : null}
          <Text style={styles.aiStory}>{chapter.aiStory}</Text>
        </View>

        <View style={styles.yourStoryBlock}>
          { chapter.yourStory ? (
            <>
              <View style={styles.storyHeader}>
                <Text style={styles.sectionTitle}>{strings.whatYouRemember}</Text>
                <Pressable onPress={openEditor} hitSlop={8} style={styles.editHit}>
                  <Text style={styles.editLink}>{strings.edit}</Text>
                </Pressable>
              </View>
              <View style={styles.storyBody}>
                <View style={styles.storyMark} />
                <Text style={styles.yourStoryText}>{chapter.yourStory}</Text>
              </View>
            </>
          ) : (
            <Pressable onPress={openEditor} style={styles.addStory}>
              <Text style={styles.addStoryPlus}>+  {strings.addStory}</Text>
              <Text style={styles.addStoryHint}>
                {strings.storyHint}
              </Text>
            </Pressable>
          )}
        </View>

        <View style={styles.moments}>
          {mediaEntries.length === 0 ? (
            <View style={styles.moment}>
              {chapter.heroUri ? (
                <MomentMedia
                  uri={chapter.heroUri}
                  playbackUri={chapter.heroUri}
                  playing={false}
                  onPlay={() => {}}
                  onStop={() => {}}
                />
              ) : (
                <View style={styles.momentPoster}>
                  <Text style={styles.momentHint}>{strings.mediaUnavailable}</Text>
                </View>
              )}
            </View>
          ) : (
            mediaEntries.map((entry) => {
              const m = entry.media;
              if (!m) return <View key={entry.id}>{entry.texts.map((text, i) =>
                <SmallMemory key={i} text={text} />)}</View>;
              const playing = playingMomentId === m.id;
              const posterUri = m.posterUri ?? m.playbackUri;
              const playbackUri = m.playbackUri ?? m.posterUri;
              return (
                <View key={m.id} style={styles.moment}>
                  {entry.texts.map((text, i) => <SmallMemory key={i} text={text} />)}
                  {posterUri || playbackUri ? (
                    <MomentMedia
                      uri={posterUri ?? playbackUri!}
                      playbackUri={playbackUri}
                      focusTimeSec={m.focusTimeSec}
                      playing={playing}
                      onPlay={() => playMoment(m.id)}
                      onStop={stopPlayback}
                    />
                  ) : (
                    <View style={styles.momentPoster}>
                      <Text style={styles.momentHint}>{strings.mediaUnavailable}</Text>
                    </View>
                  )}
                  <Text style={[styles.momentLabel, playing && styles.momentLabelPlaying]}>{momentLabel(m.label, language)}</Text>
                  {m.capturedByYou ? (
                    <Text style={styles.capturedMeta}>{strings.capturedByYou}</Text>
                  ) : null}
                </View>
              );
            })
          )}
        </View>

        {chapter.detailTags && chapter.detailTags.length > 0 ? (
          <View style={styles.moreBlock}>
            <Text style={styles.sectionTitle}>{strings.moreAboutMemory}</Text>
            <View style={styles.tagRow} pointerEvents="none">
              {chapter.detailTags.map((t) => (
                <MemoryTag key={t} label={t} tone="neutral" />
              ))}
            </View>
          </View>
        ) : null}

        <View style={styles.bottomSpace} />
      </ScrollView>

      <YourStorySheet
        open={sheetOpen}
        draft={draft}
        dirty={dirty}
        saveState={saveState}
        hasExistingStory={Boolean(chapter.yourStory)}
        onChangeDraft={(t) => {
          setDraft(t);
          setDirty(true);
        }}
        onClose={closeSheet}
        onSave={() => void saveStory()}
        onRemove={() => { setSheetOpen(false); stopPlayback(); navigation.navigate('YourStoryRemoveConfirm', { chapterId }); }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  nav: {
    height: 52,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    backgroundColor: colors.paper,
  },
  navBtn: {
    width: layout.minTouch,
    height: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backChevron: {
    fontSize: 32,
    color: colors.ink,
    fontWeight: '300',
    marginTop: -2,
  },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    gap: spacing.xxxl,
    paddingBottom: spacing.xxxl,
  },
  hero: {
    width: '100%',
    height: layout.heroDetail,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    overflow: 'hidden',
  },
  heroImage: { width: '100%', height: '100%' },
  heroPlaceholder: { flex: 1, backgroundColor: colors.surface },
  sun: {
    position: 'absolute',
    top: 31,
    right: 46,
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: '#F5E6C8',
  },
  wave: {
    position: 'absolute',
    left: -35,
    bottom: -40,
    width: 424,
    height: 168,
    borderRadius: 210,
    backgroundColor: '#F7F5F0',
  },
  intro: { gap: 10, width: '100%' },
  title: { ...type.titleSection, color: colors.ink },
  meta: { ...type.caption, color: colors.tertiary },
  tagRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: spacing.sm,
  },
  aiStory: { ...type.bodyStory, color: colors.secondary },
  yourStoryBlock: { gap: 10, width: '100%' },
  storyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 44,
  },
  sectionTitle: { ...type.titleChapter, color: colors.ink, flex: 1 },
  editHit: {
    width: 56,
    height: 44,
    alignItems: 'flex-end',
    justifyContent: 'center',
  },
  editLink: { ...type.captionEmphasis, color: colors.secondary, textAlign: 'right' },
  storyBody: { flexDirection: 'row', gap: 12, width: '100%' },
  storyMark: {
    width: 2,
    alignSelf: 'stretch',
    backgroundColor: colors.accent,
    opacity: 0.55,
    borderRadius: 1,
  },
  yourStoryText: { ...type.bodyStory, color: colors.secondary, flex: 1 },
  moments: { gap: spacing.xl, width: '100%' },
  moment: { gap: spacing.sm, width: '100%' },
  momentLabel: { ...type.metadata, color: colors.tertiary },
  momentLabelPlaying: { color: colors.accent, fontWeight: '600' },
  momentPoster: {
    height: 198,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    alignItems: 'center',
    justifyContent: 'center',
  },
  momentPosterActive: { borderWidth: 2, borderColor: colors.accent },
  momentHint: { ...type.caption, color: colors.tertiary },
  capturedMeta: { ...type.caption, color: colors.secondary },
  moreBlock: { gap: 12, width: '100%' },
  /** Figma 112:1288 — white card r12 · h72 · ink title (not accent) */
  addStory: {
    backgroundColor: colors.card,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 11,
    minHeight: 72,
    gap: 4,
    marginBottom: spacing.sm,
  },
  addStoryPlus: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.ink },
  addStoryHint: { fontSize: 13, lineHeight: 18, color: colors.secondary },
  storyLoadFailed: {
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    padding: spacing.md,
    gap: spacing.xs,
  },
  storyLoadTitle: { ...type.bodyStory, fontWeight: '600', color: colors.ink },
  storyLoadBody: { ...type.caption, color: colors.secondary },
  storyLoadRetry: { ...type.captionEmphasis, color: colors.accent, marginTop: spacing.sm },
  bottomSpace: { height: 80 },
  missing: { padding: layout.gutterDiary, ...type.bodyStory, color: colors.ink },
  back: { padding: layout.gutterDiary, color: colors.accent },
});
