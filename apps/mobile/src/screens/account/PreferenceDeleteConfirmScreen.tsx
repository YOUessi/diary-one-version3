import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { colors, font, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';

type Route = RouteProp<AccountStackParamList, 'PreferenceDeleteConfirm'>;

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
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Delete this preference?</Text>
          <Text style={styles.sub}>
            Diary One will stop using this preference as an importance signal. Your existing memories are not deleted.
          </Text>
          <View style={styles.actions}>
            <Pressable onPress={() => navigation.goBack()}>
              <Text style={styles.cancel}>Cancel</Text>
            </Pressable>
            <Pressable onPress={confirm}>
              <Text style={styles.delete}>Delete</Text>
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
    backgroundColor: 'rgba(0,0,0,0.35)',
    justifyContent: 'center',
    padding: layout.gutterDiary,
  },
  card: {
    backgroundColor: colors.paper,
    borderRadius: 16,
    padding: spacing.lg,
  },
  title: { fontSize: font.body, fontWeight: '700', color: colors.ink, marginBottom: spacing.xs },
  sub: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.lg },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: spacing.lg },
  cancel: { fontSize: font.body, color: colors.secondary, fontWeight: '600' },
  delete: { fontSize: font.body, color: colors.accent, fontWeight: '700' },
});
