import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Alert, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, radius, spacing } from '../../theme';
import { chaptersForDate, useAppStore } from '../../store/useAppStore';
import { buildDailyRecapAsset, type DailyRecapAsset } from '../../share/buildDailyRecap';
import { saveVideoToPhotos, shareVideoUri } from '../../share/shareActions';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { isDailyRecapBlockedForDate } from '../../domain/dailyRecapReadiness';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFailedView, SharePreparingView } from '../../components/SharePhaseViews';
import { SharePreviewShell } from '../../components/SharePreviewShell';
import { RecapVideoPreview } from '../../components/RecapVideoPreview';
import { formatChapterDateLong } from '../../domain/formatChapterDate';
import { formatShortDay } from '../../domain/formatMedia';

type Route = RouteProp<DiaryStackParamList, 'DailyRecapFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DailyRecapFlow'>;

const recapCache = new Map<string, DailyRecapAsset>();

export default function DailyRecapFlowScreen() {
  const { dateKey, phase, errorHint } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));
  const [asset, setAsset] = useState<DailyRecapAsset | null>(recapCache.get(dateKey) ?? null);
  /** Figma Preview shows ▶ idle; tap to play. */
  const [playing, setPlaying] = useState(false);
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
      <SafeAreaView style={styles.safePhase} edges={['top', 'bottom']}>
        <SharePreparingView
          cardLabel="9:16 Video"
          status="Preparing your Daily Recap…"
          onCancel={back}
        />
      </SafeAreaView>
    );
  }

  if (phase === 'failed') {
    return (
      <SafeAreaView style={styles.safePhase} edges={['top', 'bottom']}>
        <ShareFailedView
          title="Couldn't prepare this recap."
          subtitle="Your Diary is unchanged."
          onRetry={() => navigation.replace('DailyRecapFlow', { dateKey, phase: 'preparing' })}
          onBack={back}
        >
          {errorHint ? (
            <Text style={styles.errorHint}>
              {errorHint.includes('ffmpeg')
                ? 'Install ffmpeg on your PC and restart Dev Lite. See docs/DAILY_RECAP_VIDEO.md.'
                : errorHint.includes('bff_url')
                  ? 'Set Production BFF URL in Lab (same as cloud processing).'
                  : errorHint.slice(0, 280)}
            </Text>
          ) : null}
        </ShareFailedView>
      </SafeAreaView>
    );
  }

  const preview = asset ?? recapCache.get(dateKey);

  return (
    <SharePreviewShell
      heading="Daily Recap"
      title={formatShortDay(dateKey)}
      dateLabel={formatChapterDateLong(dateKey)}
      media={
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
      }
      captionBelowCard={
        preview?.hasAudio ? 'Original audio off · tap to play' : 'Silent slideshow · tap to play'
      }
      onBack={back}
      onShare={() => {
        if (!preview?.videoUri) {
          Alert.alert('Not ready', 'Recap video is not available yet.');
          return;
        }
        void shareVideoUri(preview.videoUri).catch((e) => Alert.alert('Share failed', String(e)));
      }}
      onSave={() => {
        if (!preview?.videoUri) {
          Alert.alert('Not available', 'Save requires a prepared recap video.');
          return;
        }
        void saveVideoToPhotos(preview.videoUri)
          .then(() => Alert.alert('Saved', 'Daily Recap video saved to Photos.'))
          .catch((e) => Alert.alert('Save failed', String(e)));
      }}
      onTryAnother={back}
    />
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  safePhase: { flex: 1, backgroundColor: colors.paper },
  errorHint: { fontSize: font.small, color: colors.secondary, textAlign: 'center', marginTop: spacing.md },
  videoFrame: {
    width: '100%',
    aspectRatio: 9 / 16,
    maxHeight: 420,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    overflow: 'hidden',
  },
  missing: { textAlign: 'center', marginTop: '40%', color: colors.tertiary },
});
