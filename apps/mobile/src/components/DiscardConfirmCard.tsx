import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, layout } from '../theme';

type Props = {
  visible: boolean;
  title: string;
  message: string;
  keepLabel?: string;
  discardLabel?: string;
  /** `sheet` ≈ Profile 370:2640 bottom-biased; `inline` for overlay inside another sheet */
  placement?: 'sheet' | 'inline';
  onKeepEditing: () => void;
  onDiscard: () => void;
};

/**
 * Figma Discard Confirmation — card r12; Keep Editing text + Discard fill 145×44 r12.
 * Story 123:1374 / APP045 309:2542 / Profile 370:2640.
 */
export function DiscardConfirmCard({
  visible,
  title,
  message,
  keepLabel = 'Keep Editing',
  discardLabel = 'Discard',
  placement = 'sheet',
  onKeepEditing,
  onDiscard,
}: Props) {
  if (!visible) return null;

  const card = (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.body}>{message}</Text>
      <View style={styles.actions}>
        <Pressable style={styles.keepHit} onPress={onKeepEditing}>
          <Text style={styles.keepLabel}>{keepLabel}</Text>
        </Pressable>
        <Pressable style={styles.discardBtn} onPress={onDiscard}>
          <Text style={styles.discardLabel}>{discardLabel}</Text>
        </Pressable>
      </View>
    </View>
  );

  if (placement === 'inline') {
    return <View style={styles.inlineWrap}>{card}</View>;
  }

  return (
    <Modal transparent animationType="fade" visible={visible} onRequestClose={onKeepEditing}>
      <Pressable style={styles.backdrop} onPress={onKeepEditing}>
        <Pressable style={styles.sheetPad} onPress={(e) => e.stopPropagation()}>
          {card}
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.35)',
    justifyContent: 'flex-end',
  },
  sheetPad: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: 48,
  },
  inlineWrap: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.35)',
    justifyContent: 'flex-end',
    paddingHorizontal: 16,
    paddingBottom: 18,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    overflow: 'hidden',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 18,
    gap: 14,
  },
  title: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    color: colors.ink,
  },
  body: {
    fontSize: 17,
    lineHeight: 24,
    color: colors.secondary,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  keepHit: {
    flex: 1,
    maxWidth: 145,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  keepLabel: {
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '600',
    color: colors.ink,
  },
  discardBtn: {
    flex: 1,
    maxWidth: 145,
    minHeight: 44,
    borderRadius: 12,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 'auto',
  },
  discardLabel: {
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '600',
    color: '#ffffff',
  },
});
