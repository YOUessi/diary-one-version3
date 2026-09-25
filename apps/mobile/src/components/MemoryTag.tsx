import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, font, radius, spacing } from '../theme';

type Tone = 'primary' | 'neutral';

export function MemoryTag({ label, tone = 'primary' }: { label: string; tone?: Tone }) {
  const isPrimary = tone === 'primary';
  return (
    <View style={[styles.tag, isPrimary ? styles.primary : styles.neutral]}>
      <Text style={[styles.text, isPrimary ? styles.textPrimary : styles.textNeutral]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  tag: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: radius.pill,
    marginRight: 6,
    marginBottom: 4,
  },
  primary: { backgroundColor: colors.accentSoft },
  neutral: { backgroundColor: colors.surface },
  text: { fontSize: font.micro, fontWeight: '500' },
  textPrimary: { color: colors.accent },
  textNeutral: { color: colors.secondary },
});
