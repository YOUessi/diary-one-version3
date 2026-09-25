import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { colors, font, layout } from '../theme';

/** Figma R6-S4 — preparing / preview flows use top-left Cancel. */
export function ShareFlowCancelHeader({ onCancel }: { onCancel: () => void }) {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.wrap, { paddingTop: Math.max(insets.top, 8) }]}>
      <Pressable onPress={onCancel} style={styles.btn} hitSlop={12} accessibilityRole="button">
        <Text style={styles.label}>Cancel</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { paddingHorizontal: layout.gutterDiary },
  btn: { minHeight: 44, justifyContent: 'center', alignSelf: 'flex-start' },
  label: { fontSize: font.body, color: colors.accent, fontWeight: '600' },
});
