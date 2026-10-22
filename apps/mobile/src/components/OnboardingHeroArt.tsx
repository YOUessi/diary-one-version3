import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../theme';

type ArtKind =
  | 'wear'
  | 'power'
  | 'capture_modes'
  | 'double_tap'
  | 'angle'
  | 'auto'
  | 'pipeline'
  | 'pair'
  | 'found'
  | 'connecting'
  | 'connected'
  | 'searching';

/** Abstract hardware / flow illustrations for onboarding (replaces text placeholders). */
export function OnboardingHeroArt({ kind }: { kind: ArtKind }) {
  return (
    <View style={styles.frame} accessibilityElementsHidden>
      {kind === 'wear' || kind === 'pair' || kind === 'found' || kind === 'connected' ? (
        <DeviceSilhouette accent={kind === 'connected' || kind === 'found'} />
      ) : null}
      {kind === 'power' ? <PowerBars /> : null}
      {kind === 'capture_modes' ? <ModeWheel /> : null}
      {kind === 'double_tap' ? <TapTarget /> : null}
      {kind === 'angle' ? <AngleDial /> : null}
      {kind === 'auto' ? <PulseDots /> : null}
      {kind === 'pipeline' ? <PipelineSteps /> : null}
      {kind === 'searching' || kind === 'connecting' ? <RadarRing active={kind === 'connecting'} /> : null}
    </View>
  );
}

function DeviceSilhouette({ accent }: { accent?: boolean }) {
  return (
    <View style={styles.deviceWrap}>
      <View style={[styles.deviceDisc, accent && styles.deviceDiscOn]}>
        <View style={styles.deviceStem} />
        <View style={[styles.deviceLens, accent && styles.deviceLensOn]}>
          <View style={styles.deviceLensCore} />
        </View>
      </View>
    </View>
  );
}

function PowerBars() {
  return (
    <View style={styles.rowCenter}>
      <View style={styles.powerBtn} />
      <View style={styles.volCol}>
        <View style={styles.volBtn} />
        <View style={styles.volBtn} />
      </View>
    </View>
  );
}

function ModeWheel() {
  return (
    <View style={styles.wheel}>
      <View style={[styles.wheelSeg, styles.wheelSegOn]} />
      <View style={styles.wheelSeg} />
      <View style={styles.wheelSeg} />
      <View style={styles.wheelHub} />
    </View>
  );
}

function TapTarget() {
  return (
    <View style={styles.tapOuter}>
      <View style={styles.tapMid}>
        <View style={styles.tapInner} />
      </View>
    </View>
  );
}

function AngleDial() {
  return (
    <View style={styles.dial}>
      <View style={styles.dialTick} />
      <View style={[styles.dialTick, { transform: [{ rotate: '-15deg' }] }]} />
      <View style={[styles.dialTick, { transform: [{ rotate: '90deg' }] }]} />
      <View style={styles.dialKnob} />
    </View>
  );
}

function PulseDots() {
  return (
    <View style={styles.pulseRow}>
      <View style={[styles.pulse, styles.pulseA]} />
      <View style={[styles.pulse, styles.pulseB]} />
      <View style={[styles.pulse, styles.pulseC]} />
    </View>
  );
}

function PipelineSteps() {
  return (
    <View style={styles.pipeRow}>
      {['Sync', 'Understand', 'Remember'].map((label, i) => (
        <React.Fragment key={label}>
          <View style={styles.pipeNode}>
            <View style={[styles.pipeDot, i === 2 && styles.pipeDotOn]} />
          </View>
          {i < 2 ? <View style={styles.pipeLine} /> : null}
        </React.Fragment>
      ))}
    </View>
  );
}

function RadarRing({ active }: { active?: boolean }) {
  return (
    <View style={styles.radar}>
      <View style={[styles.radarRing, styles.radarRingLg]} />
      <View style={[styles.radarRing, styles.radarRingMd]} />
      <View style={[styles.radarCore, active && styles.radarCoreOn]} />
    </View>
  );
}

const styles = StyleSheet.create({
  frame: {
    minHeight: 188,
    width: '100%',
    backgroundColor: 'transparent',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  deviceWrap: { alignItems: 'center', justifyContent: 'center' },
  deviceDisc: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: colors.card,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 10,
  },
  deviceDiscOn: { borderWidth: 2, borderColor: colors.accentSoft },
  deviceStem: {
    width: 3,
    height: 32,
    borderRadius: 2,
    backgroundColor: colors.secondary,
    opacity: 0.55,
  },
  deviceLens: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.secondary,
    opacity: 0.75,
    alignItems: 'center',
    justifyContent: 'center',
  },
  deviceLensOn: { backgroundColor: colors.accent, opacity: 0.9 },
  deviceLensCore: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: colors.ink,
    opacity: 0.45,
  },
  rowCenter: { flexDirection: 'row', alignItems: 'center', gap: 28 },
  powerBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 2,
    borderColor: colors.ink,
  },
  volCol: { gap: 10 },
  volBtn: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: colors.ink,
    opacity: 0.85,
  },
  wheel: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 8,
    borderColor: colors.divider,
    alignItems: 'center',
    justifyContent: 'center',
  },
  wheelSeg: {
    position: 'absolute',
    width: 14,
    height: 28,
    borderRadius: 7,
    backgroundColor: colors.divider,
    top: 12,
  },
  wheelSegOn: { backgroundColor: colors.accent },
  wheelHub: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.ink,
  },
  tapOuter: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: colors.accentSoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tapMid: {
    width: 78,
    height: 78,
    borderRadius: 39,
    borderWidth: 2,
    borderColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tapInner: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.ink,
  },
  dial: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: colors.divider,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dialTick: {
    position: 'absolute',
    width: 4,
    height: 28,
    borderRadius: 2,
    backgroundColor: colors.ink,
    top: 10,
  },
  dialKnob: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.accent,
  },
  pulseRow: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  pulse: { width: 18, height: 18, borderRadius: 9, backgroundColor: colors.accent },
  pulseA: { opacity: 1 },
  pulseB: { opacity: 0.55, transform: [{ scale: 1.25 }] },
  pulseC: { opacity: 0.28, transform: [{ scale: 1.55 }] },
  pipeRow: { flexDirection: 'row', alignItems: 'center' },
  pipeNode: { alignItems: 'center' },
  pipeDot: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: colors.divider,
  },
  pipeDotOn: { backgroundColor: colors.accent },
  pipeLine: { width: 36, height: 2, backgroundColor: colors.divider },
  radar: { width: 140, height: 140, alignItems: 'center', justifyContent: 'center' },
  radarRing: {
    position: 'absolute',
    borderWidth: 1.5,
    borderColor: colors.divider,
    borderRadius: 999,
  },
  radarRingLg: { width: 130, height: 130 },
  radarRingMd: { width: 86, height: 86 },
  radarCore: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.secondary,
  },
  radarCoreOn: { backgroundColor: colors.accent },
});
