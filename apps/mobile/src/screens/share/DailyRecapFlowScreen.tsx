import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Alert, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing } from '../../theme';
import { chaptersForDate, useAppStore } from '../../store/useAppStore';
import { buildDailyRecapAsset, type DailyRecapAsset } from '../../share/buildDailyRecap';
import { saveVideoToPhotos, shareVideoUri } from '../../share/shareActions';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { isDailyRecapBlockedForDate } from '../../domain/dailyRecapReadiness';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFlowCancelHeader } from '../../components/ShareFlowCancelHeader';
import { RecapVideoPreview } from '../../components/RecapVideoPreview';

type Route = RouteProp<DiaryStackParamList, 'DailyRecapFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DailyRecapFlow'>;

const recapCache = new Map<string, DailyRecapAsset>();

export default function DailyRecapFlowScreen() {
  const { dateKey, phase, errorHint } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));
  const [asset, setAsset] = useState<DailyRecapAsset | null>(recapCache.get(dateKey) ?? null);
  const [playing, setPlaying] = useState(true);
  const prepareForKey = useRef(dateKey);

  const dismissWithReadinessChanged = useCallback(() => {
    useAppStore.getState().setDailyRecapShareBlockedBanner(true);
    navigation.popToTop();
  }, [navigation]);

  const runPrepare = useCallback(async () => {
    prepareForKey.current = dateKey;
    try {
      await new Promise((r) => setTimeout(r, 400));
      const dayChanged = useAppStore.getState().selectedDateKey !== prepareForKey.current;
      const blocked = isDailyRecapBlockedForDate(dateKey, useAppStore.getState().todayStatus);
      if (dayChanged || blocked) {
        dismissWithReadinessChanged();
        return;
      }
      const out = await buildDailyRecapAsset(chapters);
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('DailyRecapFlow', { dateKey, phase: 'failed' });
        return;
      }
      recapCache.set(dateKey, out);
      setAsset(out);
      setPlaying(true);
      navigation.replace('DailyRecapFlow', { dateKey, phase: 'preview' });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      if (msg.includes('ffmpeg_not_installed') || msg.includes('bff_url_required')) {
        navigation.replace('DailyRecapFlow', { dateKey, phase: 'failed', errorHint: msg });
        return;
      }
      navigation.replace('DailyRecapFlow', { dateKey, phase: 'failed' });
    }
  }, [chapters, dateKey, dismissWithReadinessChanged, navigation]);

  useEffect(() => {
    if (phase === 'preparing') void runPrepare();
  }, [phase, runPrepare]);

  const back = () => navigation.goBack();

  if (phase === 'preparing') {
    return (
      <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
        <ShareFlowCancelHeader onCancel={back} />
        <View style={styles.center}>
          <Text style={styles.phaseTitle}>9:16 Video</Text>
          <Text style={styles.phaseLead}>Preparing your Daily Recap…</Text>
          <Text style={styles.phaseHint}>Building slides and encoding MP4 (device or Dev Lite ffmpeg).</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (phase === 'failed') {
    return (
      <SafeAreaView style={styles.safe}>
        <View style={styles.center}>
          <Text style={styles.phaseTitle}>Couldn&apos;t prepare this recap.</Text>
          <Text style={styles.phaseLead}>Your Diary is unchanged.</Text>
          {errorHint ? (
            <Text style={styles.errorHint}>
              {errorHint.includes('ffmpeg')
                ? 'Install ffmpeg on your PC and restart Dev Lite. See docs/DAILY_RECAP_VIDEO.md.'
                : errorHint.includes('bff_url')
                  ? 'Set Production BFF URL in Lab (same as cloud processing).'
                  : errorHint.slice(0, 280)}
            </Text>
          ) : null}
          <Pressable onPress={() => navigation.replace('DailyRecapFlow', { dateKey, phase: 'preparing' })}>
            <Text style={styles.primaryLink}>Try Again</Text>
          </Pressable>
          <Pressable onPress={back}>
            <Text style={styles.secondaryLink}>Back</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const preview = asset ?? recapCache.get(dateKey);

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <ShareFlowCancelHeader onCancel={back} />
      <Text style={styles.previewEyebrow}>Daily Recap</Text>
      <View style={styles.videoFrame}>
        {preview ? (
          <RecapVideoPreview
            videoUri={preview.videoUri}
            posterUri={preview.posterUri}
            playing={playing}
            onTogglePlay={() => setPlaying((p) => !p)}
          />
        ) : (
          <Text style={styles.missing}>No preview</Text>
        )}
      </View>
      <Text style={styles.caption}>
        {preview?.hasAudio ? 'With original audio when available' : 'Silent slideshow · tap to pause'}
      </Text>
      <View style={styles.actions}>
        <Pressable
          style={styles.btn}
          onPress={() => {
            if (!preview?.videoUri) {
              Alert.alert('Not ready', 'Recap video is not available yet.');
              return;
            }
            void shareVideoUri(preview.videoUri).catch((e) => Alert.alert('Share failed', String(e)));
          }}
        >
          <Text style={styles.btnLabel}>Share</Text>
        </Pressable>
        <Pressable
          style={styles.btnOutline}
          onPress={() => {
            if (!preview?.videoUri) {
              Alert.alert('Not available', 'Save requires a prepared recap video.');
              return;
            }
            void saveVideoToPhotos(preview.videoUri)
              .then(() => Alert.alert('Saved', 'Daily Recap video saved to Photos.'))
              .catch((e) => Alert.alert('Save failed', String(e)));
          }}
        >
          <Text style={styles.btnOutlineLabel}>Save to Photos</Text>
        </Pressable>
        <Pressable onPress={back}>
          <Text style={styles.secondaryLink}>Try another</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: layout.gutterDiary },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: spacing.sm, paddingHorizontal: spacing.md },
  phaseTitle: { fontSize: 22, fontWeight: '600', color: colors.ink, textAlign: 'center' },
  phaseLead: { fontSize: font.body, color: colors.secondary, textAlign: 'center', marginBottom: spacing.sm },
  phaseHint: { fontSize: font.micro, color: colors.tertiary, textAlign: 'center', marginBottom: spacing.lg },
  errorHint: { fontSize: font.small, color: colors.secondary, textAlign: 'center', marginBottom: spacing.md },
  primaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '700', marginTop: spacing.md },
  secondaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '600', marginTop: spacing.md, textAlign: 'center' },
  previewEyebrow: { fontSize: font.small, color: colors.tertiary, marginTop: spacing.md },
  videoFrame: {
    width: '100%',
    aspectRatio: 9 / 16,
    maxHeight: 420,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    marginVertical: spacing.md,
    overflow: 'hidden',
  },
  missing: { textAlign: 'center', marginTop: '40%', color: colors.tertiary },
  caption: { fontSize: font.small, color: colors.secondary, marginBottom: spacing.md },
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
