import React from 'react';
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, spacing, type } from '../theme';

type Props = {
  /** Figma Preview heading — 28/600 (184:2067). */
  heading: string;
  title: string;
  dateLabel?: string;
  body?: string;
  imageUri?: string | null;
  media?: React.ReactNode;
  imageAspectRatio?: number;
  captionBelowCard?: string;
  onBack: () => void;
  onShare: () => void;
  onSave: () => void;
  onTryAnother: () => void;
};

/**
 * Figma 184:2067 / 184:2166 — metrics from share_nodes.json:
 * heading 28, canvas r16, media r10, CTAs 52×r12, Try another 16 secondary.
 */
export function SharePreviewShell({
  heading,
  title,
  dateLabel,
  body,
  imageUri,
  media,
  imageAspectRatio = 4 / 5,
  captionBelowCard,
  onBack,
  onShare,
  onSave,
  onTryAnother,
}: Props) {
  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <View style={styles.nav}>
        <Pressable onPress={onBack} style={styles.backHit} hitSlop={12} accessibilityLabel="Back">
          <Text style={styles.backText}>‹</Text>
        </Pressable>
        <Text style={styles.navTitle} numberOfLines={1}>
          {heading}
        </Text>
        <View style={styles.navSpacer} />
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.card}>
          {media ? (
            <View style={styles.mediaSlot}>{media}</View>
          ) : imageUri ? (
            <Image
              source={{ uri: imageUri }}
              style={[styles.cardImage, { aspectRatio: imageAspectRatio }]}
              resizeMode="cover"
            />
          ) : (
            <View style={[styles.cardImage, styles.cardImageEmpty, { aspectRatio: imageAspectRatio }]} />
          )}
          <View style={styles.cardCopy}>
            <Text style={styles.cardTitle}>{title}</Text>
            {dateLabel ? <Text style={styles.cardDate}>{dateLabel}</Text> : null}
            {body ? <Text style={styles.cardBody}>{body}</Text> : null}
          </View>
        </View>
        {captionBelowCard ? <Text style={styles.caption}>{captionBelowCard}</Text> : null}
      </ScrollView>

      <View style={styles.actions}>
        <Pressable style={styles.primary} onPress={onShare}>
          <Text style={styles.primaryLabel}>Share</Text>
        </Pressable>
        <Pressable style={styles.outline} onPress={onSave}>
          <Text style={styles.outlineLabel}>Save to Photos</Text>
        </Pressable>
        <Pressable onPress={onTryAnother} style={styles.tryHit} hitSlop={8}>
          <Text style={styles.tryAnother}>Try another</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const CTA_RADIUS = 12;
const CANVAS_RADIUS = 16;
const MEDIA_RADIUS = 10;

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  nav: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    minHeight: 44,
  },
  backHit: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300', marginTop: -2 },
  navTitle: {
    flex: 1,
    textAlign: 'center',
    fontSize: 28,
    lineHeight: 34,
    fontWeight: '600',
    letterSpacing: -0.2,
    color: colors.ink,
  },
  navSpacer: { width: 44 },
  scroll: { flex: 1 },
  scrollContent: {
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.md,
    paddingBottom: spacing.md,
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: CANVAS_RADIUS,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.divider,
    overflow: 'hidden',
    padding: spacing.md,
  },
  mediaSlot: {
    borderRadius: MEDIA_RADIUS,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  cardImage: {
    width: '100%',
    borderRadius: MEDIA_RADIUS,
    backgroundColor: colors.surface,
  },
  cardImageEmpty: { minHeight: 160 },
  cardCopy: { marginTop: spacing.md, gap: 4 },
  cardTitle: { ...type.titleChapter, color: colors.ink },
  cardDate: { fontSize: 12, lineHeight: 16, color: colors.tertiary },
  cardBody: { fontSize: 15, lineHeight: 22, color: colors.secondary, marginTop: spacing.xs },
  caption: {
    fontSize: 15,
    lineHeight: 20,
    color: colors.secondary,
    marginTop: spacing.md,
    textAlign: 'center',
  },
  actions: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.lg,
    gap: spacing.sm,
  },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: CTA_RADIUS,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryLabel: { ...type.bodyStory, color: colors.paper, fontWeight: '600' },
  outline: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: CTA_RADIUS,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.card,
  },
  outlineLabel: { ...type.bodyStory, color: colors.ink, fontWeight: '600' },
  tryHit: { minHeight: 44, alignItems: 'center', justifyContent: 'center' },
  tryAnother: {
    fontSize: 16,
    lineHeight: 22,
    color: colors.secondary,
    fontWeight: '500',
    textAlign: 'center',
  },
});
