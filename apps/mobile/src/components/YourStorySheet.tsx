import { appStrings } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import React, { useCallback, useMemo, useRef, useEffect, useState } from 'react';
import { View, Text, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import BottomSheet, { BottomSheetBackdrop, BottomSheetTextInput } from '@gorhom/bottom-sheet';
import type { BottomSheetBackdropProps } from '@gorhom/bottom-sheet';
import { colors, font, layout, spacing } from '../theme';
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
  const strings = appStrings(useAppStore((s) => s.language));
  const snapPoints = useMemo(() => ['50%', '75%'], []);
  const [discardOpen, setDiscardOpen] = useState(false);

  useEffect(() => {
    if (open) {
      ref.current?.expand();
    } else {
      ref.current?.close();
    }
  }, [open]);

  const renderBackdrop = useCallback(
    (props: BottomSheetBackdropProps) => (
      <BottomSheetBackdrop {...props} disappearsOnIndex={-1} appearsOnIndex={0} opacity={0.18}
        pressBehavior="none" onPress={() => {
          if (saveState === 'saving') return;
          if (dirty) setDiscardOpen(true); else ref.current?.close();
        }} />
    ),
    [dirty, saveState],
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
      // This editor uses fixed percentage stops, not content measurements.
      // v5 otherwise waits for an unreported content height and cannot open.
      enableDynamicSizing={false}
      enablePanDownToClose={!saving && !dirty}
      onChange={handleSheetChange}
      backdropComponent={renderBackdrop}
      backgroundStyle={styles.sheetBg}
      handleIndicatorStyle={styles.handle}
    >
      <View style={styles.content}>
        <Text style={styles.title}>
          {hasExistingStory ? strings.editStory : strings.addStory}
        </Text>
        <Text style={styles.lead}>{strings.storyQuestion}</Text>
        <BottomSheetTextInput
          multiline
          editable={!saving}
          value={draft}
          onChangeText={onChangeDraft}
          placeholder={strings.storyHint}
          placeholderTextColor={colors.tertiary}
          style={styles.input}
        />
        <Text style={styles.footnote}>{strings.storyFootnote}</Text>
        {failed ? (
          <Text style={styles.error}>{strings.saveFailed}</Text>
        ) : null}
        {saving ? (
          <View style={styles.savingRow}>
            <ActivityIndicator color={colors.accent} size="small" />
            <Text style={styles.savingText}>{strings.saving}</Text>
          </View>
        ) : null}
        <View style={styles.actions}>
          {hasExistingStory && onRemove && !failed ? (
            <Pressable onPress={onRemove} style={styles.btn} disabled={saving}>
              <Text style={styles.remove}>{strings.removeNote}</Text>
            </Pressable>
          ) : null}
          <Pressable onPress={requestClose} style={styles.btn} disabled={saving}>
            <Text style={styles.cancel}>{strings.cancel}</Text>
          </Pressable>
          {failed ? (
            <Pressable onPress={onSave} style={[styles.btn, styles.save]}>
              <Text style={styles.saveText}>{strings.retry}</Text>
            </Pressable>
          ) : (
            <Pressable
              onPress={onSave}
              style={[styles.btn, styles.save]}
              disabled={!draft.trim() || saving}
            >
              <Text style={[styles.saveText, (!draft.trim() || saving) && { opacity: 0.4 }]}>{strings.save}</Text>
            </Pressable>
          )}
        </View>
      </View>
    </BottomSheet>
      <DiscardConfirmCard
        visible={discardOpen}
        title={strings.discardTitle}
        message={strings.discardMessage}
        keepLabel={strings.keepEditing}
        discardLabel={strings.discard}
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
  handle: {
    backgroundColor: colors.divider,
    width: 41,
    height: 4,
  },
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
    lineHeight: 22,
    color: colors.ink,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: 12,
    padding: spacing.md,
    backgroundColor: colors.paper,
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
