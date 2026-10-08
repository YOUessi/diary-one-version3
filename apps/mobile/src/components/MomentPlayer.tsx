import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { colors, layout, radius, type } from '../theme';

type Props = {
  uri: string;
  playing: boolean;
  onStop: () => void;
};

/** Figma Short Clip Playing — accent frame + Playing; tap media to stop. */
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
    <Pressable
      onPress={onStop}
      style={styles.wrap}
      accessibilityLabel="Stop playback"
      accessibilityState={{ selected: true }}
    >
      <VideoView style={styles.video} player={player} nativeControls={false} contentFit="cover" />
      <View style={styles.playingBadge} pointerEvents="none">
        <Text style={styles.playingText}>Playing</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: {
    height: layout.heroHome,
    borderRadius: radius.media,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: colors.accent,
    backgroundColor: colors.surface,
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
  playingText: { ...type.metadata, color: colors.paper, fontWeight: '700' },
  video: { width: '100%', height: '100%' },
  poster: {
    height: layout.heroHome,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hint: { ...type.caption, color: colors.tertiary },
});
