import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../theme';

/**
 * Figma Device hero (44:1347 / 269:2102) — soft disc + lens.
 * `compact` fits inside the white status card (≈110–122 wide).
 */
export function DeviceHeroMark({
  connected = false,
  compact = false,
}: {
  connected?: boolean;
  compact?: boolean;
}) {
  return (
    <View style={[styles.wrap, compact && styles.wrapCompact]} accessibilityElementsHidden>
      <View style={styles.row}>
        <View style={[styles.stem, compact && styles.stemCompact]} />
        <View
          style={[
            styles.disc,
            compact && styles.discCompact,
            connected ? styles.discOn : styles.discOff,
          ]}
        >
          <View style={[styles.lens, compact && styles.lensCompact]} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    marginBottom: 8,
  },
  wrapCompact: {
    marginTop: 12,
    marginBottom: 4,
    height: 116,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  stem: {
    width: 4,
    height: 40,
    borderRadius: 2,
    backgroundColor: '#C8C4BC',
  },
  stemCompact: { height: 28, width: 3 },
  disc: {
    width: 168,
    height: 168,
    borderRadius: 84,
    backgroundColor: colors.surface,
    alignItems: 'flex-end',
    justifyContent: 'center',
    paddingRight: 44,
  },
  discCompact: {
    width: 110,
    height: 110,
    borderRadius: 55,
    paddingRight: 28,
  },
  discOn: {
    backgroundColor: '#ECE9E3',
  },
  discOff: {
    backgroundColor: '#E8E5DF',
    opacity: 0.92,
  },
  lens: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.ink,
  },
  lensCompact: {
    width: 18,
    height: 18,
    borderRadius: 9,
  },
});
