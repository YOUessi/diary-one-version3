import React from 'react';

import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useNavigation, useRoute } from '@react-navigation/native';

import type { RouteProp } from '@react-navigation/native';

import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { SafeAreaView } from 'react-native-safe-area-context';

import { formatShortDay } from '../../domain/formatMedia';

import { colors, font, layout, radius, spacing } from '../../theme';

import { chaptersForDate, useAppStore } from '../../store/useAppStore';

import type { DiaryStackParamList } from '../../navigation/types';



type Route = RouteProp<DiaryStackParamList, 'ShareDaySelector'>;

type Nav = NativeStackNavigationProp<DiaryStackParamList, 'ShareDaySelector'>;



export default function ShareDaySelectorScreen() {

  const { dateKey } = useRoute<Route>().params;

  const navigation = useNavigation<Nav>();

  const chapters = useAppStore((s) => chaptersForDate(s.chapters, dateKey));



  const close = () => navigation.goBack();



  return (

    <View style={styles.root}>

      <Pressable style={styles.dim} onPress={close} accessibilityLabel="Dismiss share day" />

      <SafeAreaView edges={['bottom']} style={styles.sheet}>

        <View style={styles.handleRow}>

          <Text style={styles.sheetTitle}>Share day</Text>

          <Pressable onPress={close} hitSlop={12}>

            <Text style={styles.close}>×</Text>

          </Pressable>

        </View>

        <Text style={styles.dateTitle}>{formatShortDay(dateKey)}</Text>

        <Text style={styles.meta}>

          {chapters.length} {chapters.length === 1 ? 'memory' : 'memories'} on this day

        </Text>



        <Pressable

          style={styles.option}

          onPress={() =>

            navigation.replace('DailyRecapFlow', { dateKey, phase: 'preparing' })

          }

        >

          <Text style={styles.optionTitle}>Daily Recap</Text>

          <Text style={styles.optionBody}>A 9:16 video-style recap of your day.</Text>

        </Pressable>

        <Pressable

          style={styles.option}

          onPress={() =>

            navigation.replace('DayPhotoCollageFlow', { dateKey, phase: 'preparing' })

          }

        >

          <Text style={styles.optionTitle}>Photo collage</Text>

          <Text style={styles.optionBody}>A clean layout using moments from this day.</Text>

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

    marginBottom: spacing.sm,

  },

  sheetTitle: { fontSize: font.body, fontWeight: '700', color: colors.ink },

  close: { fontSize: 28, color: colors.ink, fontWeight: '300' },

  dateTitle: { fontSize: 22, fontWeight: '600', color: colors.ink },

  meta: { fontSize: font.small, color: colors.tertiary, marginBottom: spacing.lg },

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


