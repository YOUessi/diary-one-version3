import React, { useCallback, useState } from 'react';
import {
  ScrollView,
  View,
  Text,
  Pressable,
  StyleSheet,
  Alert,
  Image,
} from 'react-native';
import { useFocusEffect, useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MemoryTag } from '../../components/MemoryTag';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { MomentMedia } from '../../components/MomentMedia';
import { YourStorySheet, type YourStorySaveState } from '../../components/YourStorySheet';
import { useAppBackgroundPause } from '../../hooks/useAppBackgroundPause';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';
import { STORY_DISCARD_ALERT } from '../../domain/discardCopy';
import { formatChapterDateLong } from '../../domain/formatChapterDate';

type Route = RouteProp<DiaryStackParamList, 'ChapterDetail'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ChapterDetail'>;

/** Alternates load-failure banner on every other chapter open (APP045). */
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
  const [storyJustSaved, setStoryJustSaved] = useState(false);
  const storySaveFailAlternate = React.useRef(false);

  const stopPlayback = useCallback(() => setPlayingMomentId(null), []);
  useFocusEffect(useCallback(() => () => stopPlayback(), [stopPlayback]));

  React.useEffect(() => {
    if (!chapter?.yourStory) return;
    if (yourStoryLoadFailNext) {
      yourStoryLoadFailNext = false;
      setStoryLoadFailed(true);
    } else {
      yourStoryLoadFailNext = true;
    }
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
      if (storySaveFailAlternate.current) {
        storySaveFailAlternate.current = false;
        setSaveState('failed');
        return;
      }
      storySaveFailAlternate.current = true;
      updateYourStory(chapterId, trimmed);
      setDirty(false);
      setSaveState('idle');
      setSheetOpen(false);
      setStoryJustSaved(true);
      setTimeout(() => setStoryJustSaved(false), 2400);
    }, 550);
  };

  const closeSheet = () => {
    if (dirty) {
      Alert.alert(STORY_DISCARD_ALERT.title, STORY_DISCARD_ALERT.message, [
        { text: STORY_DISCARD_ALERT.keepEditing, style: 'cancel' },
        {
          text: STORY_DISCARD_ALERT.discard,
          style: 'destructive',
          onPress: () => {
            setDirty(false);
            setSheetOpen(false);
          },
        },
      ]);
      return;
    }
    setSheetOpen(false);
  };

  const playMoment = (momentId: string) => {
    setPlayingMomentId(momentId);
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <FigmaBackHeader onBack={() => navigation.goBack()} />
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.hero}>
          {chapter.heroUri ? (
            <Image source={{ uri: chapter.heroUri }} style={styles.heroImage} resizeMode="cover" />
          ) : (
            <Text style={styles.heroHint}>Hero · static poster</Text>
          )}
        </View>
        <Text style={styles.title}>{chapter.title}</Text>
        <Text style={styles.meta}>
          {[formatChapterDateLong(chapter.dateKey), chapter.weakTime].filter(Boolean).join(' · ')}
        </Text>
        <View style={styles.tagRow} pointerEvents="none">
          {chapter.tags.map((t) => <MemoryTag key={t} label={t} tone="primary" />)}
        </View>
        <Text style={styles.body}>{chapter.aiStory}</Text>

        <View style={styles.storyHeader}>
          <Text style={styles.sectionLabelInline}>What you remember</Text>
          <View style={styles.storyHeaderTrailing}>
            {storyJustSaved ? <Text style={styles.savedPill}>Saved</Text> : null}
            <Pressable onPress={openEditor} hitSlop={8}>
              <Text style={styles.editLink}>Edit</Text>
            </Pressable>
          </View>
        </View>
        {storyLoadFailed ? (
          <View style={styles.storyLoadFailed}>
            <Text style={styles.storyLoadTitle}>Your note couldn&apos;t be loaded</Text>
            <Text style={styles.storyLoadBody}>Your saved note has not been changed.</Text>
            <Pressable onPress={() => setStoryLoadFailed(false)} hitSlop={8}>
              <Text style={styles.storyLoadRetry}>Try Again</Text>
            </Pressable>
          </View>
        ) : chapter.yourStory ? (
          <Text style={styles.body}>{chapter.yourStory}</Text>
        ) : (
          <Pressable onPress={openEditor} style={styles.addStory}>
            <Text style={styles.addStoryPlus}>+  Add what you remember</Text>
            <Text style={styles.addStoryHint}>
              Add a person, detail, or why this memory mattered to you.
            </Text>
          </Pressable>
        )}

        {chapter.moments.map((m) => {
          const playing = playingMomentId === m.id;
          const mediaUri = m.playbackUri ?? m.posterUri ?? chapter.heroUri;
          return (
            <View key={m.id} style={styles.moment}>
              <Text style={[styles.momentLabel, playing && styles.momentLabelPlaying]}>{m.label}</Text>
              {mediaUri ? (
                <MomentMedia
                  uri={mediaUri}
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
              {m.capturedByYou ? (
                <Text style={styles.capturedMeta}>Captured by you</Text>
              ) : null}
            </View>
          );
        })}

        {chapter.detailTags && chapter.detailTags.length > 0 ? (
          <>
            <Text style={styles.sectionLabel}>More about this memory</Text>
            <View style={styles.tagRow} pointerEvents="none">
              {chapter.detailTags.map((t) => <MemoryTag key={t} label={t} tone="neutral" />)}
            </View>
          </>
        ) : null}
      </ScrollView>

      <Pressable
        style={styles.shareBar}
        onPress={() => navigation.navigate('ShareMemorySelector', { chapterId })}
      >
        <Text style={styles.shareLabel}>Share memory</Text>
      </Pressable>

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
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  hero: {
    aspectRatio: 4 / 3,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
    overflow: 'hidden',
  },
  heroImage: { width: '100%', height: '100%' },
  heroHint: { color: colors.tertiary, fontSize: font.small },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, letterSpacing: -0.2 },
  meta: { fontSize: font.small, color: colors.tertiary, marginTop: 4 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', marginTop: spacing.sm },
  sectionLabel: {
    fontSize: font.micro,
    fontWeight: '600',
    color: colors.secondary,
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  sectionLabelInline: {
    fontSize: font.micro,
    fontWeight: '600',
    color: colors.secondary,
    textTransform: 'uppercase',
    letterSpacing: 0.6,
  },
  storyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
  },
  storyHeaderTrailing: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  savedPill: { fontSize: font.micro, fontWeight: '600', color: colors.secondary },
  editLink: { fontSize: font.small, fontWeight: '600', color: colors.accent },
  momentLabel: { fontSize: font.small, color: colors.tertiary, marginBottom: spacing.xs },
  momentLabelPlaying: { color: colors.accent, fontWeight: '600' },
  body: { fontSize: font.body, lineHeight: 24, color: colors.ink },
  moment: { marginBottom: spacing.md },
  momentPoster: {
    height: 200,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    alignItems: 'center',
    justifyContent: 'center',
  },
  momentPosterActive: { borderWidth: 2, borderColor: colors.accent },
  momentHint: { fontSize: font.small, color: colors.tertiary },
  capturedMeta: { fontSize: font.micro, color: colors.secondary, marginTop: 4 },
  addStory: { marginBottom: spacing.md },
  addStoryPlus: { fontSize: font.body, fontWeight: '600', color: colors.accent },
  addStoryHint: { fontSize: font.small, color: colors.secondary, marginTop: 4, lineHeight: 20 },
  storyLoadFailed: {
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.md,
    gap: spacing.xs,
  },
  storyLoadTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  storyLoadBody: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  storyLoadRetry: { fontSize: font.small, fontWeight: '600', color: colors.accent, marginTop: spacing.sm },
  shareBar: {
    marginHorizontal: layout.gutterDiary,
    marginBottom: spacing.md,
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  shareLabel: { color: colors.paper, fontWeight: '700', fontSize: font.body },
  missing: { padding: layout.gutterDiary, fontSize: font.body, color: colors.ink },
  back: { padding: layout.gutterDiary, color: colors.accent },
});
