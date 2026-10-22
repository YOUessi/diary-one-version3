import React from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { appStrings } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import { useImportFeedbackStore } from '../store/useImportFeedbackStore';
import { colors, spacing, radius } from '../theme';

/** An in-app panel survives the native Photos sheet's dismissal animation. */
export function ImportFeedbackPanel() {
  const feedback = useImportFeedbackStore((s) => s.feedback);
  const strings = appStrings(useAppStore((s) => s.language));
  const insets = useSafeAreaInsets();
  if (!feedback) return null;
  return (
    <View pointerEvents="box-none" style={[styles.container, { top: insets.top + spacing.sm }]}>
      <View style={styles.panel} accessibilityLiveRegion="polite" testID="import-feedback">
        <ScrollView style={styles.content}>
          <View style={styles.heading}>
            {feedback.kind === 'busy' ? <ActivityIndicator color={colors.accent} /> : null}
            <Text style={styles.title}>{feedback.title}</Text>
          </View>
          <Text style={styles.message}>{feedback.message}</Text>
        </ScrollView>
        <View style={styles.actions}>
          <Pressable accessibilityRole="button" onPress={feedback.dismiss} style={styles.button}>
            <Text style={styles.label}>{feedback.dismissLabel ?? (feedback.kind === 'busy' || feedback.kind === 'confirm' ? strings.cancel : strings.done)}</Text>
          </Pressable>
          {feedback.confirm ? (
            <Pressable accessibilityRole="button" onPress={feedback.confirm.run} style={styles.button}>
              <Text style={styles.label}>{feedback.confirm.label}</Text>
            </Pressable>
          ) : null}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { position: 'absolute', left: spacing.md, right: spacing.md, zIndex: 100 },
  panel: { backgroundColor: colors.surface, borderRadius: radius.control, padding: spacing.md,
    borderWidth: 1, borderColor: colors.divider, elevation: 8,
    shadowColor: '#000', shadowOffset: { width: 0, height: 3 }, shadowOpacity: 0.15, shadowRadius: 8 },
  content: { maxHeight: 240 },
  heading: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  title: { flex: 1, fontSize: 16, fontWeight: '700', color: colors.ink },
  message: { fontSize: 14, lineHeight: 21, color: colors.secondary, marginTop: spacing.sm },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', flexWrap: 'wrap', gap: spacing.sm },
  button: { minHeight: 44, justifyContent: 'center', paddingHorizontal: spacing.sm, marginTop: spacing.sm },
  label: { fontSize: 15, fontWeight: '600', color: colors.ink },
});
