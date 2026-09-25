import React, { useEffect } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { colors, font } from '../theme';

type Props = {
  videoUri: string;
  posterUri: string;
  playing: boolean;
  onTogglePlay: () => void;
};

export function RecapVideoPreview({ videoUri, posterUri, playing, onTogglePlay }: Props) {
  const player = useVideoPlayer(videoUri, (p) => {
    p.loop = true;
    p.muted = false;
  });

  useEffect(() => {
    if (playing) {
      player.play();
    } else {
      player.pause();
    }
  }, [playing, player]);

  return (
    <Pressable style={styles.wrap} onPress={onTogglePlay} accessibilityRole="button">
      {playing ? (
        <VideoView player={player} style={styles.video} contentFit="cover" nativeControls={false} />
      ) : (
        <>
          <Image source={{ uri: posterUri }} style={styles.video} resizeMode="cover" />
          <View style={styles.overlay}>
            <Text style={styles.play}>▶</Text>
          </View>
        </>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: { width: '100%', height: '100%' },
  video: { width: '100%', height: '100%' },
  overlay: {
    ...StyleSheet.absoluteFill,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0,0,0,0.12)',
  },
  play: { fontSize: 36, color: colors.paper, fontWeight: '700' },
});
