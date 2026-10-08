import React, { type ReactNode } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, layout, spacing, type } from '../theme';

/** Figma Header / Diary + Search — Title/Large 34. */
export function FigmaScreenHeader({
  title,
  rightAccessory,
}: {
  title: string;
  rightAccessory?: ReactNode;
}) {
  return (
    <View style={styles.row}>
      <Text style={styles.title}>{title}</Text>
      {rightAccessory ? <View style={styles.right}>{rightAccessory}</View> : null}
    </View>
  );
}

export function FigmaEyebrow({ children }: { children: string }) {
  return <Text style={styles.eyebrow}>{children}</Text>;
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 44,
    marginBottom: spacing.xxl,
  },
  title: {
    ...type.titleLarge,
    color: colors.ink,
    flex: 1,
  },
  right: {
    width: layout.minTouch,
    height: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  eyebrow: {
    ...type.metadata,
    fontWeight: '600',
    color: colors.tertiary,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    marginTop: spacing.xl,
    marginBottom: spacing.xs,
  },
});
