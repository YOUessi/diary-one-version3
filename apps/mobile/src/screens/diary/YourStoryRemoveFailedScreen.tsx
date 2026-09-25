import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, font, layout, spacing } from '../../theme';
import type { DiaryStackParamList } from '../../navigation/types';

type Route = RouteProp<DiaryStackParamList, 'YourStoryRemoveFailed'>;
type Nav = NativeStackNavigationProp<DiaryStackParamList, 'YourStoryRemoveFailed'>;

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
            <Pressable onPress={keepNote}>
              <Text style={styles.keep}>Keep note</Text>
            </Pressable>
            <Pressable onPress={tryAgain}>
              <Text style={styles.tryAgain}>Try Again</Text>
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
  card: { backgroundColor: colors.paper, borderRadius: 16, padding: spacing.lg },
  title: { fontSize: font.body, fontWeight: '700', color: colors.ink, marginBottom: spacing.sm },
  body: { fontSize: font.small, color: colors.secondary, lineHeight: 20, marginBottom: spacing.lg },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: spacing.lg },
  keep: { fontSize: font.body, color: colors.secondary, fontWeight: '600' },
  tryAgain: { fontSize: font.body, color: colors.accent, fontWeight: '700' },
});
