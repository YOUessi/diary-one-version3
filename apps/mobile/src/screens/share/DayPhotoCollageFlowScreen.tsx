import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { formatShortDay } from '../../domain/formatMedia';
import { colors, font, layout, radius, spacing } from '../../theme';
import { chaptersForDate, useAppStore } from '../../store/useAppStore';
import { buildDayPhotoCollage } from '../../share/buildDayCollage';
import { shouldSimulateSharePrepareFailure } from '../../share/sharePrepareFail';
import { saveImageToPhotos, shareImageUri } from '../../share/shareActions';
import type { DiaryStackParamList } from '../../navigation/types';
import { ShareFlowCancelHeader } from '../../components/ShareFlowCancelHeader';

type Route = RouteProp<DiaryStackParamList, 'DayPhotoCollageFlow'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'DayPhotoCollageFlow'>;

const dayCollageCache = new Map<string, string>();

export default function DayPhotoCollageFlowScreen() {
  const { dateKey, phase } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));
  const [uri, setUri] = useState<string | null>(dayCollageCache.get(dateKey) ?? null);

  const runPrepare = useCallback(async () => {
    try {
      const out = await buildDayPhotoCollage(chapters);
      if (!out || shouldSimulateSharePrepareFailure()) {
        navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'failed' });
        return;
      }
      dayCollageCache.set(dateKey, out);
      setUri(out);
      navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'preview' });
    } catch {
      navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'failed' });
    }
  }, [chapters, dateKey, navigation]);

  useEffect(() => {
    if (phase === 'preparing') void runPrepare();
  }, [phase, runPrepare]);

  const back = () => navigation.goBack();

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
          <Text style={styles.phaseLead}>Your Diary is unchanged.</Text>
          <Pressable onPress={() => navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'preparing' })}>
            <Text style={styles.primaryLink}>Try Again</Text>
          </Pressable>
          <Pressable onPress={back}>
            <Text style={styles.secondaryLink}>Back</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const previewUri = uri ?? dayCollageCache.get(dateKey);

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <ShareFlowCancelHeader onCancel={back} />
      <Text style={styles.previewEyebrow}>Photo collage</Text>
      <Text style={styles.previewTitle}>{formatShortDay(dateKey)}</Text>
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
              .then(() => Alert.alert('Saved', 'Collage saved to Photos.'))
              .catch((e) => Alert.alert('Save failed', String(e)))
          }
        >
          <Text style={styles.btnOutlineLabel}>Save to Photos</Text>
        </Pressable>
        <Pressable onPress={() => navigation.replace('ShareDaySelector', { dateKey })}>
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
  phaseTitle: { fontSize: 22, fontWeight: '600', color: colors.ink },
  phaseLead: { fontSize: font.body, color: colors.secondary, textAlign: 'center' },
  primaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '700', marginTop: spacing.md },
  secondaryLink: { fontSize: font.body, color: colors.accent, fontWeight: '600', marginTop: spacing.md, textAlign: 'center' },
  previewEyebrow: { fontSize: font.small, color: colors.tertiary, marginTop: spacing.md },
  previewTitle: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.md },
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
