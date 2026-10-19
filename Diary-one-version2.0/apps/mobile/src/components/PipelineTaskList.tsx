import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { colors, font, layout, radius, spacing } from '../theme';
import type { PipelineTask, PipelineTaskStatus } from '../pipeline/types';
import { retryStoredCloudResult } from '../pipeline/runPipeline';

const LABEL: Record<PipelineTaskStatus, string> = {
  queued: 'Queued',
  building_evidence: 'Building evidence',
  bundle_ready: 'Bundle ready',
  uploading: 'Uploading',
  cloud_processing: 'Cloud processing',
  succeeded: 'Succeeded',
  failed: 'Failed',
};

export function PipelineTaskList({ tasks }: { tasks: PipelineTask[] }) {
  if (!tasks.length) return null;
  return (
    <View style={styles.wrap}>
      {tasks.slice(0, 5).map((t) => (
        <View key={t.id} style={styles.row}>
          <Text style={styles.status}>{LABEL[t.status]}</Text>
          <Text style={styles.msg}>{t.message}</Text>
          <Text style={styles.meta}>
            {t.dayKey} · {t.sourceCount} file(s)
            {t.bundleVersion ? ` · ${t.bundleVersion}` : ''}
            {t.dayRevisionId ? `\n${t.dayRevisionId}` : ''}
          </Text>
          {t.error ? <Text style={styles.err}>{t.error}</Text> : null}
          {t.status === 'failed' && t.bundleDir && t.bundleJsonPath ? (
            <Pressable accessibilityRole="button" onPress={() => retryStoredCloudResult(t.id)}>
              <Text style={styles.msg}>Try again</Text>
            </Pressable>
          ) : null}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    gap: spacing.sm,
    marginBottom: spacing.md,
    marginHorizontal: layout.gutterDiary,
  },
  row: {
    backgroundColor: colors.card,
    borderRadius: radius.control,
    borderWidth: 1,
    borderColor: colors.divider,
    padding: spacing.md,
  },
  status: { fontSize: font.small, fontWeight: '700', color: colors.ink },
  msg: { fontSize: font.small, color: colors.secondary, marginTop: 2 },
  meta: { fontSize: font.micro, color: colors.tertiary, marginTop: 4 },
  err: { fontSize: font.micro, color: '#9B3B3B', marginTop: 4 },
});
