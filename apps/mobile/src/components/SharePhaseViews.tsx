import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors, layout, spacing, type } from '../theme';
import { ShareFlowCancelHeader } from './ShareFlowCancelHeader';

const CTA_RADIUS = 12;
const PREP_RADIUS = 18;

/** Figma 184:2049 — preparing card + status under Cancel. */
export function SharePreparingView({
  cardLabel,
  status,
  onCancel,
}: {
  cardLabel: string;
  status: string;
  onCancel: () => void;
}) {
  return (
    <View style={styles.flex}>
      <ShareFlowCancelHeader onCancel={onCancel} />
      <View style={styles.prepCenter}>
        <View style={styles.prepCard}>
          <View style={styles.prepTop}>
            <View style={styles.prepOrb} />
            <Text style={styles.prepCardLabel}>{cardLabel}</Text>
          </View>
          <View style={styles.prepBottom} />
        </View>
        <Text style={styles.prepStatus}>{status}</Text>
      </View>
    </View>
  );
}

/** Figma 184:2095 / 184:2193 / 184:2262 — title 28, sub 15, CTAs 52×r12. */
export function ShareFailedView({
  title,
  subtitle,
  onRetry,
  onBack,
  children,
}: {
  title: string;
  subtitle: string;
  onRetry: () => void;
  onBack: () => void;
  children?: React.ReactNode;
}) {
  return (
    <View style={styles.flex}>
      <View style={styles.failCenter}>
        <Text style={styles.failTitle}>{title}</Text>
        <Text style={styles.failSub}>{subtitle}</Text>
        {children}
      </View>
      <View style={styles.failFooter}>
        <Pressable style={styles.primary} onPress={onRetry}>
          <Text style={styles.primaryLabel}>Try Again</Text>
        </Pressable>
        <Pressable style={styles.outline} onPress={onBack}>
          <Text style={styles.outlineLabel}>Back</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  prepCenter: {
    flex: 1,
    alignItems: 'center',
    paddingTop: spacing.xxxl,
    paddingHorizontal: layout.gutterDiary,
  },
  prepCard: {
    width: 281,
    maxWidth: '100%',
    aspectRatio: 281 / 352,
    borderRadius: PREP_RADIUS,
    overflow: 'hidden',
    backgroundColor: colors.card,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.divider,
  },
  prepTop: {
    flex: 1.2,
    margin: spacing.md,
    marginBottom: 0,
    borderRadius: 10,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  prepOrb: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#E2DED6',
  },
  prepCardLabel: { ...type.caption, color: colors.secondary },
  prepBottom: { flex: 0.8, backgroundColor: colors.card },
  prepStatus: {
    fontSize: 20,
    lineHeight: 26,
    fontWeight: '500',
    color: colors.ink,
    marginTop: spacing.xl,
    textAlign: 'center',
    paddingHorizontal: spacing.md,
  },
  failCenter: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: layout.gutterDiary,
    alignItems: 'center',
  },
  failTitle: {
    fontSize: 28,
    lineHeight: 34,
    fontWeight: '600',
    letterSpacing: -0.2,
    color: colors.ink,
    textAlign: 'center',
  },
  failSub: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.secondary,
    textAlign: 'center',
    marginTop: spacing.sm,
  },
  failFooter: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.lg,
    gap: spacing.md,
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
});
