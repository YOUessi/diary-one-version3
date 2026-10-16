import React from 'react';
import { View, Text, Pressable, StyleSheet, Image } from 'react-native';
import { colors } from '../theme';
import { formatDurationClock } from '../domain/formatMedia';
import type { CapturedOriginal } from '../model';

/**
 * Figma Captured by You cell (65:913): top-rounded tile + soft bottom scallop,
 * duration badge bottom-right.
 * Memory Home strip uses variant="preview" (82×72).
 */
export function CapturedGridCell({
  item,
  onPress,
  variant = 'grid',
}: {
  item: CapturedOriginal;
  onPress: () => void;
  /** preview = Memory Home strip 82×72; library = Captured page 111×110 */
  variant?: 'grid' | 'preview' | 'library';
}) {
  const duration =
    item.kind === 'video' && item.durationSec != null
      ? formatDurationClock(item.durationSec)
      : null;

  const cellStyle =
    variant === 'preview'
      ? styles.previewCell
      : variant === 'library'
        ? styles.libraryCell
        : styles.cell;

  const clipStyle = variant === 'library' ? styles.clipLibrary : styles.clip;

  return (
    <Pressable onPress={onPress} style={cellStyle} accessibilityRole="button">
      <View style={clipStyle}>
        {item.posterUri ? (
          <Image source={{ uri: item.posterUri }} style={styles.image} resizeMode="cover" />
        ) : (
          <View style={styles.placeholder}>
            <View style={styles.placeholderOrb} />
          </View>
        )}
        {variant !== 'library' ? (
          <View style={styles.scallop} pointerEvents="none" />
        ) : null}
      </View>
      {duration ? (
        <View style={[styles.durationBadge, variant === 'library' && styles.durationBadgeLibrary]}>
          <Text style={styles.durationText}>{duration}</Text>
        </View>
      ) : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  cell: {
    width: '31.5%',
    aspectRatio: 1,
    position: 'relative',
  },
  previewCell: {
    width: 82,
    height: 72,
    position: 'relative',
  },
  /** Figma 65:913 — 111×110 · r10 */
  libraryCell: {
    width: 111,
    height: 110,
    position: 'relative',
  },
  clip: {
    flex: 1,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
    borderBottomLeftRadius: 18,
    borderBottomRightRadius: 18,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  /** Figma Captured library cells — uniform r10, no scallop */
  clipLibrary: {
    flex: 1,
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  image: { width: '100%', height: '100%' },
  placeholder: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  placeholderOrb: {
    position: 'absolute',
    top: '18%',
    right: '18%',
    width: '42%',
    height: '42%',
    borderRadius: 999,
    backgroundColor: '#E2DED6',
  },
  scallop: {
    position: 'absolute',
    left: '12%',
    right: '12%',
    bottom: -10,
    height: 20,
    borderRadius: 999,
    backgroundColor: colors.paper,
  },
  durationBadge: {
    position: 'absolute',
    right: 6,
    bottom: 10,
    backgroundColor: 'rgba(0,0,0,0.62)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    minHeight: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  /** Figma 65:913 — badge ~42×22 r8 */
  durationBadgeLibrary: {
    right: 6,
    bottom: 6,
    minWidth: 42,
    borderRadius: 8,
  },
  durationText: { fontSize: 11, lineHeight: 14, color: colors.paper, letterSpacing: 0.1 },
});
