import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { colors, font, spacing } from '../theme';

function formatClock(sec: number) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
}

export function OriginalVideoPlayer({
  uri,
  durationSec,
}: {
  uri: string;
  durationSec?: number;
}) {
  const [paused, setPaused] = useState(true);
  const [muted, setMuted] = useState(false);
  const [positionSec, setPositionSec] = useState(0);
  const player = useVideoPlayer(uri, (p) => {
    p.loop = true;
    p.muted = false;
  });

  useEffect(() => {
    player.muted = muted;
  }, [muted, player]);

  useEffect(() => {
    if (paused) player.pause();
    else player.play();
  }, [paused, player]);

  useEffect(() => {
    const id = setInterval(() => {
      const t = player.currentTime;
      if (typeof t === 'number' && !Number.isNaN(t)) setPositionSec(t);
    }, 400);
    return () => clearInterval(id);
  }, [player]);

  useEffect(() => () => player.pause(), [player]);

  const total = durationSec ?? (player.duration > 0 ? player.duration : undefined);
  const timeLabel =
    total != null
      ? `${formatClock(positionSec)} / ${formatClock(total)}`
      : `${formatClock(positionSec)} / —`;

  return (
    <View style={styles.wrap}>
      <Pressable style={styles.videoTap} onPress={() => setPaused((p) => !p)}>
        <VideoView style={styles.video} player={player} contentFit="contain" nativeControls={false} />
        {paused ? <Text style={styles.playOverlay}>▶</Text> : null}
      </Pressable>
      <View style={styles.toolbar}>
        <Text style={styles.time}>{timeLabel}</Text>
        <View style={styles.actions}>
          <Pressable onPress={() => setPaused((p) => !p)} hitSlop={8}>
            <Text style={styles.action}>{paused ? 'Play' : 'Pause'}</Text>
          </Pressable>
          <Pressable onPress={() => setMuted((m) => !m)} hitSlop={8}>
            <Text style={styles.action}>{muted ? 'Unmute' : 'Mute'}</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, width: '100%' },
  videoTap: { flex: 1, width: '100%', justifyContent: 'center' },
  video: { width: '100%', height: '100%' },
  playOverlay: {
    position: 'absolute',
    alignSelf: 'center',
    fontSize: 40,
    color: colors.paper,
  },
  toolbar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
  },
  time: { fontSize: font.small, color: colors.tertiary },
  actions: { flexDirection: 'row', gap: spacing.md },
  action: { fontSize: font.small, fontWeight: '600', color: colors.paper },
});
