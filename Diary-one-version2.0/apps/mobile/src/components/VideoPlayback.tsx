import React, { useCallback, useEffect, useState } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { useAppBackgroundPause } from '../hooks/useAppBackgroundPause';
import { colors, spacing } from '../theme';

function clock(value: number) {
  const sec = Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
  return `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;
}

/** One set of lifecycle rules and controls for clips and manual Originals. */
export function VideoPlayback({ uri, autoPlay = false, durationSec, immersive = false, initialMuted = false, posterUri }: {
  uri: string; autoPlay?: boolean; durationSec?: number; immersive?: boolean; initialMuted?: boolean; posterUri?: string;
}) {
  const [paused, setPaused] = useState(!autoPlay);
  const [muted, setMuted] = useState(initialMuted);
  const [ended, setEnded] = useState(false);
  const [position, setPosition] = useState(0);
  const [duration, setDuration] = useState(durationSec ?? 0);
  const [seekWidth, setSeekWidth] = useState(0);
  const [failed, setFailed] = useState(false);
  const player = useVideoPlayer(uri, (p) => {
    p.loop = false;
    p.muted = initialMuted;
    p.staysActiveInBackground = false;
    p.timeUpdateEventInterval = 0.25;
  });
  const pause = useCallback(() => { player.pause(); setPaused(true); }, [player]);
  useAppBackgroundPause(pause);
  useFocusEffect(useCallback(() => () => pause(), [pause]));
  useEffect(() => {
    if (paused) player.pause(); else player.play();
  }, [paused, player]);
  useEffect(() => {
    // Expo VideoPlayer is an imperative native handle; its documented setters are mutable.
    // eslint-disable-next-line react-hooks/immutability
    player.muted = muted;
  }, [muted, player]);
  useEffect(() => {
    const time = player.addListener('timeUpdate', ({ currentTime }) => setPosition(currentTime));
    const loaded = player.addListener('sourceLoad', ({ duration: seconds }) => setDuration(seconds));
    const end = player.addListener('playToEnd', () => { setEnded(true); pause(); });
    const status = player.addListener('statusChange', ({ status: value }) => {
      setFailed(value === 'error');
      if (value === 'error') pause();
    });
    const playing = player.addListener('playingChange', ({ isPlaying }) => {
      // Audio interruptions stay paused until the next explicit user action.
      if (!isPlaying) setPaused(true);
    });
    return () => { time.remove(); loaded.remove(); end.remove(); status.remove(); playing.remove(); };
  }, [player, pause]);
  const toggle = () => {
    if (!paused) { pause(); return; }
    if (ended) {
      // Expo native playback seek, not React state mutation.
      // eslint-disable-next-line react-hooks/immutability
      player.currentTime = 0;
      setEnded(false);
    }
    setPaused(false);
  };
  const seek = (value: number) => {
    if (duration <= 0) return;
    // Expo native playback seek, not React state mutation.
    // eslint-disable-next-line react-hooks/immutability
    player.currentTime = Math.max(0, Math.min(duration, value));
    setPosition(player.currentTime);
    setEnded(false);
  };
  const ink = immersive ? colors.paper : colors.ink;
  return (
    <View style={styles.container}>
      <Pressable style={styles.videoArea} onPress={toggle} accessibilityRole="button"
        accessibilityLabel={paused ? ended ? 'Replay video' : 'Play video' : 'Pause video'}>
        <VideoView style={styles.video} player={player} nativeControls={false}
          contentFit={immersive ? 'contain' : 'cover'} />
        {paused && position === 0 && posterUri ? <Image source={{ uri: posterUri }} style={StyleSheet.absoluteFill} resizeMode="cover" /> : null}
        {paused ? <Text style={styles.play}>▶</Text> : null}
        {failed ? <Text style={styles.error}>Video unavailable</Text> : null}
      </Pressable>
      <View style={styles.controls}>
        <Text style={[styles.time, { color: ink }]}>{clock(position)} / {duration > 0 ? clock(duration) : '—'}</Text>
        <Pressable style={styles.action} onPress={toggle} accessibilityRole="button">
          <Text style={{ color: ink }}>{paused ? ended ? 'Replay' : 'Play' : 'Pause'}</Text>
        </Pressable>
        <Pressable style={styles.action} onPress={() => setMuted((v) => !v)} accessibilityRole="button">
          <Text style={{ color: ink }}>{muted ? 'Unmute' : 'Mute'}</Text>
        </Pressable>
      </View>
      <Pressable style={styles.seekHit} onLayout={(e) => setSeekWidth(e.nativeEvent.layout.width)}
        accessibilityRole="adjustable" accessibilityLabel="Video position"
        accessibilityValue={{ min: 0, max: Math.round(duration), now: Math.round(position) }}
        accessibilityActions={[{ name: 'increment' }, { name: 'decrement' }]}
        onAccessibilityAction={(e) => seek(player.currentTime + (e.nativeEvent.actionName === 'increment' ? 5 : -5))}
        onPress={(e) => { if (seekWidth > 0) seek(duration * e.nativeEvent.locationX / seekWidth); }}>
        <View style={styles.track}>
          <View style={[styles.fill, { width: `${duration > 0 ? Math.min(100, position / duration * 100) : 0}%` }]} />
        </View>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, width: '100%' },
  videoArea: { flex: 1, justifyContent: 'center', backgroundColor: colors.surface },
  video: { width: '100%', height: '100%' },
  play: { position: 'absolute', alignSelf: 'center', color: colors.paper, fontSize: 32 },
  error: { position: 'absolute', alignSelf: 'center', color: colors.paper },
  controls: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, paddingHorizontal: spacing.sm },
  time: { flex: 1, fontSize: 12 },
  action: { minHeight: 44, minWidth: 44, justifyContent: 'center', alignItems: 'center' },
  seekHit: { minHeight: 44, justifyContent: 'center', paddingHorizontal: spacing.sm },
  track: { height: 3, backgroundColor: colors.divider },
  fill: { height: 3, backgroundColor: colors.accent },
});
