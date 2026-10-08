import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, spacing, type } from '../theme';

/** Figma D1/Small Memory — orange punctation + fragment body; not tappable. */
export function SmallMemory({ text }: { text: string }) {
  return (
    <View style={styles.wrap} accessibilityRole="text">
      <View style={styles.dot} />
      <Text style={styles.text}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    minHeight: 56,
    width: '100%',
  },
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
