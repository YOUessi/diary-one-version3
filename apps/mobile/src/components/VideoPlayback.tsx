import { appStrings } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { useAppBackgroundPause } from '../hooks/useAppBackgroundPause';
import { colors, layout, spacing } from '../theme';

function clock(value: number) {
  const sec = Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
  return `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;
}

/** One set of lifecycle rules and controls for clips and manual Originals. */
export function VideoPlayback({ uri, autoPlay = false, durationSec, immersive = false, fill = immersive, initialMuted = false, posterUri, initialPositionSec = 0, videoHeight = layout.heroHome }: {
  uri: string; autoPlay?: boolean; durationSec?: number; immersive?: boolean; initialMuted?: boolean; posterUri?: string;
  initialPositionSec?: number; videoHeight?: number; fill?: boolean;
}) {
  const initialPosition = Number.isFinite(initialPositionSec) ? Math.max(0, initialPositionSec) : 0;
  const loadedPlayer = useRef<ReturnType<typeof useVideoPlayer> | null>(null);
  const videoView = useRef<VideoView>(null);
  const openingFullscreen = useRef(false);
  const [fullscreenFailed, setFullscreenFailed] = useState(false);
  const [fullscreenControls, setFullscreenControls] = useState(false);
  const [paused, setPaused] = useState(!autoPlay);
  const strings = appStrings(useAppStore((s) => s.language));
  const [muted, setMuted] = useState(initialMuted);
  const [ended, setEnded] = useState(false);
  const [position, setPosition] = useState(initialPosition);
  const [duration, setDuration] = useState(durationSec ?? 0);
  const [seekWidth, setSeekWidth] = useState(0);
  const [failed, setFailed] = useState(false);
  const player = useVideoPlayer(uri, (p) => {
    p.loop = false;
    p.muted = initialMuted;
    p.staysActiveInBackground = false;
    p.timeUpdateEventInterval = 0.25;
    p.currentTime = initialPosition;
  });
  const pause = useCallback(() => { player.pause(); setPaused(true); }, [player]);
  const navigation = useNavigation();
  useAppBackgroundPause(pause);
  // Expo owns disposal. Unmount/source-change cleanup must only unsubscribe:
  // useVideoPlayer may already have released the native handle at that point.
  useEffect(() => navigation.addListener('blur', pause), [navigation, pause]);
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
    const loaded = player.addListener('sourceLoad', ({ duration: seconds }) => {
      setDuration(seconds);
      if (loadedPlayer.current !== player) {
        loadedPlayer.current = player;
        const start = Math.min(initialPosition, Math.max(0, seconds - 0.05));
        // Expo native seek, once per source load; never reset a user's later seek.
        player.currentTime = start;
        setPosition(start);
      }
    });
    const end = player.addListener('playToEnd', () => { setEnded(true); pause(); });
    const status = player.addListener('statusChange', ({ status: value }) => {
      setFailed(value === 'error');
      if (value === 'error') pause();
    });
    const playing = player.addListener('playingChange', ({ isPlaying }) => {
      // Reflect native fullscreen controls as well as audio interruptions.
      setPaused(!isPlaying);
      if (isPlaying) setEnded(false);
    });
    const sound = player.addListener('mutedChange', ({ muted: value }) => setMuted(value));
    return () => { time.remove(); loaded.remove(); end.remove(); status.remove(); playing.remove(); sound.remove(); };
  }, [player, pause, initialPosition]);
  const toggle = () => {
    if (!paused) { pause(); return; }
    if (ended) {
      // Expo native playback seek, not React state mutation.
      // eslint-disable-next-line react-hooks/immutability
      player.currentTime = Math.min(initialPosition, Math.max(0, duration - 0.05));
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
  const enterFullscreen = async () => {
    if (!videoView.current || openingFullscreen.current || failed) return;
    openingFullscreen.current = true;
    setFullscreenFailed(false);
    try {
      // Present this VideoView, rather than mounting another player or reloading the source.
      await videoView.current.enterFullscreen();
    } catch {
      setFullscreenFailed(true);
    } finally {
      openingFullscreen.current = false;
    }
  };
  const syncFullscreenExit = () => {
    setFullscreenControls(false);
    // Native controls can seek, mute and pause. Keep their final state without seeking again.
    setPosition(player.currentTime);
    setPaused(!player.playing);
    setMuted(player.muted);
    setEnded(player.duration > 0 && player.currentTime >= player.duration);
  };
  return (
    <View style={[styles.container, fill && styles.expanded]}>
      <Pressable style={[styles.videoArea, fill ? styles.expanded : { height: videoHeight }]} onPress={toggle} accessibilityRole="button"
        accessibilityLabel={paused ? ended ? strings.replayVideo : strings.playVideo : strings.pauseVideo}>
        <VideoView ref={videoView} style={styles.video} player={player} nativeControls={fullscreenControls}
          contentFit="contain" fullscreenOptions={{ enable: true }}
          onFullscreenEnter={() => setFullscreenControls(true)} onFullscreenExit={syncFullscreenExit} />
        {paused && position === 0 && posterUri ? <Image source={{ uri: posterUri }} style={StyleSheet.absoluteFill} resizeMode="contain" /> : null}
        {paused ? <Text style={styles.play}>▶</Text> : null}
        {failed ? <Text style={styles.error}>{strings.videoUnavailable}</Text> : null}
      </Pressable>
      <View style={styles.controls}>
        <Pressable style={styles.action} onPress={toggle} accessibilityRole="button"
          accessibilityLabel={paused ? ended ? strings.replayVideo : strings.playVideo : strings.pauseVideo}>
          <Text style={[styles.actionText, { color: ink }]}>{paused ? ended ? strings.replay : strings.play : strings.pause}</Text>
        </Pressable>
        <Pressable style={styles.seekHit} onLayout={(e) => setSeekWidth(e.nativeEvent.layout.width)}
          accessibilityRole="adjustable" accessibilityLabel={strings.videoPosition}
          accessibilityValue={{ min: 0, max: Math.round(duration), now: Math.round(position) }}
          accessibilityActions={[{ name: 'increment' }, { name: 'decrement' }]}
          onAccessibilityAction={(e) => seek(player.currentTime + (e.nativeEvent.actionName === 'increment' ? 5 : -5))}
          onPress={(e) => { if (seekWidth > 0) seek(duration * e.nativeEvent.locationX / seekWidth); }}>
          <View style={styles.track}>
            <View style={[styles.fill, { width: `${duration > 0 ? Math.min(100, position / duration * 100) : 0}%` }]} />
          </View>
          <Text style={[styles.time, { color: ink }]}>{clock(position)} / {duration > 0 ? clock(duration) : '—'}</Text>
        </Pressable>
        <Pressable style={styles.action} onPress={() => setMuted((v) => !v)} accessibilityRole="button">
          <Text style={[styles.actionText, { color: ink }]}>{muted ? strings.unmute : strings.mute}</Text>
        </Pressable>
        <Pressable style={styles.action} onPress={enterFullscreen} accessibilityRole="button"
          accessibilityLabel={strings.fullscreenVideo} disabled={failed} accessibilityState={{ disabled: failed }}>
          <Text style={[styles.actionText, { color: ink }]}>{strings.fullscreen}</Text>
        </Pressable>
      </View>
      {fullscreenFailed ? <Text accessibilityRole="alert" style={[styles.fullscreenError, { color: ink }]}>{strings.fullscreenUnavailable}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width: '100%' },
  expanded: { flex: 1 },
  videoArea: { width: '100%', justifyContent: 'center', backgroundColor: '#000' },
  video: { width: '100%', height: '100%' },
  play: { position: 'absolute', alignSelf: 'center', color: colors.paper, fontSize: 32 },
  error: { position: 'absolute', alignSelf: 'center', color: colors.paper },
  controls: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: spacing.sm, paddingVertical: 6 },
  time: { fontSize: 11, marginTop: 6, textAlign: 'center' },
  actionText: { fontSize: 12 },
  action: { minHeight: 44, minWidth: 44, justifyContent: 'center', alignItems: 'center' },
  seekHit: { flex: 1, minHeight: 44, justifyContent: 'center' },
  track: { height: 3, backgroundColor: colors.divider },
  fill: { height: 3, backgroundColor: colors.accent },
  fullscreenError: { fontSize: 12, padding: spacing.sm },
});
