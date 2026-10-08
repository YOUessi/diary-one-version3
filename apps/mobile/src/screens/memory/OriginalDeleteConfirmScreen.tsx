import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, layout } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';

type Route = RouteProp<MemoryStackParamList, 'OriginalDeleteConfirm'>;
type Nav = NativeStackNavigationProp<MemoryStackParamList, 'OriginalDeleteConfirm'>;

/** Figma 125:1156 — centered Confirm Card r16; Cancel text + Delete Original fill 154×44 r12. */
export default function OriginalDeleteConfirmScreen() {
  const { captureId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const removeCapturedOriginal = useAppStore((s) => s.removeCapturedOriginal);

  const confirm = () => {
    removeCapturedOriginal(captureId);
    navigation.pop(2);
  };

  return (
    <Modal transparent animationType="fade" onRequestClose={() => navigation.goBack()}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Delete Original?</Text>
          <Text style={styles.body}>
            This removes this original photo/video from Captured by You. Memories created from it
            won&apos;t be affected.
          </Text>
          <View style={styles.actions}>
            <Pressable style={styles.cancelHit} onPress={() => navigation.goBack()}>
              <Text style={styles.cancel}>Cancel</Text>
            </Pressable>
            <Pressable style={styles.deleteBtn} onPress={confirm}>
              <Text style={styles.deleteLabel}>Delete Original</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.45)',
    justifyContent: 'center',
    paddingHorizontal: layout.gutterDiary,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    paddingHorizontal: 18,
    paddingVertical: 20,
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
  cancelHit: {
    flex: 1,
    maxWidth: 144,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancel: {
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '600',
    color: colors.ink,
  },
  deleteBtn: {
    flex: 1,
    maxWidth: 154,
    minHeight: 44,
    borderRadius: 12,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 'auto',
  },
  deleteLabel: {
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '600',
    color: '#ffffff',
  },
});
