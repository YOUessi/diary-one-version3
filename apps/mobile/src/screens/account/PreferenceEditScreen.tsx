import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';
import type { AccountStackParamList } from '../../navigation/types';

type Route = RouteProp<AccountStackParamList, 'PreferenceEdit'>;

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
      <Modal visible onRequestClose={() => navigation.goBack()}>
        <View style={styles.sheet}>
          <Text>Preference not found.</Text>
        </View>
      </Modal>
    );
  }

  return (
    <Modal visible animationType="slide" presentationStyle="formSheet" onRequestClose={() => navigation.goBack()}>
      <View style={styles.sheet}>
        <Text style={styles.sheetTitle}>Edit preference</Text>
        <Text style={styles.hint}>Describe what you would like Diary One to pay more attention to.</Text>
        <TextInput
          value={text}
          onChangeText={setText}
          style={styles.input}
          multiline
        />
        <Text style={styles.note}>
          Diary may show a short normalized topic title while preserving your original intent.
        </Text>
        <View style={styles.actions}>
          <Pressable onPress={() => navigation.goBack()}>
            <Text style={styles.cancel}>Cancel</Text>
          </Pressable>
          <Pressable onPress={save} disabled={!text.trim()}>
            <Text style={[styles.save, !text.trim() && styles.saveDisabled]}>Save</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  sheet: {
    flex: 1,
    backgroundColor: colors.paper,
    padding: layout.gutterDiary,
    paddingTop: spacing.xl,
  },
  sheetTitle: { fontSize: 22, fontWeight: '600', color: colors.ink, marginBottom: spacing.sm },
  hint: { fontSize: font.small, color: colors.secondary, marginBottom: spacing.md },
  input: {
    minHeight: 120,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    fontSize: font.body,
    color: colors.ink,
    textAlignVertical: 'top',
  },
  note: { fontSize: font.micro, color: colors.tertiary, marginTop: spacing.md, lineHeight: 18 },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.xl,
  },
  cancel: { fontSize: font.body, color: colors.secondary, fontWeight: '600' },
  save: { fontSize: font.body, color: colors.accent, fontWeight: '700' },
  saveDisabled: { opacity: 0.4 },
});
