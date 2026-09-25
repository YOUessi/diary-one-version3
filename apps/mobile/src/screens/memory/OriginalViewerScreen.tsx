import React from 'react';
import { Text, Pressable, StyleSheet, View, Image, Alert } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Sharing from 'expo-sharing';
import * as MediaLibrary from 'expo-media-library/legacy';
import { colors, font, layout, spacing, radius } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';
import { OriginalVideoPlayer } from '../../components/OriginalVideoPlayer';

type Route = RouteProp<MemoryStackParamList, 'OriginalViewer'>;
type Nav = NativeStackNavigationProp<MemoryStackParamList, 'OriginalViewer'>;

export default function OriginalViewerScreen() {
  const { captureId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const item = useAppStore((s) => s.capturedOriginals.find((c) => c.id === captureId));

  const shareOriginal = async () => {
    if (!item) return;
    const message = [
      item.capturedAtLabel ?? 'Captured by You',
      item.kind === 'video' && item.durationSec != null ? `Video · ${item.durationSec}s` : 'Photo',
    ].join('\n');
    try {
      const fileUri = item.playbackUri ?? item.posterUri;
      if (fileUri && (await Sharing.isAvailableAsync())) {
        await Sharing.shareAsync(fileUri, { dialogTitle: 'Share original' });
        return;
      }
      await Sharing.shareAsync(message, { dialogTitle: 'Share original' });
    } catch (e) {
      Alert.alert('Share failed', e instanceof Error ? e.message : String(e));
    }
  };

  const saveToPhotos = async () => {
    const mediaUri = item?.playbackUri ?? item?.posterUri;
    if (!mediaUri) {
      Alert.alert(
        'Not available',
        'Full-resolution originals arrive after device sync. Only synced media can be saved to Photos.',
      );
      return;
    }
    const perm = await MediaLibrary.requestPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Permission needed', 'Allow Photos access to save this original.');
      return;
    }
    try {
      await MediaLibrary.saveToLibraryAsync(mediaUri);
      Alert.alert('Saved', 'Saved to your photo library.');
    } catch (e) {
      Alert.alert('Save failed', e instanceof Error ? e.message : String(e));
    }
  };

  const videoUri = item?.kind === 'video' ? item.playbackUri : undefined;
  const imageUri = item?.posterUri ?? (item?.kind === 'photo' ? item.playbackUri : undefined);

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <View style={styles.topBar}>
        <Pressable onPress={() => navigation.goBack()} style={styles.back}>
          <Text style={styles.backText}>‹</Text>
        </Pressable>
        <Pressable
          onPress={() => navigation.navigate('OriginalDeleteConfirm', { captureId })}
          hitSlop={8}
        >
          <Text style={styles.deleteLink}>⌫ Delete Original</Text>
        </Pressable>
      </View>

      {item?.capturedAtLabel ? <Text style={styles.viewerMeta}>{item.capturedAtLabel}</Text> : null}

      <View style={styles.viewer}>
        {videoUri ? (
          <OriginalVideoPlayer uri={videoUri} durationSec={item?.durationSec} />
        ) : imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.image} resizeMode="contain" />
        ) : (
          <>
            <Text style={styles.kind}>{item?.kind === 'video' ? 'Video original' : 'Photo original'}</Text>
            {item?.durationSec ? <Text style={styles.meta}>Duration {item.durationSec}s</Text> : null}
            <Text style={styles.hint}>Immersive playback after device sync provides media URIs.</Text>
          </>
        )}
      </View>

      <View style={styles.actions}>
        <Pressable style={styles.actionBtn} onPress={() => void saveToPhotos()}>
          <Text style={styles.actionText}>⇩ Save to Photos</Text>
        </Pressable>
        <Pressable style={styles.actionBtn} onPress={() => void shareOriginal()}>
          <Text style={styles.actionText}>↗ Share</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.ink },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingRight: layout.gutterDiary,
  },
  back: { padding: layout.gutterDiary, minHeight: layout.minTouch, justifyContent: 'center' },
  backText: { fontSize: 28, color: colors.paper, fontWeight: '300' },
  deleteLink: { fontSize: font.small, color: colors.paper, fontWeight: '600' },
  viewerMeta: {
    fontSize: font.small,
    color: colors.tertiary,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.sm,
  },
  viewer: {
    flex: 1,
    margin: layout.gutterDiary,
    borderRadius: radius.control,
    backgroundColor: '#2A2A2A',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.lg,
    overflow: 'hidden',
  },
  image: { width: '100%', height: '100%' },
  playWrap: { alignItems: 'center', gap: spacing.sm },
  play: { fontSize: 36, color: colors.paper },
  playHint: { color: colors.tertiary, fontSize: font.small },
  kind: { color: colors.paper, fontSize: font.h2, fontWeight: '600' },
  meta: { color: colors.tertiary, marginTop: spacing.sm },
  hint: { color: colors.tertiary, fontSize: font.small, textAlign: 'center', marginTop: spacing.lg },
  actions: { flexDirection: 'row', gap: spacing.sm, padding: layout.gutterDiary },
  actionBtn: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.secondary,
    borderRadius: radius.pill,
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionText: { color: colors.paper, fontWeight: '600' },
});
