import React from 'react';
import { Text, StyleSheet, ActivityIndicator, View } from 'react-native';
import { colors, font, radius, spacing } from '../theme';

/** Figma 131:1689 — day switch while memories load for selected date. */
export function DayPrepareBanner({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <View style={styles.wrap} accessibilityLiveRegion="polite">
      <ActivityIndicator color={colors.accent} size="small" />
      <Text style={styles.label}>Preparing your memories...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  label: { fontSize: font.small, color: colors.secondary, fontWeight: '600' },
});
