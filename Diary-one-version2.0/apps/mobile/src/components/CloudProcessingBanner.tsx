import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { colors, font, radius, spacing } from '../theme';
import type { PipelineTask } from '../pipeline/types';
import { useAppStore } from '../store/useAppStore';

/** Shown on Diary while S6–S7 pipeline runs (distinct from device Sync). */
export function CloudProcessingBanner({ task }: { task: PipelineTask }) {
  const target = useAppStore((s) => s.cloudProcessingTarget);
  const hint =
    target === 'production'
      ? 'Production BFF job — usually under a minute on Dev Lite. Keep the app open.'
      : 'Research preview can take 3–9 minutes. Keep the app open.';

  return (
    <View style={styles.banner} accessibilityLiveRegion="polite">
      <ActivityIndicator color={colors.accent} size="small" />
      <View style={styles.copy}>
        <Text style={styles.title}>Cloud processing</Text>
        <Text style={styles.sub}>{task.message}</Text>
        {task.status === 'cloud_processing' || task.status === 'uploading' ? (
          <Text style={styles.hint}>{hint}</Text>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  copy: { flex: 1 },
  title: { fontSize: font.small, fontWeight: '700', color: colors.ink },
  sub: { fontSize: font.small, color: colors.secondary, marginTop: 2 },
  hint: { fontSize: font.micro, color: colors.tertiary, marginTop: 4, lineHeight: 16 },
});
