import React, { useCallback, useMemo, useRef, useEffect, useState } from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import BottomSheet, { BottomSheetBackdrop, BottomSheetTextInput } from '@gorhom/bottom-sheet';
import type { BottomSheetBackdropProps } from '@gorhom/bottom-sheet';
import { colors, font, layout, radius, spacing } from '../theme';
import { STORY_DISCARD_ALERT } from '../domain/discardCopy';
import { DiscardConfirmCard } from './DiscardConfirmCard';

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
  const [discardOpen, setDiscardOpen] = useState(false);

  useEffect(() => {
    if (open) {
      ref.current?.expand();
    } else {
      setDiscardOpen(false);
      ref.current?.close();
    }
  }, [open]);

  const renderBackdrop = useCallback(
    (props: BottomSheetBackdropProps) => (
      <BottomSheetBackdrop {...props} disappearsOnIndex={-1} appearsOnIndex={0} opacity={0.35} />
    ),
    [],
  );

  const handleSheetChange = (index: number) => {
    if (index < 0) {
      setDiscardOpen(false);
      onClose();
    }
  };

  const requestClose = () => {
    if (!dirty) {
      ref.current?.close();
      return;
    }
    setDiscardOpen(true);
  };

  const saving = saveState === 'saving';
  const failed = saveState === 'failed';

  return (
    <>
    <BottomSheet
      ref={ref}
      index={-1}
      snapPoints={snapPoints}
      enablePanDownToClose={!saving && !dirty}
      onChange={handleSheetChange}
      backdropComponent={renderBackdrop}
      backgroundStyle={styles.sheetBg}
      handleIndicatorStyle={styles.handle}
    >
      <View style={styles.content}>
        <Text style={styles.title}>
          {hasExistingStory ? 'Edit what you remember' : 'Add what you remember'}
        </Text>
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
          {hasExistingStory && onRemove && !failed ? (
            <Pressable onPress={onRemove} style={styles.btn}>
              <Text style={styles.remove}>Remove note</Text>
            </Pressable>
          ) : null}
          <Pressable onPress={requestClose} style={styles.btn} disabled={saving}>
            <Text style={styles.cancel}>Cancel</Text>
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
      <DiscardConfirmCard
        visible={discardOpen}
        title={STORY_DISCARD_ALERT.title}
        message={STORY_DISCARD_ALERT.message}
        keepLabel={STORY_DISCARD_ALERT.keepEditing}
        discardLabel={STORY_DISCARD_ALERT.discard}
        onKeepEditing={() => setDiscardOpen(false)}
        onDiscard={() => {
          setDiscardOpen(false);
          ref.current?.close();
        }}
      />
    </>
  );
}

const styles = StyleSheet.create({
  /** Figma 134:1842 — sheet top r16; title 22; Save 88×44 r12 */
  sheetBg: {
    backgroundColor: colors.card,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
  },
  handle: { backgroundColor: colors.divider },
  content: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    marginBottom: spacing.xs,
    color: colors.ink,
  },
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
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    marginTop: spacing.md,
    gap: spacing.sm,
    flexWrap: 'wrap',
  },
  btn: { minHeight: 44, justifyContent: 'center', paddingHorizontal: spacing.md },
  cancel: { fontSize: font.body, color: colors.secondary },
  remove: { fontSize: font.body, color: colors.accent, fontWeight: '600' },
  save: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minWidth: 88,
    minHeight: 44,
    paddingHorizontal: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  saveText: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
});
