import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../theme';

/** Figma search magnifier — header hit 44×44; Memory field uses size=22. */
export function SearchGlyph({ size = 44 }: { size?: number }) {
  const compact = size <= 28;
  return (
    <View
      style={[styles.box, { width: size, height: size }]}
      accessibilityElementsHidden
    >
      <View
        style={[
          styles.ring,
          compact && styles.ringCompact,
          { borderColor: compact ? colors.tertiary : colors.ink },
        ]}
      />
      <View
        style={[
          styles.handle,
          compact && styles.handleCompact,
          { backgroundColor: compact ? colors.tertiary : colors.ink },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  box: { alignItems: 'center', justifyContent: 'center' },
  ring: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 1.8,
    borderColor: colors.ink,
    marginRight: 4,
    marginBottom: 4,
  },
  ringCompact: {
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 1.5,
    marginRight: 2,
    marginBottom: 2,
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
  handleCompact: {
    width: 6,
    height: 1.5,
    right: 4,
    bottom: 5,
  },
});
