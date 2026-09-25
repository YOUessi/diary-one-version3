import React, { useCallback, useMemo, useRef, useEffect } from 'react';
import { View, Text, Pressable, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import BottomSheet, { BottomSheetBackdrop, BottomSheetTextInput } from '@gorhom/bottom-sheet';
import type { BottomSheetBackdropProps } from '@gorhom/bottom-sheet';
import { colors, font, layout, radius, spacing } from '../theme';
import { STORY_DISCARD_ALERT } from '../domain/discardCopy';

export type YourStorySaveState = 'idle' | 'saving' | 'failed';

type Props = {
  open: boolean;
  draft: string;
  dirty: boolean;
  saveState: YourStorySaveState;
  hasExistingStory: boolean;
  onChangeDraft: (text: string) => void;
  onClose: () => void;
  onSave: () => void;
  onRemove?: () => void;
};

export function YourStorySheet({
  open,
  draft,
  dirty,
  saveState,
  hasExistingStory,
  onChangeDraft,
  onClose,
  onSave,
  onRemove,
}: Props) {
  const ref = useRef<BottomSheet>(null);
  const snapPoints = useMemo(() => ['50%', '75%'], []);

  useEffect(() => {
    if (open) ref.current?.expand();
    else ref.current?.close();
  }, [open]);

  const renderBackdrop = useCallback(
    (props: BottomSheetBackdropProps) => (
      <BottomSheetBackdrop {...props} disappearsOnIndex={-1} appearsOnIndex={0} opacity={0.35} />
    ),
    [],
  );

  const handleSheetChange = (index: number) => {
    if (index < 0) onClose();
  };

  const requestClose = () => {
    if (!dirty) {
      ref.current?.close();
      return;
    }
    Alert.alert(STORY_DISCARD_ALERT.title, STORY_DISCARD_ALERT.message, [
      { text: STORY_DISCARD_ALERT.keepEditing, style: 'cancel' },
      {
        text: STORY_DISCARD_ALERT.discard,
        style: 'destructive',
        onPress: () => ref.current?.close(),
      },
    ]);
  };

  const saving = saveState === 'saving';
  const failed = saveState === 'failed';

  return (
    <BottomSheet
      ref={ref}
      index={-1}
      snapPoints={snapPoints}
      enablePanDownToClose={!saving}
      onChange={handleSheetChange}
      backdropComponent={renderBackdrop}
      backgroundStyle={styles.sheetBg}
      handleIndicatorStyle={styles.handle}
    >
      <View style={styles.content}>
        <Text style={styles.title}>Edit what you remember</Text>
        <Text style={styles.lead}>What would you like to remember about this memory?</Text>
        <BottomSheetTextInput
          multiline
          editable={!saving}
          value={draft}
          onChangeText={onChangeDraft}
          placeholder="Add a person, detail, or why this memory mattered to you."
          placeholderTextColor={colors.tertiary}
          style={styles.input}
        />
        <Text style={styles.footnote}>This is saved separately from Diary&apos;s AI summary.</Text>
        {failed ? (
          <Text style={styles.error}>Couldn&apos;t save. Your text is still here.</Text>
        ) : null}
        {saving ? (
          <View style={styles.savingRow}>
            <ActivityIndicator color={colors.accent} size="small" />
            <Text style={styles.savingText}>Saving…</Text>
          </View>
        ) : null}
        <View style={styles.actions}>
          {hasExistingStory && onRemove ? (
            <Pressable onPress={onRemove} style={styles.btn}>
              <Text style={styles.remove}>Remove</Text>
            </Pressable>
          ) : null}
          <Pressable onPress={requestClose} style={styles.btn} disabled={saving}>
            <Text style={styles.cancel}>{failed ? 'Cancel' : 'Cancel'}</Text>
          </Pressable>
          {failed ? (
            <Pressable onPress={onSave} style={[styles.btn, styles.save]}>
              <Text style={styles.saveText}>Try Again</Text>
            </Pressable>
          ) : (
            <Pressable
              onPress={onSave}
              style={[styles.btn, styles.save]}
              disabled={!draft.trim() || saving}
            >
              <Text style={[styles.saveText, (!draft.trim() || saving) && { opacity: 0.4 }]}>Save</Text>
            </Pressable>
          )}
        </View>
      </View>
    </BottomSheet>
  );
}

const styles = StyleSheet.create({
  sheetBg: { backgroundColor: colors.card },
  handle: { backgroundColor: colors.divider },
  content: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: { fontSize: font.h2, fontWeight: '600', marginBottom: spacing.xs, color: colors.ink },
  lead: { fontSize: font.small, color: colors.secondary, marginBottom: spacing.md },
  input: {
    minHeight: 120,
    fontSize: font.body,
    color: colors.ink,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
  },
  footnote: { fontSize: font.micro, color: colors.tertiary, marginTop: spacing.sm, lineHeight: 18 },
  error: { fontSize: font.small, color: colors.accent, marginTop: spacing.sm },
  savingRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginTop: spacing.md },
  savingText: { fontSize: font.small, color: colors.secondary },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: spacing.md, gap: spacing.sm, flexWrap: 'wrap' },
  btn: { minHeight: layout.minTouch, justifyContent: 'center', paddingHorizontal: spacing.md },
  cancel: { fontSize: font.body, color: colors.secondary },
  remove: { fontSize: font.body, color: colors.accent, fontWeight: '600' },
  save: { backgroundColor: colors.ink, borderRadius: radius.pill, paddingHorizontal: spacing.lg },
  saveText: { color: colors.paper, fontWeight: '600' },
});
