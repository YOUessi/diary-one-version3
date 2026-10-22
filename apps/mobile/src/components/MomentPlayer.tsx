import React from 'react';
import { StyleSheet, View } from 'react-native';
import { colors, layout, radius } from '../theme';
import { VideoPlayback } from './VideoPlayback';

export function MomentPlayer({ uri, playing, videoHeight = layout.heroHome, focusTimeSec }: {
  uri: string; playing: boolean; onStop: () => void; videoHeight?: number; focusTimeSec?: number;
}) {
  return <View style={styles.wrap}><VideoPlayback videoHeight={videoHeight}
    key={`${uri}:${focusTimeSec ?? 0}`} uri={uri} autoPlay={playing} initialPositionSec={focusTimeSec} /></View>;
}

const styles = StyleSheet.create({
  wrap: { width: '100%', borderRadius: radius.media,
    overflow: 'hidden', backgroundColor: colors.surface },
});
