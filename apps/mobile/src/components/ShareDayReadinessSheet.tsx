import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, font, layout, radius, spacing } from '../theme';

type Props = {
  visible: boolean;
  onDismiss: () => void;
};

/** Figma 184:2282 · Daily Recap / Readiness Changed */
export function ShareDayReadinessSheet({ visible, onDismiss }: Props) {
  return (
    <Modal transparent visible={visible} animationType="fade" onRequestClose={onDismiss}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>New recordings are still being prepared.</Text>
          <Text style={styles.body}>Share this day when they&apos;re ready.</Text>
          <Pressable onPress={onDismiss} style={styles.btn}>
            <Text style={styles.btnLabel}>Back to Diary</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.35)',
    justifyContent: 'flex-end',
    padding: layout.gutterDiary,
    paddingBottom: spacing.xl,
  },
  card: {
    backgroundColor: colors.paper,
    borderRadius: radius.card,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  title: { fontSize: font.body, fontWeight: '700', color: colors.ink, lineHeight: 22 },
  body: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.sm },
  btn: { minHeight: layout.minTouch, alignItems: 'center', justifyContent: 'center' },
  btnLabel: { fontSize: font.body, fontWeight: '600', color: colors.accent },
});
