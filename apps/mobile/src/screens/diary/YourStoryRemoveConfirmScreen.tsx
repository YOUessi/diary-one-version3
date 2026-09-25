import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, font, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';

type Route = RouteProp<DiaryStackParamList, 'YourStoryRemoveConfirm'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'YourStoryRemoveConfirm'>;

/** Alternates failure on every other remove attempt (APP045 test build). */
let storyRemoveFailNext = false;

export default function YourStoryRemoveConfirmScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const updateYourStory = useAppStore((s) => s.updateYourStory);
  const [removing, setRemoving] = useState(false);

  const confirm = () => {
    setRemoving(true);
    setTimeout(() => {
      if (storyRemoveFailNext) {
        storyRemoveFailNext = false;
        setRemoving(false);
        navigation.replace('YourStoryRemoveFailed', { chapterId });
        return;
      }
      storyRemoveFailNext = true;
      updateYourStory(chapterId, undefined);
      setRemoving(false);
      navigation.goBack();
    }, 500);
  };

  return (
    <Modal transparent animationType="fade" onRequestClose={() => navigation.goBack()}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          <Text style={styles.title}>Remove your note?</Text>
          <Text style={styles.body}>
            Only your note will be removed. Diary&apos;s summary and media stay unchanged. Any unsaved
            edits will also be discarded.
          </Text>
          {removing ? (
            <View style={styles.removingBlock}>
              <ActivityIndicator color={colors.accent} style={styles.spinner} />
              <Text style={styles.removingTitle}>Removing note…</Text>
              <Text style={styles.removingBody}>
                Please wait. Diary&apos;s summary and media will not be changed.
              </Text>
            </View>
          ) : (
            <View style={styles.actions}>
              <Pressable onPress={() => navigation.goBack()}>
                <Text style={styles.cancel}>Keep note</Text>
              </Pressable>
              <Pressable onPress={confirm}>
                <Text style={styles.remove}>Remove note</Text>
              </Pressable>
            </View>
          )}
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
  card: { backgroundColor: colors.paper, borderRadius: 16, padding: spacing.lg },
  title: { fontSize: font.body, fontWeight: '700', color: colors.ink, marginBottom: spacing.sm },
  body: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.lg },
  removingBlock: { alignItems: 'center', gap: spacing.sm, marginBottom: spacing.md },
  removingTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink },
  removingBody: { fontSize: font.small, color: colors.secondary, textAlign: 'center', lineHeight: 20 },
  spinner: { marginVertical: spacing.xs },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: spacing.lg },
  cancel: { fontSize: font.body, color: colors.secondary, fontWeight: '600' },
  remove: { fontSize: font.body, color: colors.accent, fontWeight: '700' },
});
