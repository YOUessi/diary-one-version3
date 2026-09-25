import React from 'react';
import { View, Text, Pressable, StyleSheet, Image } from 'react-native';
import { colors, font, layout, spacing } from '../theme';
import { MemoryTag } from './MemoryTag';

/** Figma D1/Chapter Card — editorial block on Paper, no outer card or shadow. */
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
          <Text style={styles.heroPlaceholder}>Hero · curated still</Text>
        )}
      </View>
      {weakTime ? <Text style={styles.weakTime}>{weakTime}</Text> : null}
      <Text style={styles.title}>{title}</Text>
      {showDateMeta ? <Text style={styles.meta}>{dateLabel}</Text> : null}
      <Text style={styles.story} numberOfLines={2}>{aiStory}</Text>
      <View style={styles.tagRow} pointerEvents="none" accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
        {tags.slice(0, 2).map((t) => (
          <MemoryTag key={t} label={t} tone="primary" />
        ))}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  block: {
    marginBottom: spacing.lg,
    minHeight: layout.minTouch,
  },
  pressed: { opacity: 0.92 },
  hero: {
    width: '100%',
    aspectRatio: 4 / 3,
    backgroundColor: colors.surface,
    borderRadius: 8,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  heroImage: { width: '100%', height: '100%' },
  heroPlaceholder: { fontSize: font.small, color: colors.tertiary },
  weakTime: {
    fontSize: font.small,
    fontWeight: '600',
    color: colors.secondary,
    marginBottom: 4,
  },
  title: { fontSize: 22, fontWeight: '600', color: colors.ink, letterSpacing: -0.1 },
  meta: { fontSize: font.micro, color: colors.tertiary, marginTop: 4 },
  story: { fontSize: font.body, lineHeight: 22, color: colors.secondary, marginTop: spacing.sm },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', marginTop: spacing.sm },
});
