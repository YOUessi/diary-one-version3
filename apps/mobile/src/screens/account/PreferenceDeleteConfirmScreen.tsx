import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { colors, layout } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';

type Route = RouteProp<AccountStackParamList, 'PreferenceDeleteConfirm'>;

/** Figma 126:1209 — centered Confirm Card r16; Cancel text + Delete fill 145×44 r12. */
export default function PreferenceDeleteConfirmScreen() {
  const { preferenceId } = useRoute<Route>().params;
  const navigation = useNavigation();
  const removePreference = useAppStore((s) => s.removePreference);

  const confirm = () => {
    removePreference(preferenceId);
    navigation.goBack();
  };

  return (
    <Modal transparent animationType="fade" onRequestClose={() => navigation.goBack()}>
      <Pressable style={styles.backdrop} onPress={() => navigation.goBack()}>
        <Pressable style={styles.card} onPress={(e) => e.stopPropagation()}>
          <Text style={styles.title}>Delete this preference?</Text>
          <Text style={styles.body}>
            Diary One will stop using this preference as an importance signal. Your existing
            memories are not deleted.
          </Text>
          <View style={styles.actions}>
            <Pressable style={styles.cancelHit} onPress={() => navigation.goBack()}>
              <Text style={styles.cancel}>Cancel</Text>
            </Pressable>
            <Pressable style={styles.deleteBtn} onPress={confirm}>
              <Text style={styles.deleteLabel}>Delete</Text>
            </Pressable>
          </View>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.35)',
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
    maxWidth: 145,
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
    maxWidth: 145,
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
