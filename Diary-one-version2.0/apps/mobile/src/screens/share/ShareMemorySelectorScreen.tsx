import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, spacing, type } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';

type Route = RouteProp<DiaryStackParamList, 'ShareMemorySelector'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ShareMemorySelector'>;

/** Figma 184:1976 — sheet r24 white, options r14 paper+border, 94×100 thumb, scrim 18%. */
export default function ShareMemorySelectorScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const chapter = useAppStore((s) => s.chapters.find((c) => c.id === chapterId));
  const thumb = chapter?.heroUri ?? chapter?.moments[0]?.posterUri;

  const close = () => navigation.goBack();

  return (
    <View style={styles.root}>
      <Pressable style={styles.dim} onPress={close} accessibilityLabel="Dismiss share options" />
      <SafeAreaView edges={['bottom']} style={styles.sheet}>
        <View style={styles.handle} />
        <View style={styles.titleBlock}>
          <Text style={styles.sheetTitle}>Share memory</Text>
          <Pressable onPress={close} hitSlop={12} accessibilityLabel="Close" style={styles.closeHit}>
            <Text style={styles.close}>×</Text>
          </Pressable>
        </View>

        <Pressable
          style={styles.option}
          onPress={() => navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preparing' })}
        >
          <CollageThumb uri={thumb} />
          <View style={styles.optionCopy}>
            <Text style={styles.optionTitle}>Photo collage</Text>
            <Text style={styles.optionBody}>A clean layout using moments from this memory.</Text>
          </View>
        </Pressable>
        <Pressable
          style={styles.option}
          onPress={() => navigation.replace('IllustratedShareFlow', { chapterId, phase: 'picker' })}
        >
          <IllustratedThumb uri={thumb} />
          <View style={styles.optionCopy}>
            <Text style={styles.optionTitle}>Illustrated memory</Text>
            <Text style={styles.optionBody}>A stylized version created from this memory.</Text>
          </View>
        </Pressable>
      </SafeAreaView>
    </View>
  );
}

function CollageThumb({ uri }: { uri?: string }) {
  if (uri) {
    return (
      <View style={styles.thumb}>
        <Image source={{ uri }} style={styles.thumbImage} resizeMode="cover" />
      </View>
    );
  }
  return (
    <View style={[styles.thumb, styles.collageThumb]}>
      <View style={styles.collageA} />
      <View style={styles.collageB} />
      <View style={styles.collageC} />
    </View>
  );
}

function IllustratedThumb({ uri }: { uri?: string }) {
  return (
    <View style={[styles.thumb, styles.thumbTinted]}>
      {uri ? (
        <Image source={{ uri }} style={[styles.thumbImage, { opacity: 0.85 }]} resizeMode="cover" />
      ) : (
        <>
          <View style={styles.illSun} />
          <View style={styles.illHill} />
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'transparent' },
  /** Figma Share Scrim opacity 0.18 */
  dim: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.18)' },
  sheet: {
    backgroundColor: colors.card,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: 10,
    paddingBottom: spacing.lg,
    minHeight: 428,
  },
  handle: {
    alignSelf: 'center',
    width: 41,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
    marginBottom: 20,
  },
  titleBlock: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.lg,
    minHeight: 44,
  },
  sheetTitle: {
    ...type.titleSection,
    color: colors.ink,
    flex: 1,
    paddingRight: spacing.md,
  },
  closeHit: {
    position: 'absolute',
    right: -4,
    top: -18,
    width: layout.minTouch,
    height: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  close: { fontSize: 26, color: '#404040', fontWeight: '400', lineHeight: 32 },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: 14,
    backgroundColor: colors.paper,
    padding: 13,
    marginBottom: 14,
    height: 128,
    gap: 16,
  },
  thumb: {
    width: 94,
    height: 100,
    borderRadius: 10,
    backgroundColor: '#EEEAE4',
    overflow: 'hidden',
  },
  collageThumb: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
    padding: 6,
  },
  collageA: {
    width: 39,
    height: 39,
    borderRadius: 6,
    backgroundColor: colors.accentSoft,
  },
  collageB: {
    width: 39,
    height: 39,
    borderRadius: 6,
    backgroundColor: '#E7E1D8',
  },
  collageC: {
    width: 82,
    height: 43,
    borderRadius: 6,
    backgroundColor: colors.card,
  },
  thumbTinted: { backgroundColor: colors.surface },
  thumbImage: { width: '100%', height: '100%' },
  illSun: {
    position: 'absolute',
    top: 14,
    right: 14,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.accentSoft,
  },
  illHill: {
    position: 'absolute',
    left: -20,
    bottom: -30,
    width: 140,
    height: 80,
    borderRadius: 70,
    backgroundColor: '#E7E1D8',
  },
  optionCopy: { flex: 1, paddingRight: spacing.sm, justifyContent: 'center' },
  optionTitle: { fontSize: 17, lineHeight: 24, fontWeight: '600', color: colors.ink, marginBottom: 8 },
  optionBody: { fontSize: 13, lineHeight: 18, color: colors.secondary },
});
