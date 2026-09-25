import React from 'react';
import { View, Text, Pressable, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from './FigmaBackHeader';
import { colors, font, layout, radius, spacing } from '../theme';

type Props = {
  eyebrow?: string;
  title: string;
  lead?: string;
  visualHint?: string;
  calloutTitle?: string;
  calloutBody?: string;
  primaryLabel?: string;
  onPrimary?: () => void;
  primaryDisabled?: boolean;
  secondaryLabel?: string;
  onSecondary?: () => void;
  showBack?: boolean;
  onBack?: () => void;
  children?: React.ReactNode;
};

export function OnboardingScaffold({
  eyebrow,
  title,
  lead,
  visualHint,
  calloutTitle,
  calloutBody,
  primaryLabel,
  onPrimary,
  primaryDisabled,
  secondaryLabel,
  onSecondary,
  showBack = true,
  onBack,
  children,
}: Props) {
  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      {showBack ? <FigmaBackHeader eyebrow={eyebrow} onBack={onBack} /> : eyebrow ? (
        <Text style={styles.eyebrowOnly}>{eyebrow}</Text>
      ) : null}
      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>{title}</Text>
        {lead ? <Text style={styles.lead}>{lead}</Text> : null}
        {visualHint ? (
          <View style={styles.visual}>
            <Text style={styles.visualText}>{visualHint}</Text>
          </View>
        ) : null}
        {calloutTitle || calloutBody ? (
          <View style={styles.callout}>
            {calloutTitle ? <Text style={styles.calloutTitle}>{calloutTitle}</Text> : null}
            {calloutBody ? <Text style={styles.calloutBody}>{calloutBody}</Text> : null}
          </View>
        ) : null}
        {children}
      </ScrollView>
      {(primaryLabel && onPrimary) || (secondaryLabel && onSecondary) ? (
        <View style={styles.footer}>
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
              <Text style={styles.secondaryLabel}>{secondaryLabel}</Text>
            </Pressable>
          ) : null}
        </View>
      ) : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  eyebrowOnly: {
    fontSize: font.micro,
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
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: colors.ink,
    letterSpacing: -0.3,
    marginBottom: spacing.sm,
  },
  lead: { fontSize: font.body, color: colors.secondary, lineHeight: 24, marginBottom: spacing.lg },
  visual: {
    minHeight: 200,
    backgroundColor: colors.surface,
    borderRadius: radius.control,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    padding: spacing.md,
  },
  visualText: { fontSize: font.small, color: colors.tertiary, textAlign: 'center' },
  callout: {
    borderLeftWidth: 3,
    borderLeftColor: colors.divider,
    paddingLeft: spacing.md,
    marginBottom: spacing.lg,
  },
  calloutTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink, marginBottom: 4 },
  calloutBody: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
  footer: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.md, gap: spacing.sm },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: radius.pill,
    minHeight: layout.buttonHeight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryDisabled: { opacity: 0.45 },
  primaryLabel: { color: colors.paper, fontWeight: '700', fontSize: font.body },
  secondary: {
    minHeight: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryLabel: { color: colors.accent, fontWeight: '600', fontSize: font.body },
});
