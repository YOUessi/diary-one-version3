import React from 'react';
import { StyleSheet, View } from 'react-native';
import { colors, layout, radius } from '../theme';
import { VideoPlayback } from './VideoPlayback';

export function MomentPlayer({ uri, playing, fill = false }: {
  uri: string; playing: boolean; onStop: () => void; fill?: boolean;
}) {
  return <View style={[styles.wrap, fill && { height: '100%' }]}><VideoPlayback uri={uri} autoPlay={playing} /></View>;
}

const styles = StyleSheet.create({
  wrap: { height: layout.heroHome, width: '100%', borderRadius: radius.media,
    overflow: 'hidden', borderWidth: 2, borderColor: colors.accent, backgroundColor: colors.surface },
});
