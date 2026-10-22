import { appStrings, appLocale } from '../domain/strings';
import { pipelineTaskLabel, pipelineTaskDetail, requiresEvidenceRebuild } from '../domain/pipelineCopy';
import { useAppStore } from '../store/useAppStore';
import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { colors, font, layout, radius, spacing } from '../theme';
import type { PipelineTask } from '../pipeline/types';
import { retryStoredCloudResult } from '../pipeline/runPipeline';

export function PipelineTaskList({ tasks }: { tasks: PipelineTask[] }) {
  const language = useAppStore((s) => s.language);
  const strings = appStrings(language);
  if (!tasks.length) return null;
  return (
    <View style={styles.wrap}>
      {tasks.slice(0, 5).map((t) => (
        <View key={t.id} style={styles.row}>
          <Text style={styles.status}>{pipelineTaskLabel(t, language)}</Text>
          <Text style={styles.meta}>
            {t.dayKey} · {t.sourceCount} {appLocale(language) === 'zh-CN' ? '份素材' : 'files'}
          </Text>
          {pipelineTaskDetail(t, language) ? <Text style={styles.msg}>{pipelineTaskDetail(t, language)}</Text> : null}
          {t.error && !pipelineTaskDetail(t, language) ? <Text style={styles.err}>{t.error}</Text> : null}
          {t.status === 'failed' && t.bundleDir && t.bundleJsonPath && !requiresEvidenceRebuild(t.error) ? (
            <Pressable accessibilityRole="button" onPress={() => retryStoredCloudResult(t.id)}>
              <Text style={styles.msg}>{strings.retry}</Text>
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
