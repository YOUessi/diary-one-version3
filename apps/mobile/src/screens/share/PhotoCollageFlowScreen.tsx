import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { buildChapterPhotoCollage } from '../../share/buildPhotoCollage';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFlowCancelHeader } from '../../components/ShareFlowCancelHeader';

type Route = RouteProp<DiaryStackParamList, 'PhotoCollageFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'PhotoCollageFlow'>;

const collageUriCache = new Map<string, string>();

export default function PhotoCollageFlowScreen() {
  const { chapterId, phase } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const [uri, setUri] = useState<string | null>(null);

  const runPrepare = useCallback(async () => {
    if (!chapter) {
      navigation.replace('PhotoCollageFlow', { chapterId, phase: 'failed' });
      return;
    }
    try {
      const out = await buildChapterPhotoCollage(chapter);
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('PhotoCollageFlow', { chapterId, phase: 'failed' });
        return;
      }
      collageUriCache.set(chapterId, out);
      setUri(out);
      navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preview' });
    } catch {
      navigation.replace('PhotoCollageFlow', { chapterId, phase: 'failed' });
    }
  }, [chapter, chapterId, navigation]);

  useEffect(() => {
    if (phase === 'preparing') void runPrepare();
  }, [phase, runPrepare]);

  const back = () => navigation.navigate('ChapterDetail', { chapterId });

  if (!chapter) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text>Memory unavailable.</Text>
      </SafeAreaView>
    );
  }

  if (phase === 'preparing') {
    return (
      <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
        <ShareFlowCancelHeader onCancel={back} />
        <View style={styles.center}>
          <Text style={styles.phaseTitle}>Collage</Text>
          <Text style={styles.phaseLead}>Preparing your collage…</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (phase === 'failed') {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.center}>
          <Text style={styles.phaseTitle}>Couldn&apos;t prepare this share.</Text>
          <Text style={styles.phaseLead}>Your memory is unchanged.</Text>
          <Pressable onPress={() => navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preparing' })}>
            <Text style={styles.primaryLink}>Try Again</Text>
          </Pressable>
          <Pressable onPress={back}>
            <Text style={styles.secondaryLink}>Back</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const previewUri = uri ?? collageUriCache.get(chapterId) ?? chapter.heroUri;

  const onShare = async () => {
    if (!previewUri) {
      Alert.alert('No image', 'This memory has no shareable image yet.');
      return;
    }
    try {
      await shareImageUri(previewUri);
    } catch (e) {
      Alert.alert('Share failed', e instanceof Error ? e.message : String(e));
    }
  };

  const onSave = async () => {
    if (!previewUri) return;
    try {
      await saveImageToPhotos(previewUri);
      Alert.alert('Saved', 'Collage saved to Photos.');
    } catch (e) {
      Alert.alert('Save failed', e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <ShareFlowCancelHeader onCancel={back} />
      <Text style={styles.previewEyebrow}>Photo collage</Text>
      <Text style={styles.previewTitle}>{chapter.title}</Text>
      <Text style={styles.previewMeta}>{formatChapterDateLong(chapter.dateKey)}</Text>
      <Text style={styles.previewBody}>{chapter.aiStory}</Text>
      {previewUri ? (
        <Image source={{ uri: previewUri }} style={styles.previewImage} resizeMode="cover" />
      ) : null}
      <View style={styles.actions}>
        <Pressable style={styles.btn} onPress={() => void onShare()}>
          <Text style={styles.btnLabel}>Share</Text>
        </Pressable>
        <Pressable style={styles.btnOutline} onPress={() => void onSave()}>
          <Text style={styles.btnOutlineLabel}>Save to Photos</Text>
        </Pressable>
        <Pressable onPress={() => navigation.replace('ShareMemorySelector', { chapterId })}>
          <Text style={styles.secondaryLink}>Try another</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  topAction: { minHeight: 44, justifyContent: 'center' },
  topActionLabel: { fontSize: font.body, color: colors.accent, fontWeight: '600' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: spacing.sm },
  phaseTitle: { fontSize: 22, fontWeight: '600', color: colors.ink, textAlign: 'center' },
  phaseLead: { fontSize: font.body, color: colors.secondary, textAlign: 'center' },
  primaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '700', marginTop: spacing.md },
  secondaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '600', marginTop: spacing.md, textAlign: 'center' },
  previewEyebrow: { fontSize: font.small, color: colors.tertiary, marginTop: spacing.md },
  previewTitle: { fontSize: 28, fontWeight: '600', color: colors.ink },
  previewMeta: { fontSize: font.small, color: colors.tertiary, marginBottom: spacing.sm },
  previewBody: { fontSize: font.body, color: colors.secondary, marginBottom: spacing.md },
  previewImage: { width: '100%', aspectRatio: 4 / 3, borderRadius: radius.control, marginBottom: spacing.lg },
  actions: { gap: spacing.sm, paddingBottom: spacing.xl },
  btn: {
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnLabel: { color: colors.paper, fontWeight: '700' },
  btnOutline: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnOutlineLabel: { color: colors.ink, fontWeight: '600' },
});
