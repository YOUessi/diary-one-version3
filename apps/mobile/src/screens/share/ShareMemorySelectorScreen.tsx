import React from 'react';

import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useNavigation, useRoute } from '@react-navigation/native';

import type { RouteProp } from '@react-navigation/native';

import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { SafeAreaView } from 'react-native-safe-area-context';

import { colors, font, layout, radius, spacing } from '../../theme';

import type { DiaryStackParamList } from '../../navigation/types';



type Route = RouteProp<DiaryStackParamList, 'ShareMemorySelector'>;

type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ShareMemorySelector'>;



/** Figma 184:1976 — options sheet over chapter detail (chapter stays visible below). */

export default function ShareMemorySelectorScreen() {

  const { chapterId } = useRoute<Route>().params;

  const navigation = useNavigation<Nav>();



  const close = () => navigation.goBack();



  return (

    <View style={styles.root}>

      <Pressable style={styles.dim} onPress={close} accessibilityLabel="Dismiss share options" />

      <SafeAreaView edges={['bottom']} style={styles.sheet}>

        <View style={styles.handleRow}>

          <Text style={styles.sheetTitle}>Share memory</Text>

          <Pressable onPress={close} hitSlop={12} accessibilityLabel="Close">

            <Text style={styles.close}>×</Text>

          </Pressable>

        </View>



        <Pressable

          style={styles.option}

          onPress={() =>

            navigation.replace('PhotoCollageFlow', { chapterId, phase: 'preparing' })

          }

        >

          <Text style={styles.optionTitle}>Photo collage</Text>

          <Text style={styles.optionBody}>A clean layout using moments from this memory.</Text>

        </Pressable>

        <Pressable

          style={styles.option}

          onPress={() =>

            navigation.replace('IllustratedShareFlow', { chapterId, phase: 'picker' })

          }

        >

          <Text style={styles.optionTitle}>Illustrated memory</Text>

          <Text style={styles.optionBody}>A stylized version created from this memory.</Text>

        </Pressable>

      </SafeAreaView>

    </View>

  );

}



const styles = StyleSheet.create({

  root: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'transparent' },

  dim: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(0,0,0,0.35)' },

  sheet: {

    backgroundColor: colors.paper,

    borderTopLeftRadius: radius.card,

    borderTopRightRadius: radius.card,

    paddingHorizontal: layout.gutterDiary,

    paddingTop: spacing.md,

    paddingBottom: spacing.lg,

  },

  handleRow: {

    flexDirection: 'row',

    justifyContent: 'space-between',

    alignItems: 'center',

    marginBottom: spacing.md,

  },

  sheetTitle: { fontSize: font.body, fontWeight: '700', color: colors.ink },

  close: { fontSize: 28, color: colors.ink, fontWeight: '300' },

  option: {

    borderWidth: 1,

    borderColor: colors.divider,

    borderRadius: radius.control,

    padding: spacing.md,

    marginBottom: spacing.md,

  },

  optionTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink, marginBottom: 4 },

  optionBody: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },

});


