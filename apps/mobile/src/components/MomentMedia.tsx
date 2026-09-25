import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, font, radius } from '../theme';
import { MomentPlayer } from './MomentPlayer';

function isVideoUri(uri: string) {
  return /\.(mp4|mov|m4v|webm)(\?|$)/i.test(uri);
}

type Props = {
  uri: string;
  playing: boolean;
  onPlay: () => void;
  onStop: () => void;
};

export function MomentMedia({ uri, playing, onPlay, onStop }: Props) {
  if (!playing) {
    return (
      <Pressable onPress={onPlay} style={styles.poster}>
        <Image source={{ uri }} style={styles.posterImage} resizeMode="cover" />
        <View style={styles.posterOverlay}>
          {isVideoUri(uri) ? <Text style={styles.playGlyph}>▶</Text> : null}
          <Text style={styles.hint}>Tap to play</Text>
        </View>
      </Pressable>
    );
  }

  if (isVideoUri(uri)) {
    return <MomentPlayer uri={uri} playing onStop={onStop} />;
  }

  return (
    <View style={styles.stillPlaying}>
      <Image source={{ uri }} style={styles.stillImage} resizeMode="cover" />
      <View style={styles.playingBadge}>
        <Text style={styles.playingText}>Playing</Text>
      </View>
      <Pressable onPress={onStop} style={styles.stop} accessibilityLabel="Stop playback">
        <Text style={styles.stopText}>Stop</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  poster: {
    height: 200,
    borderRadius: radius.control,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  posterImage: { width: '100%', height: '100%' },
  posterOverlay: {
    ...StyleSheet.absoluteFill,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0,0,0,0.12)',
  },
  playGlyph: { fontSize: 28, color: colors.paper, marginBottom: 4 },
  hint: { fontSize: font.small, color: colors.paper, fontWeight: '600' },
  stillPlaying: {
    height: 200,
    borderRadius: radius.control,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: colors.accent,
  },
  playingBadge: {
    position: 'absolute',
    left: 8,
    top: 8,
    backgroundColor: 'rgba(0,0,0,0.55)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  playingText: { color: colors.paper, fontSize: font.micro, fontWeight: '700' },
  stillImage: { width: '100%', height: '100%' },
  stop: {
    position: 'absolute',
    right: 8,
    bottom: 8,
    backgroundColor: 'rgba(0,0,0,0.55)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  stopText: { color: '#fff', fontSize: font.micro, fontWeight: '600' },
});
