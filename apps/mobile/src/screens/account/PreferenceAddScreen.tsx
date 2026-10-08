import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { colors, layout, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';

/** Figma 126:1117 — Preference Sheet h≈420, top r16; title 22; Cancel text + Save 88×44 r12. */
export default function PreferenceAddScreen() {
  const navigation = useNavigation();
  const addPreference = useAppStore((s) => s.addPreference);
  const [text, setText] = useState('');

  const save = () => {
    const body = text.trim();
    if (!body) return;
    const heading = body.split(/\s+/).slice(0, 3).join(' ');
    addPreference(heading, body);
    navigation.goBack();
  };

  return (
    <Modal transparent animationType="slide" onRequestClose={() => navigation.goBack()}>
      <Pressable style={styles.backdrop} onPress={() => navigation.goBack()}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          <View style={styles.handle} />
          <Text style={styles.sheetTitle}>Add what matters to you</Text>
          <Text style={styles.hint}>
            Describe what you would like Diary One to pay more attention to.
          </Text>
          <TextInput
            value={text}
            onChangeText={setText}
            placeholder="For example: Meals and places I eat at are worth remembering."
            placeholderTextColor={colors.tertiary}
            style={styles.input}
            multiline
          />
          <Text style={styles.note}>
            Diary may show a short normalized topic title while preserving your original intent.
          </Text>
          <View style={styles.actions}>
            <Pressable onPress={() => navigation.goBack()} style={styles.cancelHit}>
              <Text style={styles.cancel}>Cancel</Text>
            </Pressable>
            <Pressable
              onPress={save}
              disabled={!text.trim()}
              style={[styles.savePill, !text.trim() && styles.saveDisabled]}
            >
              <Text style={styles.saveLabel}>Save</Text>
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
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.md,
    paddingBottom: spacing.xxxl,
    minHeight: 420,
  },
  handle: {
    alignSelf: 'center',
    width: 36,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
    marginBottom: spacing.lg,
  },
  sheetTitle: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    color: colors.ink,
    marginBottom: spacing.sm,
  },
  hint: {
    fontSize: 17,
    lineHeight: 24,
    color: colors.secondary,
    marginBottom: spacing.md,
  },
  input: {
    minHeight: 132,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: spacing.md,
    fontSize: 17,
    lineHeight: 24,
    color: colors.ink,
    textAlignVertical: 'top',
    backgroundColor: colors.paper,
  },
  note: {
    fontSize: 13,
    lineHeight: 18,
    color: colors.tertiary,
    marginTop: spacing.md,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.lg,
    minHeight: 48,
  },
  cancelHit: {
    minWidth: 88,
    minHeight: 44,
    justifyContent: 'center',
  },
  cancel: {
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '600',
    color: colors.secondary,
  },
  savePill: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minWidth: 88,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  saveLabel: { fontSize: 15, lineHeight: 20, color: '#ffffff', fontWeight: '600' },
  saveDisabled: { opacity: 0.4 },
});
