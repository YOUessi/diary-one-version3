import React, { useCallback, useState } from 'react';
import {
  ScrollView,
  View,
  Text,
  Pressable,
  StyleSheet,
  Image,
} from 'react-native';
import { useFocusEffect, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MemoryTag } from '../../components/MemoryTag';
import { MomentMedia } from '../../components/MomentMedia';
import { YourStorySheet, type YourStorySaveState } from '../../components/YourStorySheet';
import { ShareGlyph } from '../../components/ShareGlyph';
import { useAppBackgroundPause } from '../../hooks/useAppBackgroundPause';
import { colors, layout, radius, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { isDevFailSimulationEnabled } from '../../config/devFailSimulation';

type Route = RouteProp<DiaryStackParamList, 'ChapterDetail'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ChapterDetail'>;

let yourStoryLoadFailNext = false;

export default function ChapterDetailScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const updateYourStory = useAppStore((s) => s.updateYourStory);

  const [sheetOpen, setSheetOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [dirty, setDirty] = useState(false);
  const [playingMomentId, setPlayingMomentId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<YourStorySaveState>('idle');
  const [storyLoadFailed, setStoryLoadFailed] = useState(false);
  const storySaveFailAlternate = React.useRef(false); // used only when Lab fail-sim is on

  const stopPlayback = useCallback(() => setPlayingMomentId(null), []);
  useFocusEffect(useCallback(() => () => stopPlayback(), [stopPlayback]));

  React.useEffect(() => {
    if (!chapter?.yourStory) return;
    if (!isDevFailSimulationEnabled()) {
      setStoryLoadFailed(false);
      return;
    }
    if (yourStoryLoadFailNext) {
      yourStoryLoadFailNext = false;
      setStoryLoadFailed(true);
      return;
    }
    yourStoryLoadFailNext = true;
    setStoryLoadFailed(false);
  }, [chapterId, chapter?.yourStory]);
  useAppBackgroundPause(stopPlayback);

  if (!chapter) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text style={styles.missing}>Memory unavailable.</Text>
        <Pressable onPress={() => navigation.goBack()}>
          <Text style={styles.back}>Go back</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  const openEditor = () => {
    setDraft(chapter.yourStory ?? '');
    setDirty(false);
    setSheetOpen(true);
  };

  const saveStory = () => {
    const trimmed = draft.trim();
    if (!trimmed) return;
    setSaveState('saving');
    setTimeout(() => {
      if (isDevFailSimulationEnabled() && storySaveFailAlternate.current) {
        storySaveFailAlternate.current = false;
        setSaveState('failed');
        return;
      }
      if (isDevFailSimulationEnabled()) storySaveFailAlternate.current = true;
      updateYourStory(chapterId, trimmed);
      setDirty(false);
      setSaveState('idle');
      setSheetOpen(false);
    }, 550);
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

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.nav}>
        <Pressable
          onPress={() => navigation.goBack()}
          style={styles.navBtn}
          hitSlop={8}
          accessibilityRole="button"
          accessibilityLabel="Back"
        >
          <Text style={styles.backChevron}>‹</Text>
        </Pressable>
        <Pressable
          onPress={() => navigation.navigate('ShareMemorySelector', { chapterId })}
          style={styles.navBtn}
          hitSlop={8}
          accessibilityRole="button"
          accessibilityLabel="Share memory"
        >
          <ShareGlyph />
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.hero}>
          {chapter.heroUri ? (
            <Image source={{ uri: chapter.heroUri }} style={styles.heroImage} resizeMode="cover" />
          ) : (
            <View style={styles.heroPlaceholder}>
              <View style={styles.sun} />
              <View style={styles.wave} />
            </View>
          )}
        </View>

        <View style={styles.intro}>
          <Text style={styles.title}>{chapter.title}</Text>
          <Text style={styles.meta}>
            {[formatChapterDateLong(chapter.dateKey), chapter.weakTime].filter(Boolean).join(' · ')}
          </Text>
          <View style={styles.tagRow} pointerEvents="none">
            {chapter.tags.slice(0, 2).map((t) => (
              <MemoryTag key={t} label={t} tone="primary" />
            ))}
          </View>
          <Text style={styles.aiStory}>{chapter.aiStory}</Text>
        </View>

        <View style={styles.yourStoryBlock}>
          {storyLoadFailed ? (
            <View style={styles.storyLoadFailed}>
              <Text style={styles.storyLoadTitle}>Your note couldn&apos;t be loaded</Text>
              <Text style={styles.storyLoadBody}>Your saved note has not been changed.</Text>
              <Pressable onPress={() => setStoryLoadFailed(false)} hitSlop={8}>
                <Text style={styles.storyLoadRetry}>Try Again</Text>
              </Pressable>
            </View>
          ) : chapter.yourStory ? (
            <>
              <View style={styles.storyHeader}>
                <Text style={styles.sectionTitle}>What you remember</Text>
                <Pressable onPress={openEditor} hitSlop={8} style={styles.editHit}>
                  <Text style={styles.editLink}>Edit</Text>
                </Pressable>
              </View>
              <View style={styles.storyBody}>
                <View style={styles.storyMark} />
                <Text style={styles.yourStoryText}>{chapter.yourStory}</Text>
              </View>
            </>
          ) : (
            <Pressable onPress={openEditor} style={styles.addStory}>
              <Text style={styles.addStoryPlus}>+  Add what you remember</Text>
              <Text style={styles.addStoryHint}>
                Add a person, detail, or why this memory mattered to you.
              </Text>
            </Pressable>
          )}
        </View>

        <View style={styles.moments}>
          {chapter.moments.map((m) => {
            const playing = playingMomentId === m.id;
            const posterUri = m.posterUri ?? chapter.heroUri;
            const playbackUri = m.playbackUri ?? posterUri;
            return (
              <View key={m.id} style={styles.moment}>
                {posterUri || playbackUri ? (
                  <MomentMedia
                    uri={posterUri ?? playbackUri!}
                    playbackUri={playbackUri}
                    playing={playing}
                    onPlay={() => playMoment(m.id)}
                    onStop={stopPlayback}
                  />
                ) : (
                  <Pressable
                    onPress={() => playMoment(m.id)}
                    style={[styles.momentPoster, playing && styles.momentPosterActive]}
                  >
                    <Text style={styles.momentHint}>
                      {playing ? 'Playing (tap to stop)' : 'Tap to play'}
                    </Text>
                  </Pressable>
                )}
                <Text style={[styles.momentLabel, playing && styles.momentLabelPlaying]}>{m.label}</Text>
                {m.capturedByYou ? (
                  <Text style={styles.capturedMeta}>Captured by you</Text>
                ) : null}
              </View>
            );
          })}
        </View>

        {chapter.detailTags && chapter.detailTags.length > 0 ? (
          <View style={styles.moreBlock}>
            <Text style={styles.sectionTitle}>More about this memory</Text>
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
        onSave={saveStory}
        onRemove={() => navigation.navigate('YourStoryRemoveConfirm', { chapterId })}
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
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center' },
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
  addStory: { marginBottom: spacing.sm },
  addStoryPlus: { ...type.bodyStory, fontWeight: '600', color: colors.accent },
  addStoryHint: { ...type.caption, color: colors.secondary, marginTop: 4 },
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
