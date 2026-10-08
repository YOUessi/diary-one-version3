import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, layout, spacing, type } from '../theme';

type Props = {
  visible: boolean;
  onDismiss: () => void;
};

/** Figma 184:2282 — card r18, title 22, body 15, filled CTA 52×r12. */
export function ShareDayReadinessSheet({ visible, onDismiss }: Props) {
  return (
    <Modal transparent visible={visible} animationType="fade" onRequestClose={onDismiss}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <View style={styles.handle} />
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
  },
  card: {
    backgroundColor: colors.paper,
    borderTopLeftRadius: 18,
    borderTopRightRadius: 18,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.sm,
    paddingBottom: spacing.xxxl,
  },
  handle: {
    alignSelf: 'center',
    width: 36,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    letterSpacing: -0.1,
    color: colors.ink,
  },
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.secondary,
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  btn: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnLabel: { ...type.bodyStory, fontWeight: '600', color: colors.paper },
});
