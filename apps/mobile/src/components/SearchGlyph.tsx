import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../theme';

/** Figma search magnifier (44 hit target). */
export function SearchGlyph() {
  return (
    <View style={styles.box} accessibilityElementsHidden>
      <View style={styles.ring} />
      <View style={styles.handle} />
    </View>
  );
}

const styles = StyleSheet.create({
  box: { width: 44, height: 44, alignItems: 'center', justifyContent: 'center' },
  ring: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 1.8,
    borderColor: colors.ink,
    marginRight: 4,
    marginBottom: 4,
  },
  handle: {
    position: 'absolute',
    width: 8,
    height: 1.8,
    backgroundColor: colors.ink,
    borderRadius: 1,
    right: 12,
    bottom: 14,
    transform: [{ rotate: '45deg' }],
  },
});
