import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, font, spacing } from '../theme';

/** Figma D1/Small Memory — not clickable, no chevron, no tags. */
export function SmallMemory({ text }: { text: string }) {
  return (
    <View style={styles.wrap} accessibilityRole="text">
      <Text style={styles.text}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    paddingVertical: spacing.sm,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.divider,
  },
  text: { fontSize: font.body, lineHeight: 22, color: colors.ink },
});
