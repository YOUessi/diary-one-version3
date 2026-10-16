import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, layout, spacing } from '../../theme';
import type { DiaryStackParamList } from '../../navigation/types';

type Route = RouteProp<DiaryStackParamList, 'YourStoryRemoveFailed'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'YourStoryRemoveFailed'>;

/** Figma 307:2299 — same Note Confirmation metrics as Confirm. */
export default function YourStoryRemoveFailedScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();

  const keepNote = () => {
    navigation.goBack();
  };

  const tryAgain = () => {
    navigation.replace('YourStoryRemoveConfirm', { chapterId });
  };

  return (
    <Modal transparent animationType="fade" onRequestClose={keepNote}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Couldn&apos;t remove note</Text>
          <Text style={styles.body}>Your saved note is unchanged. You can try again.</Text>
          <View style={styles.actions}>
            <Pressable style={styles.secondaryBtn} onPress={keepNote}>
              <Text style={styles.secondaryLabel}>Keep note</Text>
            </Pressable>
            <Pressable style={styles.primaryBtn} onPress={tryAgain}>
              <Text style={styles.primaryLabel}>Try Again</Text>
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
    justifyContent: 'flex-end',
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.xxxl,
  },
  card: {
    backgroundColor: colors.paper,
    borderRadius: 12,
    paddingHorizontal: spacing.md,
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
  actions: { flexDirection: 'row', gap: 10, marginTop: spacing.xs },
  secondaryBtn: {
    flex: 1,
    maxWidth: 145,
    minHeight: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.secondary },
  primaryBtn: {
    flex: 1,
    maxWidth: 145,
    minHeight: 44,
    borderRadius: 12,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 'auto',
  },
  primaryLabel: { fontSize: 15, lineHeight: 20, fontWeight: '600', color: colors.paper },
});
