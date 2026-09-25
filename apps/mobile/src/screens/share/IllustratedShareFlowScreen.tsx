import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { buildIllustratedShare } from '../../share/buildPhotoCollage';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFlowCancelHeader } from '../../components/ShareFlowCancelHeader';

type Route = RouteProp<DiaryStackParamList, 'IllustratedShareFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'IllustratedShareFlow'>;

const STYLES: Array<'A' | 'B' | 'C'> = ['A', 'B', 'C'];
const illustratedUriCache = new Map<string, string>();

export default function IllustratedShareFlowScreen() {
  const { chapterId, phase, style = 'A' } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const [uri, setUri] = useState<string | null>(null);
  const [picked, setPicked] = useState<'A' | 'B' | 'C'>(style);

  const runPrepare = useCallback(async () => {
    if (!chapter) {
      navigation.replace('IllustratedShareFlow', { chapterId, phase: 'failed', style: picked });
      return;
    }
    try {
      const out = await buildIllustratedShare(chapter, picked);
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('IllustratedShareFlow', { chapterId, phase: 'failed', style: picked });
        return;
      }
      illustratedUriCache.set(`${chapterId}-${picked}`, out);
      setUri(out);
      navigation.replace('IllustratedShareFlow', { chapterId, phase: 'preview', style: picked });
    } catch {
      navigation.replace('IllustratedShareFlow', { chapterId, phase: 'failed', style: picked });
    }
  }, [chapter, chapterId, navigation, picked]);

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

  if (phase === 'picker') {
    return (
      <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
        <ShareFlowCancelHeader onCancel={back} />
        <Text style={styles.previewEyebrow}>Illustrated memory</Text>
        <Text style={styles.pickerLead}>
          This creates an AI-stylized copy for sharing.{'\n'}Your original memory won&apos;t change.
        </Text>
        <View style={styles.styleRow}>
          {STYLES.map((s) => (
            <Pressable
              key={s}
              onPress={() => setPicked(s)}
              style={[styles.styleChip, picked === s && styles.styleChipOn]}
            >
              <Text style={[styles.styleChipLabel, picked === s && styles.styleChipLabelOn]}>
                Style {s}
              </Text>
            </Pressable>
          ))}
        </View>
        <Pressable
          style={styles.btn}
          onPress={() =>
            navigation.replace('IllustratedShareFlow', { chapterId, phase: 'preparing', style: picked })
          }
        >
          <Text style={styles.btnLabel}>Create</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  if (phase === 'preparing') {
    return (
      <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
        <ShareFlowCancelHeader onCancel={back} />
        <View style={styles.center}>
          <Text style={styles.phaseTitle}>Illustrated</Text>
          <Text style={styles.phaseLead}>Creating your illustrated memory…</Text>
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
          <Pressable
            onPress={() =>
              navigation.replace('IllustratedShareFlow', { chapterId, phase: 'preparing', style: picked })
            }
          >
            <Text style={styles.primaryLink}>Try Again</Text>
          </Pressable>
          <Pressable onPress={back}>
            <Text style={styles.secondaryLink}>Back</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const previewUri = uri ?? illustratedUriCache.get(`${chapterId}-${picked}`) ?? chapter.heroUri;

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <ShareFlowCancelHeader onCancel={back} />
      <Text style={styles.previewEyebrow}>Illustrated memory</Text>
      <Text style={styles.previewTitle}>{chapter.title}</Text>
      <Text style={styles.previewMeta}>{formatChapterDateLong(chapter.dateKey)}</Text>
      <Text style={styles.previewBody}>{chapter.aiStory}</Text>
      {previewUri ? (
        <Image source={{ uri: previewUri }} style={styles.previewImage} resizeMode="cover" />
      ) : null}
      <View style={styles.actions}>
        <Pressable
          style={styles.btn}
          onPress={() => previewUri && void shareImageUri(previewUri).catch((e) => Alert.alert('Share failed', String(e)))}
        >
          <Text style={styles.btnLabel}>Share</Text>
        </Pressable>
        <Pressable
          style={styles.btnOutline}
          onPress={() =>
            previewUri &&
            void saveImageToPhotos(previewUri)
              .then(() => Alert.alert('Saved', 'Illustrated memory saved to Photos.'))
              .catch((e) => Alert.alert('Save failed', String(e)))
          }
        >
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
  pickerLead: { fontSize: font.body, color: colors.secondary, lineHeight: 22, marginBottom: spacing.lg },
  styleRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.lg },
  styleChip: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  styleChipOn: { borderColor: colors.ink, backgroundColor: colors.surface },
  styleChipLabel: { fontWeight: '600', color: colors.secondary },
  styleChipLabelOn: { color: colors.ink },
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
