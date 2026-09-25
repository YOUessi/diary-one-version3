import React from 'react';
import { View, Text, Pressable, StyleSheet, Image } from 'react-native';
import { colors, font, radius } from '../theme';
import { formatDurationClock } from '../domain/formatMedia';
import type { CapturedOriginal } from '../model';

export function CapturedGridCell({
  item,
  onPress,
}: {
  item: CapturedOriginal;
  onPress: () => void;
}) {
  const duration =
    item.kind === 'video' && item.durationSec != null
      ? formatDurationClock(item.durationSec)
      : null;

  return (
    <Pressable onPress={onPress} style={styles.cell} accessibilityRole="button">
      {item.posterUri ? (
        <Image source={{ uri: item.posterUri }} style={styles.image} resizeMode="cover" />
      ) : (
        <View style={styles.placeholder}>
          <Text style={styles.placeholderText}>{item.kind === 'photo' ? 'Photo' : 'Video'}</Text>
        </View>
      )}
      {duration ? (
        <View style={styles.durationBadge}>
          <Text style={styles.durationText}>{duration}</Text>
        </View>
      ) : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  cell: {
    width: '31.5%',
    aspectRatio: 1,
    borderRadius: radius.control,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  image: { width: '100%', height: '100%' },
  placeholder: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
  },
  placeholderText: { fontSize: font.micro, color: colors.tertiary },
  durationBadge: {
    position: 'absolute',
    right: 6,
    bottom: 6,
    backgroundColor: 'rgba(0,0,0,0.55)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  durationText: { fontSize: font.micro, color: colors.paper, fontWeight: '600' },
});
