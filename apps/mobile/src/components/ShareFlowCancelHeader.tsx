import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, layout, type } from '../theme';

/**
 * Figma R6-S4 Cancel — call sites already wrap SafeAreaView edges=['top'].
 * Do not add safe-area inset here (avoids double top padding).
 */
export function ShareFlowCancelHeader({ onCancel }: { onCancel: () => void }) {
  return (
    <View style={styles.wrap}>
      <Pressable onPress={onCancel} style={styles.btn} hitSlop={12} accessibilityRole="button">
        <Text style={styles.label}>Cancel</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { paddingHorizontal: layout.gutterDiary },
  btn: { minHeight: 44, justifyContent: 'center', alignSelf: 'flex-start' },
  /** Figma Cancel — iOS secondary gray #8E8E93 */
  label: { ...type.bodyStory, color: '#8E8E93', fontWeight: '400' },
});
