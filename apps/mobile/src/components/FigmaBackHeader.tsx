import { appStrings } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import React from 'react';
import { Pressable, Text, StyleSheet, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { colors, font, layout, spacing, type } from '../theme';

export function FigmaBackHeader({
  onBack,
  eyebrow,
  /** Pairing Searching/Connecting use Cancel text instead of ‹ */
  leading = 'back',
  /** Pairing boards use 22 Semibold; list/settings ≈ 34 */
  backGlyphSize = 34,
}: {
  onBack?: () => void;
  eyebrow?: string;
  leading?: 'back' | 'cancel';
  backGlyphSize?: number;
}) {
  const navigation = useNavigation();
  const strings = appStrings(useAppStore((s) => s.language));
  return (
    <View style={styles.wrap}>
      <Pressable
        onPress={onBack ?? (() => navigation.goBack())}
        style={leading === 'cancel' ? styles.cancelHit : styles.back}
        hitSlop={12}
        accessibilityRole="button"
        accessibilityLabel={leading === 'cancel' ? strings.cancel : strings.back}
      >
        {leading === 'cancel' ? (
          <Text style={styles.cancelText}>{strings.cancel}</Text>
        ) : (
          <Text
            style={[
              styles.backText,
              backGlyphSize === 22 && styles.backTextPairing,
              { fontSize: backGlyphSize, lineHeight: backGlyphSize + 6 },
            ]}
          >
            ‹
          </Text>
        )}
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
  backText: { color: colors.ink, fontWeight: '300', marginTop: -4 },
  /** Pairing Setup — Semibold 22 */
  backTextPairing: { fontWeight: '600', marginTop: 0 },
  /** Pairing Searching/Connecting — Cancel 17 secondary */
  cancelHit: {
    minWidth: 72,
    height: 44,
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  cancelText: { ...type.bodyStory, color: colors.secondary },
  eyebrow: {
    fontSize: font.micro,
    fontWeight: '600',
    color: colors.secondary,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: spacing.xs,
  },
});
