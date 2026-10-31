import React, { useEffect, useRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { useNavigation } from '@react-navigation/native';
import { useAppBackgroundPause } from '../hooks/useAppBackgroundPause';
import type { ChapterMotionCover } from '../model';

/** Chapter's primary presentation: genuine 3s local motion, never synthetic.
 * If a native MOV is unavailable (Expo Go), replay ONLY the authenticated
 * 3s window inside its local original. No fake/remote generated video.
 */
export function ChapterMotionPlayer({ cover, active = true, height }: {
  cover: ChapterMotionCover;
  active?: boolean;
  height?: number;
}) {
  const initialized = useRef(false);
  const start = cover.status === 'rendered' ? 0 : cover.clipStartSec;
  const end = cover.status === 'rendered' ? 3 : cover.clipEndSec;
  const player = useVideoPlayer(cover.motionUri, p => {
    p.muted = true;
    p.loop = cover.status === 'rendered';
    p.staysActiveInBackground = false;
    p.timeUpdateEventInterval = 0.12;
    p.currentTime = start;
  });
  const navigation = useNavigation();
  useAppBackgroundPause(() => player.pause());
  useEffect(() => navigation.addListener('blur', () => player.pause()), [navigation, player]);
  useEffect(() => {
    const load = player.addListener('sourceLoad', () => {
      if (!initialized.current) {
        initialized.current = true;
        // A nonexported source must start precisely at the original keyframe window.
        player.currentTime = start;
      }
      if (active) player.play();
    });
    const time = player.addListener('timeUpdate', ({ currentTime }) => {
      if (active && cover.status === 'source_window' && currentTime >= end - 0.08) {
        player.currentTime = start;
        player.play();
      }
    });
    const endEvent = player.addListener('playToEnd', () => {
      if (active && cover.status === 'rendered') {
        player.currentTime = 0;
        player.play();
      }
    });
    if (active) player.play();
    else player.pause();
    return () => { load.remove(); time.remove(); endEvent.remove(); player.pause(); };
  }, [player, active, start, end, cover.status]);
  return (
    <View style={[styles.frame, height !== undefined ? { height } : styles.fill]}>
      <VideoView style={styles.video} player={player} nativeControls={false} contentFit="cover" />
    </View>
  );
}

const styles = StyleSheet.create({
  frame: { width: '100%', overflow: 'hidden', backgroundColor: '#0F2420' },
  fill: { flex: 1, minHeight: 1 },
  video: { width: '100%', height: '100%' },
});
