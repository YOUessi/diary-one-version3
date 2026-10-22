import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { colors, radius, type } from '../theme';

/** Figma D1/Small Memory — orange punctation + fragment body; not tappable. */
export function SmallMemory({ text, posterUri }: { text: string; posterUri?: string }) {
  return (
    <View style={[styles.wrap, posterUri && styles.withMedia]} accessibilityRole="text">
      {posterUri ? <Image source={{ uri: posterUri }} style={styles.thumbnail} resizeMode="cover"
        accessible={false} /> : <View style={styles.dot} />}
      <Text style={styles.text}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  withMedia: { minHeight: 76, gap: 16 },
  thumbnail: { width: 92, height: 68, borderRadius: radius.media, backgroundColor: colors.surface },
  wrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    minHeight: 56,
    width: '100%',
  },
  /** Figma punctuation — 4×4, radius 2 */
  dot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.accent,
  },
  text: {
    ...type.bodyFragment,
    flex: 1,
    color: colors.secondary,
  },
});
