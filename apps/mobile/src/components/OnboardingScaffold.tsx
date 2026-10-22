import React, { type ReactNode } from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from './FigmaBackHeader';
import { colors, layout, spacing, type } from '../theme';

type Props = {
  eyebrow?: string;
  title: string;
  /** Pairing/Setup Complete = 34; Permissions = 28 */
  titleSize?: 'large' | 'section';
  lead?: string;
  /** Prefer ReactNode illustrations over plain visualHint text. */
  visual?: ReactNode;
  visualHint?: string;
  calloutTitle?: string;
  calloutBody?: string;
  /** Figma permission boards use a white system-prompt card. */
  calloutVariant?: 'rail' | 'prompt';
  primaryLabel?: string;
  onPrimary?: () => void;
  primaryDisabled?: boolean;
  secondaryLabel?: string;
  onSecondary?: () => void;
  /** muted = Figma secondary caption (Pairing soft path); accent = warm link */
  secondaryTone?: 'muted' | 'accent';
  /**
   * Figma Pairing stacks CTA under the hardware slot (gap 18).
   * footer = sticky bottom (permissions / default).
   */
  ctaPlacement?: 'footer' | 'content';
  showBack?: boolean;
  onBack?: () => void;
  /** Pairing Searching/Connecting — Cancel in header (Figma). */
  headerLeading?: 'back' | 'cancel';
  children?: React.ReactNode;
};

export function OnboardingScaffold({
  eyebrow,
  title,
  titleSize = 'large',
  lead,
  visual,
  visualHint,
  calloutTitle,
  calloutBody,
  calloutVariant = 'rail',
  primaryLabel,
  onPrimary,
  primaryDisabled,
  secondaryLabel,
  onSecondary,
  secondaryTone = 'accent',
  ctaPlacement = 'footer',
  showBack = true,
  onBack,
  headerLeading = 'back',
  children,
}: Props) {
  const hasCta = Boolean(
    (primaryLabel && onPrimary) || (secondaryLabel && onSecondary),
  );

  const ctaBlock =
    hasCta ? (
      <View style={ctaPlacement === 'content' ? styles.ctaInContent : styles.footer}>
        {primaryLabel && onPrimary ? (
          <Pressable
            onPress={onPrimary}
            disabled={primaryDisabled}
            style={[styles.primary, primaryDisabled && styles.primaryDisabled]}
          >
            <Text style={styles.primaryLabel}>{primaryLabel}</Text>
          </Pressable>
        ) : null}
        {secondaryLabel && onSecondary ? (
          <Pressable onPress={onSecondary} style={styles.secondary}>
            <Text
              style={[
                styles.secondaryLabel,
                secondaryTone === 'muted' && styles.secondaryLabelMuted,
              ]}
            >
              {secondaryLabel}
            </Text>
          </Pressable>
        ) : null}
      </View>
    ) : null;

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      {showBack || headerLeading === 'cancel' ? (
        <FigmaBackHeader
          eyebrow={eyebrow}
          onBack={onBack}
          leading={headerLeading}
          backGlyphSize={headerLeading === 'back' ? 22 : undefined}
        />
      ) : eyebrow ? (
        <Text style={styles.eyebrowOnly}>{eyebrow}</Text>
      ) : null}
      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={titleSize === 'section' ? styles.titleSection : styles.title}>{title}</Text>
        {lead ? <Text style={styles.lead}>{lead}</Text> : null}
        {visual ? (
          <>
            <View style={styles.visual}>{visual}</View>
            {visualHint ? <Text style={styles.visualCaption}>{visualHint}</Text> : null}
          </>
        ) : visualHint ? (
          <View style={styles.visual}>
            <Text style={styles.visualText}>{visualHint}</Text>
          </View>
        ) : null}
        {calloutTitle || calloutBody ? (
          <View style={calloutVariant === 'prompt' ? styles.promptCard : styles.callout}>
            {calloutTitle ? (
              <Text style={calloutVariant === 'prompt' ? styles.promptTitle : styles.calloutTitle}>
                {calloutTitle}
              </Text>
            ) : null}
            {calloutBody ? (
              <Text style={calloutVariant === 'prompt' ? styles.promptBody : styles.calloutBody}>
                {calloutBody}
              </Text>
            ) : null}
          </View>
        ) : null}
        {children}
        {ctaPlacement === 'content' ? ctaBlock : null}
      </ScrollView>
      {ctaPlacement === 'footer' ? ctaBlock : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  eyebrowOnly: {
    ...type.metadata,
    fontWeight: '600',
    color: colors.secondary,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    paddingHorizontal: layout.gutterDiary,
    marginBottom: spacing.xs,
  },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.xl,
    flexGrow: 1,
  },
  /** Pairing / Setup Complete — primary titles are 34; stack gap ~18 in Figma */
  title: {
    ...type.titleLarge,
    color: colors.ink,
    marginBottom: 18,
  },
  titleSection: {
    ...type.titleSection,
    color: colors.ink,
    marginBottom: spacing.sm,
  },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: 18 },
  /** Figma Pairing / Setup — hardware placeholder r16 × 220 */
  visual: {
    height: 220,
    backgroundColor: colors.surface,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
    padding: spacing.md,
    overflow: 'hidden',
  },
  visualText: { ...type.caption, color: colors.tertiary, textAlign: 'center' },
  visualCaption: {
    ...type.caption,
    color: colors.tertiary,
    textAlign: 'center',
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  callout: {
    borderLeftWidth: 3,
    borderLeftColor: colors.accent,
    paddingLeft: spacing.md,
    marginBottom: spacing.lg,
  },
  calloutTitle: { ...type.bodyStory, fontWeight: '600', color: colors.ink, marginBottom: 4 },
  calloutBody: { ...type.caption, color: colors.secondary, lineHeight: 20 },
  /** Figma Permissions placeholder card — r16 */
  promptCard: {
    backgroundColor: colors.card,
    borderRadius: 16,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.lg,
    marginTop: spacing.md,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 2,
  },
  promptTitle: {
    ...type.bodyStory,
    fontWeight: '600',
    color: colors.ink,
    textAlign: 'center',
    marginBottom: 4,
  },
  promptBody: { ...type.caption, color: colors.secondary, textAlign: 'center', lineHeight: 20 },
  footer: {
    paddingHorizontal: layout.gutterDiary,
    paddingTop: spacing.sm,
    paddingBottom: spacing.lg,
    gap: spacing.sm,
  },
  /** Figma Pairing — CTA sits in content stack under hardware slot */
  ctaInContent: {
    gap: 10,
    marginTop: 0,
    marginBottom: spacing.md,
  },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryDisabled: { opacity: 0.45 },
  primaryLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
  secondary: {
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryLabel: { ...type.bodyStory, color: colors.accent, fontWeight: '600' },
  secondaryLabelMuted: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.secondary,
  },
});
