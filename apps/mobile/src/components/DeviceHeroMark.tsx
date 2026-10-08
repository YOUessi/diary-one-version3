import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../theme';

/**
 * Figma Device home hero (44:1347 / 269:2102).
 * Large soft disc · vertical stem to the left · solid lens on the right.
 */
export function DeviceHeroMark({ connected = false }: { connected?: boolean }) {
  return (
    <View style={styles.wrap} accessibilityElementsHidden>
      <View style={styles.row}>
        <View style={styles.stem} />
        <View style={[styles.disc, connected && styles.discOn]}>
          <View style={[styles.lens, connected && styles.lensOn]} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 4,
    marginBottom: 24,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  stem: {
    width: 4,
    height: 40,
    borderRadius: 2,
    backgroundColor: '#C8C4BC',
  },
  disc: {
    width: 168,
    height: 168,
    borderRadius: 84,
    backgroundColor: colors.surface,
    alignItems: 'flex-end',
    justifyContent: 'center',
    paddingRight: 44,
  },
  discOn: {
    backgroundColor: '#ECE9E3',
  },
  lens: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.ink,
  },
  lensOn: {
    backgroundColor: colors.ink,
  },
});
