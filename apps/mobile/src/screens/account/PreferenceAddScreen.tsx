import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { colors, font, layout, radius, spacing } from '../../theme';
import { useAppStore } from '../../store/useAppStore';

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
    <Modal visible animationType="slide" presentationStyle="formSheet" onRequestClose={() => navigation.goBack()}>
      <View style={styles.sheet}>
        <Text style={styles.sheetTitle}>Add what matters to you</Text>
        <Text style={styles.hint}>Describe what you would like Diary One to pay more attention to.</Text>
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
  titleInput: {
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    fontSize: font.body,
    color: colors.ink,
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
