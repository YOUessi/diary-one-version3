import React, { type ReactNode } from 'react';
import { View, Text, StyleSheet } from 'react-native';

import { colors, font, layout, spacing } from '../theme';



/** Figma 主 Tab 顶栏：大标题 + 可选右侧操作（如 Search）。 */

export function FigmaScreenHeader({

  title,

  rightAccessory,

}: {

  title: string;

  rightAccessory?: ReactNode;

}) {

  return (

    <View style={styles.row}>

      <Text style={styles.title}>{title}</Text>

      {rightAccessory ? <View style={styles.right}>{rightAccessory}</View> : null}

    </View>

  );

}



export function FigmaEyebrow({ children }: { children: string }) {

  return <Text style={styles.eyebrow}>{children}</Text>;

}



const styles = StyleSheet.create({

  row: {

    flexDirection: 'row',

    alignItems: 'center',

    justifyContent: 'space-between',

    paddingRight: layout.gutterDiary,

  },

  title: {

    flex: 1,

    fontSize: font.title,

    fontWeight: '700',

    color: colors.ink,

    letterSpacing: 0.2,

    paddingHorizontal: layout.gutterDiary,

    paddingTop: spacing.md,

    paddingBottom: spacing.sm,

  },

  right: { paddingTop: spacing.md, paddingBottom: spacing.sm },

  eyebrow: {

    fontSize: font.micro,

    fontWeight: '600',

    color: colors.secondary,

    letterSpacing: 0.8,

    textTransform: 'uppercase',

    paddingHorizontal: layout.gutterDiary,

    marginTop: spacing.lg,

    marginBottom: spacing.xs,

  },

});


