import React from 'react';
import { View, StyleSheet } from 'react-native';
import { colors } from '../theme';
import type { TagCategoryId } from '../onboarding/tagLibrary';

/** Line icons for Preference survey category tiles (Figma 2145). */
export function SurveyCategoryIcon({ id, size = 28 }: { id: TagCategoryId; size?: number }) {
  const s = size;
  switch (id) {
    case 'daily_life':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.cup, { width: s * 0.55, height: s * 0.45, borderRadius: 3 }]} />
          <View style={[styles.cupHandle, { width: s * 0.18, height: s * 0.22, right: s * 0.12, top: s * 0.28 }]} />
          <View style={[styles.saucer, { width: s * 0.72, height: 3, bottom: s * 0.12 }]} />
        </View>
      );
    case 'personal_growth':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.stem, { height: s * 0.45, width: 2, bottom: s * 0.1 }]} />
          <View style={[styles.leaf, { width: s * 0.34, height: s * 0.22, left: s * 0.12, top: s * 0.22, transform: [{ rotate: '-35deg' }] }]} />
          <View style={[styles.leaf, { width: s * 0.34, height: s * 0.22, right: s * 0.12, top: s * 0.18, transform: [{ rotate: '35deg' }] }]} />
        </View>
      );
    case 'emotional':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.bubble, { width: s * 0.72, height: s * 0.55, borderRadius: s * 0.28, top: s * 0.12 }]} />
          <View style={[styles.dot, { width: 3, height: 3, left: s * 0.28, top: s * 0.32 }]} />
          <View style={[styles.dot, { width: 3, height: 3, left: s * 0.42, top: s * 0.32 }]} />
          <View style={[styles.dot, { width: 3, height: 3, left: s * 0.56, top: s * 0.32 }]} />
        </View>
      );
    case 'travel':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.planeBody, { width: s * 0.7, height: 3, top: s * 0.45 }]} />
          <View style={[styles.planeWing, { width: s * 0.45, height: 3, top: s * 0.38, transform: [{ rotate: '25deg' }] }]} />
          <View style={[styles.planeWing, { width: s * 0.28, height: 3, top: s * 0.52, left: s * 0.2, transform: [{ rotate: '-30deg' }] }]} />
        </View>
      );
    case 'relationships':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.head, { width: s * 0.28, height: s * 0.28, left: s * 0.18, top: s * 0.18 }]} />
          <View style={[styles.head, { width: s * 0.28, height: s * 0.28, right: s * 0.18, top: s * 0.18 }]} />
          <View style={[styles.shoulder, { width: s * 0.38, height: s * 0.22, left: s * 0.1, bottom: s * 0.14, borderTopLeftRadius: 10, borderTopRightRadius: 10 }]} />
          <View style={[styles.shoulder, { width: s * 0.38, height: s * 0.22, right: s * 0.1, bottom: s * 0.14, borderTopLeftRadius: 10, borderTopRightRadius: 10 }]} />
        </View>
      );
    case 'work_study':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.brief, { width: s * 0.7, height: s * 0.5, borderRadius: 3, top: s * 0.28 }]} />
          <View style={[styles.briefHandle, { width: s * 0.28, height: s * 0.16, top: s * 0.16 }]} />
        </View>
      );
    case 'health':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.runBody, { width: 3, height: s * 0.35, top: s * 0.22, left: s * 0.42, transform: [{ rotate: '12deg' }] }]} />
          <View style={[styles.head, { width: s * 0.22, height: s * 0.22, top: s * 0.08, left: s * 0.38 }]} />
          <View style={[styles.runBody, { width: s * 0.32, height: 3, top: s * 0.55, left: s * 0.18, transform: [{ rotate: '-25deg' }] }]} />
          <View style={[styles.runBody, { width: s * 0.32, height: 3, top: s * 0.62, left: s * 0.42, transform: [{ rotate: '35deg' }] }]} />
        </View>
      );
    case 'hobbies':
      return (
        <View style={[styles.box, { width: s, height: s }]}>
          <View style={[styles.palette, { width: s * 0.7, height: s * 0.55, borderRadius: s * 0.35, top: s * 0.22 }]} />
          <View style={[styles.dotAccent, { width: 5, height: 5, left: s * 0.28, top: s * 0.35 }]} />
          <View style={[styles.dot, { width: 5, height: 5, left: s * 0.48, top: s * 0.32 }]} />
          <View style={[styles.dot, { width: 5, height: 5, left: s * 0.4, top: s * 0.48 }]} />
        </View>
      );
    default:
      return <View style={[styles.box, { width: s, height: s }]} />;
  }
}

export function SurveyCheckMark({ size = 22 }: { size?: number }) {
  return (
    <View style={[styles.checkWrap, { width: size, height: size, borderRadius: size / 2 }]}>
      <View style={[styles.checkStem, { width: size * 0.18, height: size * 0.42, left: size * 0.42, top: size * 0.22 }]} />
      <View style={[styles.checkArm, { width: size * 0.28, height: size * 0.14, left: size * 0.22, top: size * 0.48, transform: [{ rotate: '-45deg' }] }]} />
    </View>
  );
}

const stroke = colors.ink;

const styles = StyleSheet.create({
  box: { position: 'relative', alignItems: 'center', justifyContent: 'center' },
  cup: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    backgroundColor: 'transparent',
    top: '28%',
  },
  cupHandle: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    borderLeftWidth: 0,
    borderRadius: 4,
  },
  saucer: {
    position: 'absolute',
    backgroundColor: stroke,
    borderRadius: 1,
  },
  stem: {
    position: 'absolute',
    backgroundColor: stroke,
    borderRadius: 1,
  },
  leaf: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    borderRadius: 10,
    backgroundColor: 'transparent',
  },
  bubble: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    backgroundColor: 'transparent',
  },
  dot: {
    position: 'absolute',
    borderRadius: 2,
    backgroundColor: stroke,
  },
  dotAccent: {
    position: 'absolute',
    borderRadius: 3,
    backgroundColor: colors.accent,
  },
  planeBody: {
    position: 'absolute',
    backgroundColor: stroke,
    borderRadius: 1,
  },
  planeWing: {
    position: 'absolute',
    backgroundColor: stroke,
    borderRadius: 1,
  },
  head: {
    position: 'absolute',
    borderRadius: 99,
    borderWidth: 1.6,
    borderColor: stroke,
    backgroundColor: 'transparent',
  },
  shoulder: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    borderBottomWidth: 0,
    backgroundColor: 'transparent',
  },
  brief: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    backgroundColor: 'transparent',
  },
  briefHandle: {
    position: 'absolute',
    borderWidth: 1.6,
    borderTopLeftRadius: 6,
    borderTopRightRadius: 6,
    borderBottomWidth: 0,
    borderColor: stroke,
    backgroundColor: 'transparent',
  },
  runBody: {
    position: 'absolute',
    backgroundColor: stroke,
    borderRadius: 1,
  },
  palette: {
    position: 'absolute',
    borderWidth: 1.6,
    borderColor: stroke,
    backgroundColor: 'transparent',
  },
  checkWrap: {
    backgroundColor: colors.accentSoft,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  checkStem: {
    position: 'absolute',
    backgroundColor: colors.accent,
    borderRadius: 1,
    transform: [{ rotate: '40deg' }],
  },
  checkArm: {
    position: 'absolute',
    backgroundColor: colors.accent,
    borderRadius: 1,
  },
});
