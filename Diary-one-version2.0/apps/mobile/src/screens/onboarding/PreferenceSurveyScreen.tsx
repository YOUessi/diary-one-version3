import React, { useMemo, useState } from 'react';
import {
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  ScrollView,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, layout, radius, spacing, type } from '../../theme';
import type { OnboardingStackParamList } from '../../navigation/types';
import {
  EMPTY_SURVEY_ANSWERS,
  INTRO_POINTS,
  MOMENT_OPTIONS,
  SHOW_LESS_OPTIONS,
  type QuestionnaireStepId,
  type SurveyAnswers,
  momentById,
  nextQuestionnaireStep,
  showLessChipLabel,
  stageMeta,
  stepIdToIndex,
  stepIndexToId,
  suggestLabelsFromCustom,
  SURVEY_OPEN_TEXT_MAX,
  togglePrefOption,
} from '../../onboarding/preferenceSurvey';
import {
  applyPreferenceSurveyAndFinish,
  applyPreferenceSurveyFromAccount,
  skipPreferenceSurveyAndFinish,
  skipPreferenceSurveyFromAccount,
} from '../../onboarding/applyPreferenceSurvey';
import { LIBRARY_TAGS } from '../../onboarding/tagLibrary';

type SurveyParams = OnboardingStackParamList['PreferenceSurvey'];
type Route = RouteProp<{ PreferenceSurvey: SurveyParams }, 'PreferenceSurvey'>;
type Nav = NativeStackNavigationProp<{ PreferenceSurvey: SurveyParams }>;

let sessionAnswers: SurveyAnswers = { ...EMPTY_SURVEY_ANSWERS };

const MOMENT_CARD_W = (layout.contentWidth - 8) / 2;

function resolveStepId(raw: SurveyParams['step']): QuestionnaireStepId {
  if (typeof raw === 'string' && raw.length) {
    const allowed: QuestionnaireStepId[] = [
      'welcome',
      'moments',
      'custom',
      'custom_review',
      'show_less',
      'summary',
    ];
    if (allowed.includes(raw as QuestionnaireStepId)) return raw as QuestionnaireStepId;
  }
  if (typeof raw === 'number' && Number.isFinite(raw)) return stepIndexToId(raw);
  return 'welcome';
}

function OptionCard({
  label,
  description,
  selected,
  onPress,
  compact,
  width,
}: {
  label: string;
  description: string;
  selected: boolean;
  onPress: () => void;
  compact?: boolean;
  width?: number;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={[
        styles.optionCard,
        compact && styles.optionCardCompact,
        width != null ? { width } : null,
        selected && styles.optionCardOn,
      ]}
      accessibilityRole="button"
      accessibilityState={{ selected }}
    >
      <View style={styles.optionCopy}>
        <Text style={styles.optionLabel}>{label}</Text>
        <Text style={styles.optionDesc}>{description}</Text>
      </View>
      <View style={[styles.check, selected && styles.checkOn]}>
        {selected ? <Text style={styles.checkMark}>✓</Text> : null}
      </View>
    </Pressable>
  );
}

function ChipRow({ labels }: { labels: string[] }) {
  return (
    <View style={styles.chipRow}>
      {labels.map((label) => (
        <View key={label} style={styles.chip}>
          <Text style={styles.chipText}>{label}</Text>
        </View>
      ))}
    </View>
  );
}

