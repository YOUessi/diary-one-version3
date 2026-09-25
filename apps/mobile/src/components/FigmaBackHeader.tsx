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
  back: { minHeight: 44, justifyContent: 'center', width: 40 },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300' },
  eyebrow: {
    fontSize: font.micro,
    fontWeight: '600',
    color: colors.secondary,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginBottom: spacing.xs,
  },
});
