import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { colors, font, radius } from '../theme';

type Props = {
  uri: string;
  playing: boolean;
  onStop: () => void;
};

export function MomentPlayer({ uri, playing, onStop }: Props) {
  const player = useVideoPlayer(uri, (p) => {
    p.loop = false;
    p.muted = false;
  });

  useEffect(() => {
    if (playing) {
      player.play();
    } else {
      player.pause();
    }
  }, [playing, player]);

  useEffect(() => {
    return () => {
      player.pause();
    };
  }, [player]);

  if (!playing) {
    return (
      <Pressable onPress={() => player.play()} style={styles.poster}>
        <Text style={styles.hint}>Tap to play</Text>
      </Pressable>
    );
  }

  return (
    <View style={styles.wrap}>
      <VideoView style={styles.video} player={player} nativeControls contentFit="cover" />
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
  wrap: {
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
  video: { width: '100%', height: '100%' },
  poster: {
    height: 200,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hint: { fontSize: font.small, color: colors.tertiary },
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
