import React from 'react';
import { View, Text, Pressable, StyleSheet, Image } from 'react-native';
import { colors, layout, radius, spacing, type } from '../theme';
import { MemoryTag } from './MemoryTag';

/** Figma D1/Chapter Card — hero 198 · time · title · tags · story. */
export function ChapterBlock({
  title,
  dateLabel,
  weakTime,
  aiStory,
  tags,
  heroUri,
  showDateMeta = false,
  onPress,
}: {
  title: string;
  dateLabel: string;
  weakTime?: string;
  aiStory: string;
  tags: string[];
  heroUri?: string;
  showDateMeta?: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.block, pressed && styles.pressed]}
      accessibilityRole="button"
      accessibilityLabel={title}
    >
      <View style={styles.hero} accessibilityIgnoresInvertColors>
        {heroUri ? (
          <Image source={{ uri: heroUri }} style={styles.heroImage} resizeMode="cover" />
        ) : (
          <View style={styles.heroPlaceholder}>
            <View style={styles.sun} />
            <View style={styles.wave} />
          </View>
        )}
      </View>
      <View style={styles.copy}>
        {weakTime ? <Text style={styles.weakTime}>{weakTime}</Text> : null}
        <Text style={styles.title}>{title}</Text>
        {showDateMeta ? <Text style={styles.meta}>{dateLabel}</Text> : null}
        <View
          style={styles.tagRow}
          pointerEvents="none"
          accessibilityElementsHidden
          importantForAccessibility="no-hide-descendants"
        >
          {tags.slice(0, 2).map((t) => (
            <MemoryTag key={t} label={t} tone="primary" />
          ))}
        </View>
        <Text style={styles.story} numberOfLines={2}>
          {aiStory}
        </Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  block: {
    width: '100%',
    gap: spacing.md,
    marginBottom: 0,
    minHeight: layout.minTouch,
  },
  pressed: { opacity: 0.92 },
  hero: {
    width: '100%',
    height: layout.heroHome,
    backgroundColor: colors.surface,
    borderRadius: radius.media,
    overflow: 'hidden',
  },
  heroImage: { width: '100%', height: '100%' },
  heroPlaceholder: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  sun: {
    position: 'absolute',
    top: 30,
    right: 48,
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: '#F5E6C8',
  },
  wave: {
    position: 'absolute',
    left: -34,
    bottom: -40,
    width: 420,
    height: 150,
    borderRadius: 210,
    backgroundColor: '#F7F5F0',
  },
  copy: {
    width: '100%',
    gap: spacing.sm,
  },
  weakTime: {
    ...type.metadata,
    color: colors.tertiary,
  },
  title: {
    ...type.titleChapter,
    color: colors.ink,
  },
  meta: {
    ...type.caption,
    color: colors.tertiary,
  },
  tagRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    height: 26,
    overflow: 'hidden',
  },
  story: {
    ...type.bodyStory,
    color: colors.secondary,
  },
});
