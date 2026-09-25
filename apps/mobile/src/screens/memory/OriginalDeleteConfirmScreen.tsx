import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, font, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { MemoryStackParamList } from '../../navigation/types';

type Route = RouteProp<MemoryStackParamList, 'OriginalDeleteConfirm'>;
type Nav = NativeStackNavigationProp<MemoryStackParamList, 'OriginalDeleteConfirm'>;

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
            This removes this original photo/video from Captured by You. Memories created from it won&apos;t be affected.
          </Text>
          <View style={styles.actions}>
            <Pressable onPress={() => navigation.goBack()}>
              <Text style={styles.cancel}>Cancel</Text>
            </Pressable>
            <Pressable onPress={confirm}>
              <Text style={styles.delete}>Delete Original</Text>
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
    padding: layout.gutterDiary,
  },
  card: {
    backgroundColor: colors.paper,
    borderRadius: 16,
    padding: spacing.lg,
  },
  title: { fontSize: font.body, fontWeight: '700', color: colors.ink, marginBottom: spacing.sm },
  body: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.lg },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: spacing.lg },
  cancel: { fontSize: font.body, color: colors.secondary, fontWeight: '600' },
  delete: { fontSize: font.body, color: colors.accent, fontWeight: '700' },
});
