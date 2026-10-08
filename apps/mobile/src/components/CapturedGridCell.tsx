import React from 'react';
import { View, Text, Pressable, StyleSheet, Image } from 'react-native';
import { colors, type } from '../theme';
import { formatDurationClock } from '../domain/formatMedia';
import type { CapturedOriginal } from '../model';

/**
 * Figma Captured by You cell (65:913): top-rounded tile + soft bottom scallop,
 * duration badge bottom-right.
 */
export function CapturedGridCell({
  item,
  onPress,
}: {
  item: CapturedOriginal;
  onPress: () => void;
}) {
  const duration =
    item.kind === 'video' && item.durationSec != null
      ? formatDurationClock(item.durationSec)
      : null;

  return (
    <Pressable onPress={onPress} style={styles.cell} accessibilityRole="button">
      <View style={styles.clip}>
        {item.posterUri ? (
          <Image source={{ uri: item.posterUri }} style={styles.image} resizeMode="cover" />
        ) : (
          <View style={styles.placeholder}>
            <View style={styles.placeholderOrb} />
          </View>
        )}
        {/* Soft concave bottom scallop (Figma tile profile) */}
        <View style={styles.scallop} pointerEvents="none" />
      </View>
      {duration ? (
        <View style={styles.durationBadge}>
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
  clip: {
    flex: 1,
    borderTopLeftRadius: 14,
    borderTopRightRadius: 14,
    borderBottomLeftRadius: 22,
    borderBottomRightRadius: 22,
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
    backgroundColor: 'rgba(23,23,23,0.72)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  durationText: { ...type.metadata, color: colors.paper, fontWeight: '600' },
});
