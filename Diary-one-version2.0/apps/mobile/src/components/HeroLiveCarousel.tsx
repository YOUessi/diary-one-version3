import React, { useMemo, useState } from 'react';
import { Image, Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, layout, radius, spacing } from '../theme';
import { MomentPlayer } from './MomentPlayer';

export type HeroSlide = {
  key: string;
  posterUri?: string;
  playbackUri?: string;
  title?: string;
};

type Props = {
  playbackScope: string;
  slides: HeroSlide[];
  activePlaybackId: string | null;
  onPlay: (id: string) => void;
  onStop: () => void;
};

function isVideoUri(uri?: string) {
  return !!uri && /\.(mp4|mov|m4v|webm)(\?|$)/i.test(uri);
}

/**
 * Chapter hero: poster carousel + optional LIVE (video) for motion frames.
 */
export function HeroLiveCarousel({ slides, activePlaybackId, onPlay, onStop, playbackScope }: Props) {
  const safe = useMemo(
    () => slides.filter((s) => s.posterUri || s.playbackUri),
    [slides],
  );
  const [index, setIndex] = useState(0);
  const slideKey = safe[Math.min(index, Math.max(0, safe.length - 1))]?.key;
  const liveId = `hero:${playbackScope}:${slideKey ?? ''}`;
  const liveOn = activePlaybackId === liveId;

  if (safe.length === 0) {
    return (
      <View style={styles.heroPlaceholder}>
        <View style={styles.sun} />
        <View style={styles.wave} />
      </View>
    );
  }

  const slide = safe[Math.min(index, safe.length - 1)];
  const playback = slide.playbackUri;
  const canLive = isVideoUri(playback);

  return (
    <View style={styles.hero}>
      {liveOn && canLive && playback ? (
        <MomentPlayer uri={playback} playing fill onStop={onStop} />
      ) : (
        <Image
          source={{ uri: slide.posterUri ?? playback! }}
          style={styles.heroImage}
          resizeMode="cover"
        />
      )}
      {safe.length > 1 && !liveOn ? (
        <View style={styles.dots}>
          {safe.map((s, i) => (
            <Pressable
              key={s.key}
              onPress={() => { onStop(); setIndex(i); }}
              accessibilityLabel={`Show image ${i + 1}`}
              style={[styles.dot, i === index && styles.dotOn]}
              hitSlop={6}
            />
          ))}
        </View>
      ) : null}
      {canLive ? (
        <Pressable
          style={styles.liveChip}
          onPress={() => liveOn ? onStop() : onPlay(liveId)}
          accessibilityRole="button"
          accessibilityLabel={liveOn ? 'Pause video' : 'Play video'}
          hitSlop={8}
        >
          <Text style={styles.liveText}>{liveOn ? 'Pause' : 'Play'}</Text>
        </Pressable>
      ) : null}
      {slide.title && !liveOn ? (
        <View style={styles.caption}>
          <Text style={styles.captionText} numberOfLines={1}>
            {slide.title}
          </Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  hero: {
    width: '100%',
    height: layout.heroDetail,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    overflow: 'hidden',
  },
  heroImage: { width: '100%', height: '100%' },
  heroPlaceholder: {
    width: '100%',
    height: layout.heroDetail,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    overflow: 'hidden',
  },
  sun: {
    position: 'absolute',
    top: '18%',
    right: '18%',
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.accentSoft,
  },
  wave: {
    position: 'absolute',
    left: '-8%',
    right: '-8%',
    bottom: -24,
    height: 56,
    borderRadius: 999,
    backgroundColor: colors.card,
    opacity: 0.9,
  },
  dots: {
    position: 'absolute',
    bottom: spacing.md,
    alignSelf: 'center',
    flexDirection: 'row',
    gap: 6,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255,255,255,0.45)',
  },
  dotOn: { backgroundColor: '#fff', width: 14 },
  liveChip: {
    position: 'absolute',
    top: spacing.md,
    left: spacing.md,
    backgroundColor: 'rgba(0,0,0,0.55)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  liveText: { color: '#fff', fontSize: 11, fontWeight: '700', letterSpacing: 0.6 },
  caption: {
    position: 'absolute',
    left: spacing.md,
    right: spacing.md,
    bottom: spacing.xl + 4,
  },
  captionText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
    textShadowColor: 'rgba(0,0,0,0.45)',
    textShadowRadius: 4,
  },
});
