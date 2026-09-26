import React, { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { OnboardingScaffold } from '../../components/OnboardingScaffold';
import { colors, font, radius, spacing } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';
import {
  EMPTY_SURVEY_ANSWERS,
  PREFERENCE_SURVEY_STEPS,
  type SurveyAnswers,
} from '../../onboarding/preferenceSurvey';
import {
  applyPreferenceSurveyAndFinish,
  skipPreferenceSurveyAndFinish,
} from '../../onboarding/applyPreferenceSurvey';

type Route = RouteProp<OnboardingStackParamList, 'PreferenceSurvey'>;
type Nav = NativeStackNavigationProp<OnboardingStackParamList, 'PreferenceSurvey'>;

/** Session answers while walking the survey (not persisted mid-flow). */
let sessionAnswers: SurveyAnswers = { ...EMPTY_SURVEY_ANSWERS, selections: {} };

export default function PreferenceSurveyScreen() {
  const { step } = useRoute<Route>().params;
  const navigation = useNavigation<Nav>();
  const page = PREFERENCE_SURVEY_STEPS[step];
  const [answers, setAnswers] = useState<SurveyAnswers>(() => ({
    selections: { ...sessionAnswers.selections },
    openText: sessionAnswers.openText,
  }));

  const selected = answers.selections[page?.id ?? ''] ?? [];
  const canContinue = useMemo(() => {
    if (!page) return false;
    if (page.kind === 'text') return true;
    if (page.kind === 'multi') return selected.length > 0;
    return selected.length === 1;
  }, [page, selected.length]);

  if (!page) {
    navigation.replace('PreferenceSurvey', { step: 0 });
    return null;
  }

  const persistSession = (next: SurveyAnswers) => {
    sessionAnswers = {
      selections: { ...next.selections },
      openText: next.openText,
    };
    setAnswers(next);
  };

  const toggleOption = (optionId: string) => {
    if (page.kind === 'multi') {
      const exclusiveNone = optionId === 'none';
      let next: string[];
      if (exclusiveNone) {
        next = selected.includes('none') ? [] : ['none'];
      } else {
        const withoutNone = selected.filter((id) => id !== 'none');
        next = withoutNone.includes(optionId)
          ? withoutNone.filter((id) => id !== optionId)
          : [...withoutNone, optionId];
      }
      persistSession({
        ...answers,
        selections: { ...answers.selections, [page.id]: next },
      });
      return;
    }
    persistSession({
      ...answers,
      selections: { ...answers.selections, [page.id]: [optionId] },
    });
  };

  const onPrimary = () => {
    sessionAnswers = {
      selections: { ...answers.selections },
      openText: answers.openText,
    };
    if (step >= PREFERENCE_SURVEY_STEPS.length - 1) {
      applyPreferenceSurveyAndFinish(sessionAnswers);
      sessionAnswers = { ...EMPTY_SURVEY_ANSWERS, selections: {} };
      return;
    }
    navigation.push('PreferenceSurvey', { step: step + 1 });
  };

  const onSkipAll = () => {
    sessionAnswers = { ...EMPTY_SURVEY_ANSWERS, selections: {} };
    skipPreferenceSurveyAndFinish();
  };

  const onBack = () => {
    if (step > 0) navigation.goBack();
    else navigation.navigate('SetupComplete');
  };

  const primaryLabel =
    step >= PREFERENCE_SURVEY_STEPS.length - 1 ? 'Finish' : 'Continue';

  return (
    <OnboardingScaffold
      eyebrow={`SETUP · PREFERENCES · ${step + 1}/${PREFERENCE_SURVEY_STEPS.length}`}
      title={page.title}
      lead={page.lead}
      primaryLabel={primaryLabel}
      primaryDisabled={!canContinue}
      onPrimary={onPrimary}
      secondaryLabel="Skip for now"
      onSecondary={onSkipAll}
      onBack={onBack}
    >
      {page.kind === 'text' ? (
        <TextInput
          value={answers.openText}
          onChangeText={(t) =>
            persistSession({ ...answers, openText: t.slice(0, page.maxLength ?? 150) })
          }
          placeholder="What matters most to you?"
          placeholderTextColor={colors.tertiary}
          multiline
          style={styles.textArea}
          maxLength={page.maxLength ?? 150}
        />
      ) : (
        <View style={styles.options}>
          {(page.options ?? []).map((opt) => {
            const on = selected.includes(opt.id);
            return (
              <Pressable
                key={opt.id}
                onPress={() => toggleOption(opt.id)}
                style={[styles.option, on && styles.optionOn]}
                accessibilityRole="button"
                accessibilityState={{ selected: on }}
              >
                <Text style={[styles.optionLabel, on && styles.optionLabelOn]}>{opt.label}</Text>
              </Pressable>
            );
          })}
        </View>
      )}
      {page.kind === 'consent' ? (
        <Text style={styles.footnote}>
          You can change Memory Preferences anytime in Account. Cloud consent is recorded with a
          version for audit — it is separate from signing in.
        </Text>
      ) : null}
    </OnboardingScaffold>
  );
}

const styles = StyleSheet.create({
  options: { gap: spacing.sm, marginBottom: spacing.lg },
  option: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    minHeight: 48,
    justifyContent: 'center',
  },
  optionOn: {
    borderColor: colors.ink,
    backgroundColor: colors.surface,
  },
  optionLabel: { fontSize: font.body, color: colors.ink },
  optionLabelOn: { fontWeight: '600' },
  textArea: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.control,
    padding: spacing.md,
    minHeight: 120,
    fontSize: font.body,
    color: colors.ink,
    textAlignVertical: 'top',
    marginBottom: spacing.md,
  },
  footnote: {
    fontSize: font.micro,
    color: colors.tertiary,
    lineHeight: 18,
    marginTop: spacing.sm,
  },
});
