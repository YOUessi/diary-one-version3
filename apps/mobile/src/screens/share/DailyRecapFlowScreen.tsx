import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Alert, Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, font, layout, radius, spacing } from '../../theme';
import { chaptersForDate, useAppStore } from '../../store/useAppStore';
import { buildDailyRecapAsset } from '../../share/buildDailyRecap';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { isDailyRecapBlockedForDate } from '../../domain/dailyRecapReadiness';
import type { DiaryStackParamList } from '../../navigation/types';
import { MomentPlayer } from '../../components/MomentPlayer';
import { ShareFlowCancelHeader } from '../../components/ShareFlowCancelHeader';

type Route = RouteProp<DiaryStackParamList, 'DailyRecapFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DailyRecapFlow'>;

const recapCache = new Map<string, string>();

export default function DailyRecapFlowScreen() {
  const { dateKey, phase } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));
  const [uri, setUri] = useState<string | null>(recapCache.get(dateKey) ?? null);
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
      setUri(out);
      navigation.replace('DailyRecapFlow', { dateKey, phase: 'preview' });
    } catch {
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

  const previewUri = uri ?? recapCache.get(dateKey);
  const videoSample = chapters[0]?.moments.find((m) => m.playbackUri)?.playbackUri;

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <ShareFlowCancelHeader onCancel={back} />
      <Text style={styles.previewEyebrow}>Daily Recap</Text>
      <View style={styles.videoStub}>
        {playing && videoSample ? (
          <MomentPlayer uri={videoSample} playing onStop={() => setPlaying(false)} />
        ) : previewUri ? (
          <Pressable style={styles.playArea} onPress={() => videoSample && setPlaying(true)}>
            <Image source={{ uri: previewUri }} style={styles.recapImage} resizeMode="cover" />
            {videoSample ? <Text style={styles.playOverlay}>▶</Text> : null}
          </Pressable>
        ) : (
          <Pressable onPress={() => videoSample && setPlaying(true)}>
            <Text style={styles.play}>▶</Text>
          </Pressable>
        )}
      </View>
      <Text style={styles.caption}>Original audio</Text>
      <View style={styles.actions}>
        <Pressable
          style={styles.btn}
          onPress={() => {
            const shareUri = previewUri ?? videoSample;
            if (!shareUri) {
              Alert.alert('Not ready', 'Recap media is not available yet.');
              return;
            }
            void shareImageUri(shareUri).catch((e) => Alert.alert('Share failed', String(e)));
          }}
        >
          <Text style={styles.btnLabel}>Share</Text>
        </Pressable>
        <Pressable
          style={styles.btnOutline}
          onPress={() => {
            if (!previewUri) {
              Alert.alert('Not available', 'Save requires a prepared recap image.');
              return;
            }
            void saveImageToPhotos(previewUri)
              .then(() => Alert.alert('Saved', 'Daily Recap saved to Photos.'))
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
  topAction: { minHeight: 44, justifyContent: 'center' },
  topActionLabel: { fontSize: font.body, color: colors.accent, fontWeight: '600' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: spacing.sm },
  phaseTitle: { fontSize: 22, fontWeight: '600', color: colors.ink, textAlign: 'center' },
  phaseLead: { fontSize: font.body, color: colors.secondary, textAlign: 'center', marginBottom: spacing.lg },
  primaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '700', marginTop: spacing.md },
  secondaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '600', marginTop: spacing.md, textAlign: 'center' },
  previewEyebrow: { fontSize: font.small, color: colors.tertiary, marginTop: spacing.md },
  videoStub: {
    width: '100%',
    aspectRatio: 9 / 16,
    maxHeight: 420,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: spacing.md,
    overflow: 'hidden',
  },
  playArea: { width: '100%', height: '100%' },
  recapImage: { width: '100%', height: '100%' },
  playOverlay: {
    position: 'absolute',
    alignSelf: 'center',
    top: '45%',
    fontSize: 32,
    color: colors.paper,
  },
  play: { fontSize: 32, color: colors.ink },
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
