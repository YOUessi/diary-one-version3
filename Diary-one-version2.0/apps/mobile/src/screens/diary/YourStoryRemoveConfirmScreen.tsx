import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View, ActivityIndicator } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { DiaryStackParamList } from '../../navigation/types';
import { saveYourStory } from '../../backend/storyRepository';
import { isDevFailSimulationEnabled } from '../../config/devFailSimulation';

type Route = RouteProp<DiaryStackParamList, 'YourStoryRemoveConfirm'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'YourStoryRemoveConfirm'>;

/** Alternates failure on every other remove when Lab fail-sim is on. */
let storyRemoveFailNext = false;

/** Figma 307:2211 / 308:2296 — Note Confirmation card r12; actions 145×44 r12. */
export default function YourStoryRemoveConfirmScreen() {
  const { chapterId } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const expectedRevision = React.useRef(useAppStore.getState().chapters.find((c) => c.id === chapterId)?.yourStoryRevision ?? 0);
  const writing = React.useRef(false);
  const [removing, setRemoving] = useState(false);

  const confirm = async () => {
    if (writing.current) return;
    writing.current = true;
    setRemoving(true);
    try {
      if (isDevFailSimulationEnabled() && storyRemoveFailNext) {
        storyRemoveFailNext = false;
        throw new Error('Simulated remove failure');
      }
      await saveYourStory(chapterId, undefined, expectedRevision.current);
      if (isDevFailSimulationEnabled()) storyRemoveFailNext = true;
      navigation.goBack();
    } catch {
      navigation.replace('YourStoryRemoveFailed', { chapterId });
    } finally {
      writing.current = false;
      setRemoving(false);
    }
  };

  return (
    <Modal transparent animationType="fade" onRequestClose={() => { if (!writing.current) navigation.goBack(); }}>
      <View style={styles.backdrop}>
        <View style={styles.card}>
          {removing ? (
            <>
              <Text style={styles.title}>Removing note…</Text>
              <Text style={styles.body}>
                Please wait. Diary&apos;s summary and media will not be changed.
              </Text>
              <ActivityIndicator color={colors.ink} style={styles.spinner} />
              <Text style={styles.wait}>Please wait…</Text>
            </>
          ) : (
            <>
              <Text style={styles.title}>Remove your note?</Text>
              <Text style={styles.body}>
                Only your note will be removed. Diary&apos;s summary and media stay unchanged. Any
                unsaved edits will also be discarded.
              </Text>
              <View style={styles.actions}>
                <Pressable style={styles.secondaryBtn} onPress={() => navigation.goBack()}>
                  <Text style={styles.secondaryLabel}>Keep note</Text>
                </Pressable>
                <Pressable style={styles.primaryBtn} onPress={() => void confirm()}>
                  <Text style={styles.primaryLabel}>Remove note</Text>
                </Pressable>
              </View>
            </>
          )}
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
  spinner: { marginTop: spacing.sm },
  wait: { fontSize: 13, lineHeight: 18, color: colors.secondary },
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
