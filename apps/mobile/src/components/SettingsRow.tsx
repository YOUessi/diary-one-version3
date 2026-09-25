import React from 'react';
import { Pressable, Text, StyleSheet } from 'react-native';
import { colors, font, layout, spacing } from '../theme';

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
      <Text style={[styles.rowLabel, destructive && styles.destructive]}>{label}</Text>
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
    minHeight: layout.minTouch,
    paddingVertical: spacing.sm,
  },
  rowLabel: { fontSize: font.body, color: colors.ink, flex: 1, paddingRight: spacing.sm },
  destructive: { color: colors.accent },
  rowTrailing: { fontSize: font.body, color: colors.tertiary },
});
