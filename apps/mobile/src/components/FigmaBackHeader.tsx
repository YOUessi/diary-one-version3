import React from 'react';
import { Pressable, Text, StyleSheet, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { colors, font, layout, spacing } from '../theme';

export function FigmaBackHeader({
  onBack,
  eyebrow,
}: {
  onBack?: () => void;
  eyebrow?: string;
}) {
  const navigation = useNavigation();
  return (
    <View style={styles.wrap}>
      <Pressable
        onPress={onBack ?? (() => navigation.goBack())}
        style={styles.back}
        hitSlop={12}
      >
        <Text style={styles.backText}>‹</Text>
      </Pressable>
      {eyebrow ? <Text style={styles.eyebrow}>{eyebrow}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { paddingHorizontal: layout.gutterDiary },
  /** Figma back hit target 44×44 */
  back: {
    width: 44,
    height: 44,
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  /** Figma list/settings Back Glyph ≈ 34 */
  backText: { fontSize: 34, color: colors.ink, fontWeight: '300', marginTop: -4, lineHeight: 36 },
  eyebrow: {
    fontSize: font.micro,
    fontWeight: '600',
    color: colors.secondary,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: spacing.xs,
  },
});
