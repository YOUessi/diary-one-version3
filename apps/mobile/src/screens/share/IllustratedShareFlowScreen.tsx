import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import { buildIllustratedShare } from '../../share/buildPhotoCollage';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFailedView, SharePreparingView } from '../../components/SharePhaseViews';
import { SharePreviewShell } from '../../components/SharePreviewShell';

type Route = RouteProp<DiaryStackParamList, 'IllustratedShareFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'IllustratedShareFlow'>;

const STYLES: Array<'A' | 'B' | 'C'> = ['A', 'B', 'C'];
const illustratedUriCache = new Map<string, string>();

export default function IllustratedShareFlowScreen() {
  const { chapterId, phase, style = 'A' } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const [uri, setUri] = useState<string | null>(null);
  /** Figma page_05 — Style Picker starts with none selected; Create disabled until pick. */
  const [picked, setPicked] = useState<'A' | 'B' | 'C' | null>(phase === 'picker' ? null : style);
  const activeStyle: 'A' | 'B' | 'C' = picked ?? style;

  const runPrepare = useCallback(async () => {
    if (!chapter) {
      navigation.replace('IllustratedShareFlow', { chapterId, phase: 'failed', style: activeStyle });
      return;
    }
    try {
      const out = await buildIllustratedShare(chapter, activeStyle);
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('IllustratedShareFlow', {
          chapterId,
          phase: 'failed',
          style: activeStyle,
        });
        return;
      }
      illustratedUriCache.set(`${chapterId}-${activeStyle}`, out);
      setUri(out);
      navigation.replace('IllustratedShareFlow', {
        chapterId,
        phase: 'preview',
        style: activeStyle,
      });
    } catch {
      navigation.replace('IllustratedShareFlow', {
        chapterId,
        phase: 'failed',
        style: activeStyle,
      });
    }
  }, [activeStyle, chapter, chapterId, navigation]);

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
    const canCreate = picked != null;
    return (
      <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
        <View style={styles.pickerNav}>
          <Pressable onPress={back} style={styles.backHit} hitSlop={12} accessibilityLabel="Back">
            <Text style={styles.backText}>‹</Text>
          </Pressable>
          <Text style={styles.pickerNavTitle}>Illustrated memory</Text>
          <View style={styles.navSpacer} />
        </View>
        <Text style={styles.pickerLead}>
          This creates an AI-stylized copy for sharing.{'\n'}Your original memory won&apos;t change.
        </Text>
        <View style={styles.styleRow}>
          {STYLES.map((s) => {
            const on = picked === s;
            return (
              <Pressable
                key={s}
                onPress={() => setPicked(s)}
                style={[styles.styleCard, on && styles.styleCardOn]}
              >
                <View style={[styles.stylePreview, on ? styles.stylePreviewOn : styles.stylePreviewOff]}>
                  <View style={styles.stylePreviewInset} />
                  {!on ? <View style={styles.stylePreviewOrb} /> : null}
                </View>
                <Text style={styles.styleChipLabel}>Style {s}</Text>
              </Pressable>
            );
          })}
        </View>
        <View style={styles.pickerFooter}>
          <Pressable
            style={[styles.btn, !canCreate && styles.btnDisabled]}
            disabled={!canCreate}
            onPress={() =>
              navigation.replace('IllustratedShareFlow', {
                chapterId,
                phase: 'preparing',
                style: picked!,
              })
            }
          >
            <Text style={[styles.btnLabel, !canCreate && styles.btnLabelDisabled]}>Create</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  if (phase === 'preparing') {
    return (
      <SafeAreaView style={styles.safePhase} edges={['top', 'bottom']}>
        <SharePreparingView
          cardLabel="Illustrated"
          status="Creating your illustrated memory…"
          onCancel={back}
        />
      </SafeAreaView>
    );
  }

  if (phase === 'failed') {
    return (
      <SafeAreaView style={styles.safePhase} edges={['top', 'bottom']}>
        <ShareFailedView
          title="Couldn't prepare this share."
          subtitle="Your memory is unchanged."
          onRetry={() =>
            navigation.replace('IllustratedShareFlow', {
              chapterId,
              phase: 'preparing',
              style: activeStyle,
            })
          }
          onBack={() =>
            navigation.replace('IllustratedShareFlow', { chapterId, phase: 'picker', style: activeStyle })
          }
        />
      </SafeAreaView>
    );
  }

  const previewUri =
    uri ?? illustratedUriCache.get(`${chapterId}-${activeStyle}`) ?? chapter.heroUri;

  return (
    <SharePreviewShell
      heading="Illustrated memory"
      title={chapter.title}
      dateLabel={formatChapterDateLong(chapter.dateKey)}
      body={chapter.aiStory}
      imageUri={previewUri}
      onBack={back}
      onShare={() =>
        previewUri && void shareImageUri(previewUri).catch((e) => Alert.alert('Share failed', String(e)))
      }
      onSave={() =>
        previewUri &&
        void saveImageToPhotos(previewUri)
          .then(() => Alert.alert('Saved', 'Illustrated memory saved to Photos.'))
          .catch((e) => Alert.alert('Save failed', String(e)))
      }
      onTryAnother={() => navigation.replace('ShareMemorySelector', { chapterId })}
    />
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  safePhase: { flex: 1, backgroundColor: colors.paper },
  pickerNav: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: -layout.gutterDiary + spacing.sm,
    minHeight: 44,
    marginBottom: spacing.md,
  },
  backHit: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300', marginTop: -2 },
  pickerNavTitle: {
    flex: 1,
    textAlign: 'center',
    fontSize: 28,
    lineHeight: 34,
    fontWeight: '600',
    letterSpacing: -0.2,
    color: colors.ink,
  },
  navSpacer: { width: 44 },
  /** Figma 184:2115 — lead 14/400 */
  pickerLead: { fontSize: 14, color: colors.secondary, lineHeight: 20, marginBottom: spacing.xl },
  styleRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.lg },
  styleCard: {
    flex: 1,
    borderRadius: 12,
    backgroundColor: colors.card,
    padding: spacing.sm,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  styleCardOn: { borderColor: colors.accent },
  stylePreview: {
    aspectRatio: 88 / 112,
    borderRadius: 10,
    marginBottom: spacing.sm,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingBottom: 16,
  },
  stylePreviewOn: { backgroundColor: colors.accentSoft },
  stylePreviewOff: { backgroundColor: colors.surface },
  stylePreviewInset: {
    width: '42%',
    height: '28%',
    borderRadius: 6,
    backgroundColor: colors.card,
  },
  stylePreviewOrb: {
    position: 'absolute',
    top: 10,
    right: 10,
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: '#C8C4BC',
  },
  styleChipLabel: { fontWeight: '500', color: colors.ink, textAlign: 'center', fontSize: 13 },
  pickerFooter: { marginTop: 'auto' as unknown as number, paddingBottom: spacing.lg },
  btn: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnDisabled: { backgroundColor: colors.surface },
  btnLabel: { color: colors.paper, fontWeight: '600', fontSize: 17 },
  btnLabelDisabled: { color: colors.tertiary },
});
