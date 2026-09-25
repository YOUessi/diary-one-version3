import React from 'react';
import { Text, StyleSheet, ScrollView, Linking, Pressable, View } from 'react-native';
import { useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FigmaBackHeader } from '../../components/FigmaBackHeader';
import { colors, font, layout, spacing } from '../../theme';
import type { AccountStackParamList } from '../../navigation/types';
import { helpTopicById } from './helpContent';
import { HARDWARE_BASICS } from '../onboarding/hardwareBasicsContent';

type Route = RouteProp<AccountStackParamList, 'HelpTopic'>;

export default function HelpTopicScreen() {
  const { topicId } = useRoute<Route>().params;
  const topic = helpTopicById(topicId);

  if (!topic) {
    return (
      <SafeAreaView style={styles.safe}>
        <Text>Topic not found.</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FigmaBackHeader />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>{topic.title}</Text>
        <Text style={styles.body}>{topic.body}</Text>
        {topicId === 'device_basics' ? (
          <View style={styles.steps}>
            {HARDWARE_BASICS.map((step) => (
              <View key={step.index} style={styles.step}>
                <Text style={styles.stepEyebrow}>{step.eyebrow}</Text>
                <Text style={styles.stepTitle}>{step.title}</Text>
                <Text style={styles.stepLead}>{step.lead}</Text>
              </View>
            ))}
          </View>
        ) : null}
        {topicId === 'contact' || topicId === 'feedback' || topicId === 'report' ? (
          <Pressable
            onPress={() =>
              Linking.openURL(
                `mailto:support@diary.one?subject=${encodeURIComponent(`Diary One — ${topic.title}`)}`,
              )
            }
          >
            <Text style={styles.link}>Email support</Text>
          </Pressable>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  scroll: { paddingHorizontal: layout.gutterDiary, paddingBottom: spacing.xl },
  title: { fontSize: 28, fontWeight: '600', color: colors.ink, marginBottom: spacing.md },
  body: { fontSize: font.body, lineHeight: 24, color: colors.secondary },
  link: { marginTop: spacing.lg, fontSize: font.body, fontWeight: '600', color: colors.accent },
  steps: { marginTop: spacing.lg, gap: spacing.lg },
  step: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.divider, paddingTop: spacing.md },
  stepEyebrow: { fontSize: font.micro, fontWeight: '600', color: colors.tertiary, marginBottom: 4 },
  stepTitle: { fontSize: font.body, fontWeight: '600', color: colors.ink, marginBottom: 4 },
  stepLead: { fontSize: font.small, color: colors.secondary, lineHeight: 20 },
});
