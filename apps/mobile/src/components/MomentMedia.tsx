import { appStrings } from '../domain/strings';
import { useAppStore } from '../store/useAppStore';
import React from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, layout, radius, type } from '../theme';
import { MomentPlayer } from './MomentPlayer';
import { ChapterMotionPlayer } from './ChapterMotionPlayer';
import type { ChapterMotionCover } from '../model';

function isVideoUri(uri: string) {
  return /\.(mp4|mov|m4v|webm)(\?|$)/i.test(uri);
}

type Props = {
  /** Idle poster / still frame (JPG preferred for Motion). */
  uri: string;
  /** Local or remote MP4 when this moment is Motion; falls back to `uri`. */
  playbackUri?: string;
  focusTimeSec?: number;
  motionCover?: ChapterMotionCover;
  playing: boolean;
  onPlay: () => void;
  onStop: () => void;
};

/** Figma 176:1966 / 176:2021 — idle poster; playing = accent stroke + Playing badge; tap to stop. */
export function MomentMedia({ uri, playbackUri, focusTimeSec, motionCover, playing, onPlay, onStop }: Props) {
  const strings = appStrings(useAppStore((s) => s.language));
  const playSource = playbackUri ?? uri;
  const isMotion = isVideoUri(playSource);

  if (motionCover) {
    return <View style={styles.poster}>
      <ChapterMotionPlayer cover={motionCover} height={layout.heroHome} />
    </View>;
  }

  if (!playing) {
    return (
      <Pressable onPress={onPlay} style={styles.poster} accessibilityLabel={isMotion ? strings.playVideo : strings.showImage}>
        <Image source={{ uri }} style={styles.posterImage} resizeMode="cover" />
        <View style={styles.posterOverlay}>
          {isMotion ? <Text style={styles.playGlyph}>▶</Text> : null}
        </View>
      </Pressable>
    );
  }

  if (isMotion) {
    return <MomentPlayer uri={playSource} focusTimeSec={focusTimeSec} playing onStop={onStop} />;
  }

  return (
    <Pressable
      onPress={onStop}
      style={styles.stillPlaying}
      accessibilityLabel={strings.close}
      accessibilityState={{ selected: true }}
    >
      <Image source={{ uri }} style={styles.stillImage} resizeMode="cover" />
      <View style={styles.playingBadge}>
        <Text style={styles.playingText}>{strings.showImage}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  poster: {
    height: layout.heroHome,
    borderRadius: radius.media,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  posterImage: { width: '100%', height: '100%' },
  posterOverlay: {
    ...StyleSheet.absoluteFill,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0,0,0,0.08)',
  },
  playGlyph: { fontSize: 28, color: colors.paper },
  stillPlaying: {
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
  stillImage: { width: '100%', height: '100%' },
});
