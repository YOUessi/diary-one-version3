import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../theme';

/** Figma Share / Day · Share / Memory glyph (↑ + tray). */
export function ShareGlyph({ size = 44 }: { size?: number }) {
  return (
    <View style={[styles.box, { width: size, height: size }]} accessibilityElementsHidden>
      <Text style={styles.arrow}>↑</Text>
      <View style={styles.tray}>
        <View style={styles.leg} />
        <View style={styles.legRight} />
        <View style={styles.base} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { alignItems: 'center', justifyContent: 'flex-start' },
  arrow: {
    fontSize: 22,
    fontWeight: '600',
    color: colors.ink,
    lineHeight: 24,
    textAlign: 'center',
  },
  tray: {
    position: 'absolute',
    left: 13,
    top: 22,
    width: 18,
    height: 12,
  },
  leg: {
    position: 'absolute',
    left: 0,
    top: 0,
    width: 1.5,
    height: 12,
    backgroundColor: colors.ink,
  },
  legRight: {
    position: 'absolute',
    right: 0,
    top: 0,
    width: 1.5,
    height: 12,
    backgroundColor: colors.ink,
  },
  base: {
    position: 'absolute',
    left: 0,
    bottom: 0,
    width: 18,
    height: 1.5,
    backgroundColor: colors.ink,
  },
});