export default function PreferenceSurveyScreen() {
  const params = useRoute<Route>().params;
  const stepId = resolveStepId(params?.step);
  const mode = params?.mode === 'account' ? 'account' : 'onboarding';
  const navigation = useNavigation<Nav>();
  const meta = stageMeta(stepId);
  const [answers, setAnswers] = useState<SurveyAnswers>(() => ({
    ...sessionAnswers,
    momentIds: [...sessionAnswers.momentIds],
    showLessIds: [...sessionAnswers.showLessIds],
    suggestedLabels: [...sessionAnswers.suggestedLabels],
  }));
  const [tagSearch, setTagSearch] = useState('');

  const canContinue = useMemo(() => {
    switch (stepId) {
      case 'welcome':
      case 'custom':
      case 'custom_review':
      case 'summary':
        return true;
      case 'moments':
        return answers.momentIds.length > 0;
      case 'show_less':
        return answers.showLessIds.length > 0;
      default:
        return false;
    }
  }, [stepId, answers]);

  const tagHits = useMemo(() => {
    const q = tagSearch.trim().toLowerCase();
    if (q.length < 2) return [];
    return LIBRARY_TAGS.filter((t) => t.label.toLowerCase().includes(q)).slice(0, 8);
  }, [tagSearch]);

  const persist = (next: SurveyAnswers) => {
    sessionAnswers = { ...next };
    setAnswers(next);
  };

  const leaveAccountSurvey = () => {
    sessionAnswers = { ...EMPTY_SURVEY_ANSWERS };
    if (navigation.canGoBack()) {
      navigation.pop(Math.max(1, stepIdToIndex(stepId) + 1));
    }
  };

  const go = (next: QuestionnaireStepId) => {
    navigation.push('PreferenceSurvey', { step: next, mode });
  };

  const onPrimary = () => {
    sessionAnswers = { ...answers };
    if (stepId === 'custom') {
      const fromWords = suggestLabelsFromCustom(answers.customText);
      const merged = [...new Set([...answers.suggestedLabels, ...fromWords])];
      const next = { ...answers, suggestedLabels: merged };
      persist(next);
      sessionAnswers = next;
    }
    const next = nextQuestionnaireStep(stepId, sessionAnswers);
    if (next === 'done') {
      if (mode === 'account') {
        applyPreferenceSurveyFromAccount(sessionAnswers);
        leaveAccountSurvey();
      } else {
        applyPreferenceSurveyAndFinish(sessionAnswers);
        sessionAnswers = { ...EMPTY_SURVEY_ANSWERS };
      }
      return;
    }
    go(next);
  };

  const onSkipAll = () => {
    sessionAnswers = { ...EMPTY_SURVEY_ANSWERS };
    if (mode === 'account') {
      skipPreferenceSurveyFromAccount();
      leaveAccountSurvey();
      return;
    }
    skipPreferenceSurveyAndFinish();
  };

  const onSkipStep = () => {
    if (stepId === 'custom' || stepId === 'custom_review') {
      persist({ ...answers, customText: '', suggestedLabels: [] });
      go('show_less');
      return;
    }
    onSkipAll();
  };

  const onBack = () => {
    if (stepId === 'welcome') {
      if (mode === 'account') {
        leaveAccountSurvey();
        return;
      }
      if (navigation.canGoBack()) navigation.goBack();
      return;
    }
    if (navigation.canGoBack()) navigation.goBack();
  };

  /** Figma “Go back and edit” → return to Moments (stage 1). */
  const onEditFromSummary = () => {
    navigation.navigate('PreferenceSurvey', { step: 'moments', mode });
  };

  const primaryLabel =
    stepId === 'welcome'
      ? 'Get started'
      : stepId === 'custom_review' || stepId === 'summary'
        ? 'Confirm and continue'
        : 'Continue';

  const secondaryLabel =
    stepId === 'welcome'
      ? mode === 'account'
        ? 'Cancel'
        : 'Skip for now'
      : stepId === 'custom' || stepId === 'custom_review'
        ? 'Skip this step'
        : stepId === 'summary'
          ? null
          : 'Skip setup for now';

  /** NOTICE MORE chips — moments only (custom goes to SPECIFIC card). */
  const noticeMoreChips = useMemo(() => {
    if (answers.momentIds.includes('follow_day')) {
      return ['No preference — follow my day'];
    }
    return answers.momentIds
      .filter((id) => id !== 'something_else' && id !== 'follow_day')
      .map((id) => momentById(id)?.label)
      .filter((x): x is string => Boolean(x));
  }, [answers.momentIds]);

  const showLessChips = useMemo(() => {
    if (answers.showLessIds.includes('nothing') || answers.showLessIds.length === 0) {
      return ['Nothing for now'];
    }
    return answers.showLessIds.map((id) => showLessChipLabel(id));
  }, [answers.showLessIds]);

  const specificChips = answers.suggestedLabels;

  const addSuggested = (label: string) => {
    if (answers.suggestedLabels.includes(label)) return;
    persist({
      ...answers,
      suggestedLabels: [...answers.suggestedLabels, label].slice(0, 8),
    });
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      {stepId === 'welcome' ? (
        <>
          <View style={styles.welcomeNav} />
          <View style={styles.welcomeTop} />
        </>
      ) : (
        <View style={styles.topNav}>
          <Text style={styles.stageLabel}>{meta.stageLabel}</Text>
          <Pressable onPress={onBack} hitSlop={12} accessibilityLabel="Back">
            <Text style={styles.backText}>BACK</Text>
          </Pressable>
        </View>
      )}

      {stepId !== 'welcome' ? (
        <View style={styles.segments}>
          {[0, 1, 2].map((i) => (
            <View
              key={i}
              style={[styles.segment, i < meta.filledSegments && styles.segmentOn]}
            />
          ))}
        </View>
      ) : null}

      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {stepId === 'welcome' ? (
          <>
            <Text style={styles.welcomeEyebrow}>WELCOME TO DIARY</Text>
            <View style={styles.welcomeHeadingGap} />
            <View style={styles.welcomeHeadingBlock}>
              <Text style={styles.titleWelcome}>Help Diary get to know you</Text>
              <Text style={styles.leadWelcome}>
                Choose the moments you would like to remember. Diary only works with what was
                actually captured and will not make up anything that did not happen.
              </Text>
            </View>
            <View style={styles.bullets}>
              {INTRO_POINTS.map((line) => (
                <Text key={line} style={styles.bullet}>{`•  ${line}`}</Text>
              ))}
            </View>
          </>
        ) : null}

        {stepId === 'moments' ? (
          <>
            <View style={styles.headingBlock}>
              <Text style={styles.title}>
                Which kinds of moments would you like Diary to notice more?
              </Text>
              <Text style={styles.lead}>
                Choose as many as you like. You can change these anytime.
              </Text>
            </View>
            <View style={styles.momentGrid}>
              {MOMENT_OPTIONS.map((opt) => (
                <OptionCard
                  key={opt.id}
                  width={MOMENT_CARD_W}
                  label={opt.label}
                  description={opt.description}
                  selected={answers.momentIds.includes(opt.id)}
                  onPress={() =>
                    persist({
                      ...answers,
                      momentIds: togglePrefOption(answers.momentIds, opt, MOMENT_OPTIONS),
                    })
                  }
                />
              ))}
            </View>
          </>
        ) : null}

        {stepId === 'custom' ? (
          <>
            <View style={styles.headingBlock}>
              <Text style={styles.title}>Anything else you’d like Diary to remember?</Text>
              <Text style={styles.lead}>
                Add an activity, interest, or place in your own words. You can skip this.
              </Text>
            </View>
            <View style={styles.noteCard}>
              <Text style={styles.noteLabel}>YOUR WORDS (OPTIONAL)</Text>
              <TextInput
                value={answers.customText}
                onChangeText={(t) =>
                  persist({ ...answers, customText: t.slice(0, SURVEY_OPEN_TEXT_MAX) })
                }
                placeholder="e.g. fishing by the water, city walks, or model-building"
                placeholderTextColor={colors.tertiary}
                multiline
                style={styles.noteInput}
                maxLength={SURVEY_OPEN_TEXT_MAX}
              />
            </View>
            <Text style={styles.searchLabel}>OR SEARCH A TAG</Text>
            <TextInput
              value={tagSearch}
              onChangeText={setTagSearch}
              placeholder="Search an activity or place"
              placeholderTextColor={colors.tertiary}
              style={styles.searchInput}
            />
            {tagHits.length ? (
              <View style={[styles.chipRow, styles.tagHits]}>
                {tagHits.map((t) => (
                  <Pressable
                    key={t.id}
                    onPress={() => {
                      addSuggested(t.label);
                      setTagSearch('');
                    }}
                    style={styles.chip}
                  >
                    <Text style={styles.chipText}>{t.label}</Text>
                  </Pressable>
                ))}
              </View>
            ) : null}
            {answers.suggestedLabels.length ? (
              <>
                <Text style={[styles.searchLabel, styles.tagHits]}>ADDED</Text>
                <ChipRow labels={answers.suggestedLabels} />
              </>
            ) : null}
          </>
        ) : null}

        {stepId === 'custom_review' ? (
          <>
            <View style={styles.headingBlock}>
              <Text style={styles.title}>Review what Diary understood</Text>
              <Text style={styles.lead}>
                These are suggestions, not facts from your recordings. You can edit or skip them.
              </Text>
            </View>
            <View style={[styles.noteCard, styles.noteCardReview]}>
              <Text style={styles.noteLabel}>YOUR WORDS</Text>
              <Text style={styles.noteBody}>{answers.customText.trim()}</Text>
            </View>
            <Text style={styles.searchLabel}>SUGGESTED PREFERENCES</Text>
            <ChipRow labels={answers.suggestedLabels} />
          </>
        ) : null}

        {stepId === 'show_less' ? (
          <>
            <View style={styles.headingBlock}>
              <Text style={styles.title}>What would you like to see less often?</Text>
              <Text style={styles.lead}>
                This only makes these moments less likely to become featured memories. It will not
                delete your original content.
              </Text>
            </View>
            <View style={styles.listCol}>
              {SHOW_LESS_OPTIONS.map((opt) => (
                <OptionCard
                  key={opt.id}
                  compact
                  label={opt.label}
                  description={opt.description}
                  selected={answers.showLessIds.includes(opt.id)}
                  onPress={() =>
                    persist({
                      ...answers,
                      showLessIds: togglePrefOption(
                        answers.showLessIds,
                        opt,
                        SHOW_LESS_OPTIONS,
                      ),
                    })
                  }
                />
              ))}
            </View>
          </>
        ) : null}

        {stepId === 'summary' ? (
          <>
            <View style={styles.headingBlock}>
              <Text style={styles.title}>Here is what Diary will look out for</Text>
              <Text style={styles.lead}>
                You can change these preferences anytime in Settings.
              </Text>
            </View>
            <View style={styles.summaryCard}>
              <Text style={styles.summaryEyebrow}>NOTICE MORE</Text>
              <ChipRow
                labels={
                  noticeMoreChips.length ? noticeMoreChips : ['No preference — follow my day']
                }
              />
            </View>
            <View style={[styles.summaryCard, styles.summaryCardGap]}>
              <Text style={[styles.summaryEyebrow, styles.summaryEyebrowMuted]}>
                SHOW LESS OFTEN
              </Text>
              <ChipRow labels={showLessChips} />
            </View>
            {specificChips.length ? (
              <View style={[styles.summaryCard, styles.summaryCardGap]}>
                <Text style={[styles.summaryEyebrow, styles.summaryEyebrowMuted]}>
                  SPECIFIC THINGS YOU ADDED
                </Text>
                <ChipRow labels={specificChips} />
              </View>
            ) : null}
            <Text style={styles.promise}>
              These preferences only affect how your content is selected and presented. Diary only
              uses moments that were actually captured.
            </Text>
            <Pressable onPress={onEditFromSummary} style={styles.editLink}>
              <Text style={styles.editLinkText}>Go back and edit</Text>
            </Pressable>
          </>
        ) : null}
      </ScrollView>

      <View style={styles.footer}>
        <Pressable
          onPress={onPrimary}
          disabled={!canContinue}
          style={[styles.primary, !canContinue && styles.primaryDisabled]}
        >
          <Text style={styles.primaryLabel}>{primaryLabel}</Text>
        </Pressable>
        {secondaryLabel ? (
          <Pressable
            onPress={
              stepId === 'custom' || stepId === 'custom_review' ? onSkipStep : onSkipAll
            }
            style={styles.secondary}
          >
            <Text style={styles.secondaryLabel}>{secondaryLabel}</Text>
          </Pressable>
        ) : (
          <Text style={styles.footerHint}>You can change this anytime in Settings.</Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  /** Figma Welcome: empty Top navigation 22 + Top spacing 54 */
  welcomeNav: { height: 22, marginHorizontal: layout.gutterDiary },
  welcomeTop: { height: 54 },
  /** Figma: Progress spacing 14 + Heading spacing 18 → eyebrow 后间距 */
  welcomeHeadingGap: { height: 32 },
  topNav: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: layout.gutterDiary,
    minHeight: 22,
    marginBottom: 6,
  },
  stageLabel: {
    ...type.metadata,
    color: colors.tertiary,
    textTransform: 'uppercase',
  },
  backText: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.secondary,
  },
  segments: {
    flexDirection: 'row',
    gap: 4,
    paddingHorizontal: layout.gutterDiary,
    marginBottom: 18,
  },
  segment: {
    flex: 1,
    height: 4,
    borderRadius: 999,
    backgroundColor: colors.divider,
  },
  segmentOn: { backgroundColor: colors.ink },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.xl,
    flexGrow: 1,
  },
  welcomeEyebrow: {
    ...type.metadata,
    color: colors.tertiary,
  },
  /** Figma 2174:127 Heading block — title 28 + guidance 16/18, gap 4 */
  welcomeHeadingBlock: {
    gap: 4,
    marginBottom: 0,
  },
  titleWelcome: {
    fontSize: 28,
    lineHeight: 28,
    fontWeight: '600',
    letterSpacing: -0.1,
    color: colors.ink,
  },
  leadWelcome: {
    fontSize: 16,
    lineHeight: 18,
    color: colors.secondary,
  },
  /** Figma 2174:130 What to expect — gap 20 */
  bullets: { gap: 20, marginTop: 0 },
  bullet: { fontSize: 15, lineHeight: 18, color: colors.secondary },
  headingBlock: {
    minHeight: 130,
    marginBottom: spacing.sm,
    gap: 4,
  },
  title: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '600',
    letterSpacing: -0.1,
    color: colors.ink,
  },
  lead: {
    fontSize: 15,
    lineHeight: 18,
    color: colors.secondary,
  },
  momentGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  listCol: { gap: 8 },
  /** Figma Preference Option Card — unselected 1px divider; selected 1.5 ink */
  optionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    height: 112,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.card,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  optionCardCompact: { height: 54, width: '100%' },
  optionCardOn: { borderWidth: 1.5, borderColor: colors.ink },
  optionCopy: { flex: 1, gap: 4 },
  optionLabel: {
    fontSize: 15,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.ink,
  },
  optionDesc: {
    fontSize: 12,
    lineHeight: 14,
    color: colors.secondary,
    letterSpacing: 0.1,
  },
  check: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.divider,
    backgroundColor: colors.card,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkOn: {
    backgroundColor: colors.ink,
    borderColor: colors.ink,
  },
  checkMark: { color: colors.paper, fontSize: 11, lineHeight: 14 },
  noteCard: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.card,
    paddingHorizontal: 14,
    paddingVertical: 12,
    gap: 4,
    marginBottom: 14,
    height: 140,
    backgroundColor: colors.paper,
  },
  noteCardReview: { height: 102 },
  noteLabel: {
    ...type.metadata,
    color: colors.tertiary,
  },
  noteInput: {
    fontSize: 16,
    lineHeight: 23,
    color: colors.ink,
    flex: 1,
    textAlignVertical: 'top',
    padding: 0,
  },
  noteBody: { fontSize: 16, lineHeight: 23, color: colors.ink },
  searchLabel: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.secondary,
    marginBottom: 8,
  },
  searchInput: {
    height: 52,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: 10,
    backgroundColor: colors.card,
    paddingHorizontal: 16,
    fontSize: 15,
    color: colors.ink,
  },
  tagHits: { marginTop: 12 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },
  chip: {
    backgroundColor: colors.accentSoft,
    borderRadius: 999,
    paddingHorizontal: 11,
    paddingVertical: 5,
    minHeight: 30,
    justifyContent: 'center',
  },
  chipText: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.ink,
  },
  summaryCard: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.card,
    padding: 14,
    gap: 8,
    minHeight: 98,
    backgroundColor: colors.paper,
  },
  summaryCardGap: { marginTop: 10 },
  summaryEyebrow: {
    ...type.metadata,
    color: colors.ink,
    textTransform: 'uppercase',
  },
  summaryEyebrowMuted: { color: colors.tertiary },
  promise: {
    ...type.caption,
    color: colors.secondary,
    marginTop: 18,
    marginBottom: 12,
  },
  editLink: { alignItems: 'center', minHeight: 44, justifyContent: 'center' },
  editLinkText: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.ink,
  },
  footer: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: 18,
    gap: 10,
  },
  primary: {
    backgroundColor: colors.ink,
    borderRadius: radius.control,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryDisabled: { opacity: 0.4 },
  primaryLabel: {
    fontSize: 15,
    lineHeight: 20,
    color: colors.paper,
    fontWeight: '600',
  },
  secondary: {
    minHeight: 18,
    paddingVertical: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryLabel: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '500',
    color: colors.secondary,
  },
  footerHint: {
    ...type.metadata,
    color: colors.tertiary,
    textAlign: 'center',
  },
});
