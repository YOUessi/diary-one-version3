import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, spacing, type } from '../theme';
import { useAppStore } from '../store/useAppStore';
import { memoryTagLabel } from '../domain/memoryTagLabel';

type Tone = 'primary' | 'neutral';

/** Figma D1/Tag — Primary on chapter cards; Neutral on detail “More about”. */
export function MemoryTag({ label, tone = 'primary' }: { label: string; tone?: Tone }) {
  const language = useAppStore((state) => state.language);
  const displayLabel = memoryTagLabel(label, language);
  if (!displayLabel) return null;
  const isPrimary = tone === 'primary';
  return (
    <View style={[styles.tag, isPrimary ? styles.primary : styles.neutral]}>
      <Text style={[styles.text, isPrimary ? styles.textPrimary : styles.textNeutral]}>{displayLabel}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  tag: {
    height: 26,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primary: { backgroundColor: colors.accentSoft },
  neutral: { backgroundColor: colors.surface },
  text: { ...type.captionEmphasis },
  textPrimary: { color: colors.ink },
  textNeutral: { color: colors.secondary },
});
