import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { colors, layout } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';

type Route = RouteProp<AccountStackParamList, 'PreferenceEdit'>;

/** Figma 126:1163 — same Preference Sheet metrics as Add. */
export default function PreferenceEditScreen() {
  const { preferenceId } = useRoute<Route>().params;
  const navigation = useNavigation();
  const pref = useAppStore((s) => s.preferences.find((p) => p.id === preferenceId));
  const updatePreference = useAppStore((s) => s.updatePreference);
  const [text, setText] = useState(pref?.text ?? '');

  const save = () => {
    if (!pref) return;
    const body = text.trim();
    if (!body) return;
    updatePreference(pref.id, pref.title, body);
    navigation.goBack();
  };

  if (!pref) {
    return (
      <Modal transparent visible onRequestClose={() => navigation.goBack()}>
        <View style={styles.backdrop}>
          <View style={styles.sheet}>
            <Text style={styles.sheetTitle}>Preference not found.</Text>
            <Pressable onPress={() => navigation.goBack()} style={styles.cancelHit}>
              <Text style={styles.cancel}>Cancel</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
    );
  }

  return (
    <Modal transparent animationType="slide" onRequestClose={() => navigation.goBack()}>
      <Pressable style={styles.backdrop} onPress={() => navigation.goBack()}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          <View style={styles.handle} />
          <Text style={styles.sheetTitle}>Edit preference</Text>
          <Text style={styles.hint}>
            Describe what you would like Diary One to pay more attention to.
          </Text>
          <TextInput value={text} onChangeText={setText} style={styles.input} multiline />
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
    backgroundColor: 'rgba(0,0,0,0.18)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: colors.card,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    paddingHorizontal: layout.gutterDiary,
    paddingTop: 14,
    paddingBottom: 26,
    minHeight: 420,
    gap: 14,
  },
  handle: {
    alignSelf: 'center',
    width: 36,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.divider,
  },
  sheetTitle: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    letterSpacing: -0.1,
    color: colors.ink,
  },
  hint: {
    fontSize: 17,
    lineHeight: 24,
    color: colors.secondary,
  },
  input: {
    height: 132,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.divider,
    paddingHorizontal: 13,
    paddingVertical: 11,
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
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: 10,
    minHeight: 48,
  },
  cancelHit: {
    width: 88,
    minHeight: 44,
    alignItems: 'center',
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
    width: 88,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  saveLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
  saveDisabled: { opacity: 0.4 },
});
