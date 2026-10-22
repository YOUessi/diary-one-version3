import React from 'react';
import { Pressable, Text, StyleSheet } from 'react-native';
import { colors, spacing } from '../theme';

/** Figma Account list rows — label Medium 17; chevron secondary; ~h50–52. */
export function SettingsRow({
  label,
  value,
  onPress,
  destructive,
}: {
  label: string;
  value?: string;
  onPress: () => void;
  destructive?: boolean;
}) {
  return (
    <Pressable onPress={onPress} style={styles.row}>
      <Text style={[styles.rowLabel, destructive && styles.destructive]} numberOfLines={2}>
        {label}
      </Text>
      <Text style={styles.rowTrailing}>
        {value ? `${value} ` : ''}
        ›
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 52,
    paddingVertical: spacing.sm,
  },
  rowLabel: {
    fontSize: 17,
    lineHeight: 24,
    fontWeight: '500',
    color: colors.ink,
    flex: 1,
    paddingRight: spacing.sm,
  },
  /** Figma Delete Account — secondary gray, not accent */
  destructive: { color: colors.secondary },
  rowTrailing: { fontSize: 17, lineHeight: 24, fontWeight: '500', color: colors.secondary },
});
