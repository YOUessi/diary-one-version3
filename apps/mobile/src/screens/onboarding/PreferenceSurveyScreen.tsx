import { appStrings, appLocale } from '../../domain/strings';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { CommonActions, useNavigation, useRoute } from '@react-navigation/native';
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
  stepIndexToId,
  suggestLabelsFromCustom,
  SURVEY_OPEN_TEXT_MAX,
  togglePrefOption,
  clearCustomAnswers,
  surveyHasAnswers,
} from '../../onboarding/preferenceSurvey';
import {
  applyPreferenceSurveyAndFinish,
  applyPreferenceSurveyFromAccount,
} from '../../onboarding/applyPreferenceSurvey';
import { searchSurveyTags } from '../../onboarding/surveyTagLibrary';
import { useAppStore } from '../../store/useAppStore';

type SurveyParams = OnboardingStackParamList['PreferenceSurvey'];
type Route = RouteProp<{ PreferenceSurvey: SurveyParams }, 'PreferenceSurvey'>;
type Nav = NativeStackNavigationProp<{ PreferenceSurvey: SurveyParams }>;


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
}: {
  label: string;
  description: string;
  selected: boolean;
  onPress: () => void;
  compact?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={[
        styles.optionCard,
        compact && styles.optionCardCompact,
        !compact && styles.gridCard,
        selected && styles.optionCardOn,
      ]}
      accessibilityRole="button"
      accessibilityState={{ selected }}
    >
      <View style={styles.optionCopy}>
        <Text style={[styles.optionLabel, !compact && styles.gridLabel]}>{label}</Text>
        <Text style={styles.optionDesc}>{description}</Text>
      </View>
      <View style={[styles.check, selected && styles.checkOn]}>
        {selected ? <Text style={styles.checkMark}>✓</Text> : null}
      </View>
    </Pressable>
  );
}

function ChipRow({ labels, onRemove }: { labels: string[]; onRemove?: (label: string) => void }) {
  return (
    <View style={styles.chipRow}>
      {labels.map((label) => (
        onRemove ? (
          <Pressable key={label} style={styles.chip} hitSlop={7} onPress={() => onRemove(label)}
            accessibilityRole="button" accessibilityLabel={`Remove ${label}`}>
            <Text style={styles.chipText}>{label} ×</Text>
          </Pressable>
        ) : (
          <View key={label} style={styles.chip}><Text style={styles.chipText}>{label}</Text></View>
        )
      ))}
    </View>
  );
}

export default function PreferenceSurveyScreen() {
  const language = useAppStore((s) => s.language);
  const strings = appStrings(language);
  const chinese = appLocale(language) === 'zh-CN';
  const route = useRoute<Route>();
  const params = route.params;
  const stepId = resolveStepId(params?.step);
  const mode = params?.mode === 'account' ? 'account' : 'onboarding';
  const navigation = useNavigation<Nav>();
  const meta = stageMeta(stepId);
  const answers = params?.answers ?? EMPTY_SURVEY_ANSWERS;
  const [tagSearch, setTagSearch] = useState('');
  const [saving, setSaving] = useState(false);
  const saveLock = useRef(false);
  const owner = useRef({ token: useAppStore.getState().sessionToken, email: useAppStore.getState().localProfile.email });
  const emptySummary = !surveyHasAnswers(answers);

  // Also preserve edits when the user uses the native back action.
  useEffect(() => {
    return navigation.addListener('beforeRemove', (event) => {
      if (!['GO_BACK', 'POP'].includes(event.data.action.type)) return;
      const state = navigation.getState();
      if (state.routes[state.index]?.key !== route.key) return;
      const previous = state.routes[state.index - 1];
      if (previous?.name === 'PreferenceSurvey') {
        navigation.dispatch({ ...CommonActions.setParams({ answers }), source: previous.key });
      }
    });
  }, [answers, navigation, route.key]);

  const canContinue = useMemo(() => {
    switch (stepId) {
      case 'welcome':
      case 'custom':
      case 'custom_review':
      case 'summary':
        return true;
      case 'moments':
      case 'show_less':
        return true;
      default:
        return false;
    }
  }, [stepId]);

  const tagHits = useMemo(() => {
    return searchSurveyTags(tagSearch);
  }, [tagSearch]);

  const persist = (next: SurveyAnswers) => navigation.setParams({ answers: next });

  const leaveAccountSurvey = () => {
    const state = navigation.getState();
    let count = 0;
    for (let i = state.index; i >= 0 && state.routes[i].name === 'PreferenceSurvey'; i--) count++;
    if (navigation.canGoBack()) navigation.pop(Math.min(count, state.index));
  };

  const go = (next: QuestionnaireStepId, nextAnswers = answers) => {
    navigation.push('PreferenceSurvey', { step: next, mode, answers: nextAnswers });
  };

  const saveAndLeave = async (nextAnswers: SurveyAnswers) => {
    if (saveLock.current) return;
    saveLock.current = true;
    setSaving(true);
    try {
      const current = useAppStore.getState();
      if (current.sessionToken !== owner.current.token || current.localProfile.email !== owner.current.email) {
        throw new Error('Account changed. Please reopen preferences.');
      }
      if (mode === 'account') {
        await applyPreferenceSurveyFromAccount(nextAnswers);
        leaveAccountSurvey();
      } else await applyPreferenceSurveyAndFinish(nextAnswers);
    } catch (error) {
      Alert.alert('Preferences not saved', error instanceof Error ? error.message : 'Please try again.');
    } finally {
      saveLock.current = false;
      setSaving(false);
    }
  };

  const onPrimary = async () => {
    if (saveLock.current) return;
    let nextAnswers = answers;
    if (stepId === 'custom') {
      const fromWords = answers.reviewedText === answers.customText ? [] : suggestLabelsFromCustom(answers.customText);
      nextAnswers = { ...answers, reviewedText: answers.customText,
        suggestedLabels: [...new Set([...answers.suggestedLabels, ...fromWords])] };
      persist(nextAnswers);
    }
    const next = nextQuestionnaireStep(stepId, nextAnswers);
    if (next === 'done') {
      await saveAndLeave(nextAnswers);
      return;
    }
    go(next, nextAnswers);
  };

  const onSkipAll = () => {
    if (mode === 'account') {
      leaveAccountSurvey();
      return;
    }
    void saveAndLeave({ ...EMPTY_SURVEY_ANSWERS });
  };

  const onSkipStep = () => {
    if (stepId === 'custom' || stepId === 'custom_review') {
      const cleared = clearCustomAnswers(answers);
      persist(cleared);
      go('show_less', cleared);
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
    if (navigation.canGoBack()) {
      // Carry later edits back to the preceding step without a shared mutable draft.
      const state = navigation.getState();
      const previous = state.routes[state.index - 1];
      if (previous?.name === 'PreferenceSurvey') navigation.dispatch({ ...CommonActions.setParams({ answers }), source: previous.key });
      navigation.goBack();
    }
  };

  /** Figma “Go back and edit” → return to Moments (stage 1). */
  const onEditFromSummary = () => {
    const state = navigation.getState();
    const index = state.routes.findLastIndex(r => r.name === 'PreferenceSurvey' &&
      resolveStepId(r.params?.step) === 'moments');
    if (index >= 0) {
      const routes = state.routes.slice(0, index + 1).map((r, i) => i === index
        ? { ...r, params: { ...r.params, answers } } : r);
      navigation.dispatch(CommonActions.reset({ ...state, routes, index }));
    } else go('moments');
  };

  const primaryLabel =
    stepId === 'welcome'
      ? strings.getStarted
      : stepId === 'custom_review' || stepId === 'summary'
        ? stepId === 'summary' && emptySummary ? strings.withoutPreferences : strings.confirmContinue
        : strings.continue;

  const secondaryLabel =
    stepId === 'welcome'
      ? mode === 'account'
        ? strings.cancel
        : strings.skipNow
      : stepId === 'custom' || stepId === 'custom_review'
        ? strings.skipStep
        : stepId === 'summary'
          ? null
          : strings.skipSetup;

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
    if (answers.showLessIds.includes('nothing')) {
      return ['Nothing for now'];
    }
    return answers.showLessIds.map((id) => showLessChipLabel(id));
  }, [answers.showLessIds]);

  const specificChips = answers.momentIds.includes('something_else') ? answers.suggestedLabels : [];
  const removeSuggested = (label: string) => persist({ ...answers,
    suggestedLabels: answers.suggestedLabels.filter(l => l !== label),
    searchedLabels: answers.searchedLabels?.filter(l => l !== label) });

  const addSuggested = (label: string) => {
    if (answers.suggestedLabels.includes(label)) return;
    persist({
      ...answers,
      suggestedLabels: [...answers.suggestedLabels, label],
      searchedLabels: [...new Set([...(answers.searchedLabels ?? []), label])],
    });
  };

  return (
    <SafeAreaView
      style={[styles.safe, mode === 'account' && { paddingBottom: layout.tabBarHeight + spacing.md }]}
      edges={['top', 'bottom']}
    >
      <KeyboardAvoidingView style={styles.safe} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      {stepId === 'welcome' ? (
        <>
          <View style={styles.welcomeNav} />
          <View style={styles.welcomeTop} />
        </>
      ) : (
        <View style={styles.topNav}>
          <Text style={styles.stageLabel}>{meta.stageLabel}</Text>
          <Pressable onPress={onBack} disabled={saving} hitSlop={12} accessibilityLabel={strings.back}>
            <Text style={styles.backText}>{strings.back}</Text>
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
        style={styles.scrollViewport}
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {stepId === 'welcome' ? (
          <>
            <Text style={styles.welcomeEyebrow}>{strings.welcome}</Text>
            <View style={styles.welcomeHeadingGap} />
            <View style={styles.welcomeHeadingBlock}>
              <Text style={styles.titleWelcome}>{strings.preferencesTitle}</Text>
              <Text style={styles.leadWelcome}>
                {strings.preferencesLead}
              </Text>
            </View>
            <View style={styles.bullets}>
              {(chinese ? ['你可以随时修改偏好。', '不设置偏好也可以使用日记。', '偏好不会改变素材中实际发生的事。'] : INTRO_POINTS).map((line) => (
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
                  label={opt.label}
                  description={opt.description}
                  selected={answers.momentIds.includes(opt.id)}
                  onPress={() =>
                    {
                      const momentIds = togglePrefOption(answers.momentIds, opt, MOMENT_OPTIONS);
                      persist({ ...(momentIds.includes('something_else') ? answers : clearCustomAnswers(answers)), momentIds });
                    }
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
                  persist({ ...answers, customText: t.slice(0, SURVEY_OPEN_TEXT_MAX),
                    suggestedLabels: answers.searchedLabels ?? [], reviewedText: undefined })
                }
                placeholder="e.g. fishing by the water, city walks, or model-building"
                placeholderTextColor={colors.tertiary}
                multiline
                style={styles.noteInput}
                maxLength={SURVEY_OPEN_TEXT_MAX}
                accessibilityLabel="Your words (optional)"
              />
            </View>
            <Text style={styles.searchLabel}>OR SEARCH A TAG</Text>
            <TextInput
              value={tagSearch}
              onChangeText={setTagSearch}
              placeholder="Search an activity or place"
              placeholderTextColor={colors.tertiary}
              style={styles.searchInput}
              accessibilityLabel="Search an activity or place"
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
                <ChipRow labels={answers.suggestedLabels} onRemove={removeSuggested} />
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
            {answers.customText.trim() ? <View style={[styles.noteCard, styles.noteCardReview]}>
              <Text style={styles.noteLabel}>YOUR WORDS</Text>
              <Text style={styles.noteBody}>{answers.customText.trim()}</Text>
            </View> : null}
            <Text style={styles.searchLabel}>SUGGESTED PREFERENCES</Text>
            <ChipRow labels={answers.suggestedLabels} onRemove={removeSuggested} />
            <Pressable onPress={onBack} style={styles.editLink} accessibilityRole="button">
              <Text style={styles.editLinkText}>Edit words or search tags</Text>
            </Pressable>
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
              <Text style={styles.title}>{emptySummary ? 'Review your preferences' : 'Here is what Diary will look out for'}</Text>
              <Text style={styles.lead}>
                {emptySummary ? 'Nothing is set yet. You can add preferences anytime in Settings.' : 'You can change these preferences anytime in Settings.'}
              </Text>
            </View>
            <View style={styles.summaryCard}>
              <Text style={styles.summaryEyebrow}>NOTICE MORE</Text>
              {noticeMoreChips.length ? <ChipRow labels={noticeMoreChips} /> : <Text style={styles.unset}>Not set yet</Text>}
            </View>
            <View style={[styles.summaryCard, styles.summaryCardGap]}>
              <Text style={[styles.summaryEyebrow, styles.summaryEyebrowMuted]}>
                SHOW LESS OFTEN
              </Text>
              {showLessChips.length ? <ChipRow labels={showLessChips} /> : <Text style={styles.unset}>Not set yet</Text>}
            </View>
            {specificChips.length || (answers.momentIds.includes('something_else') && answers.customText.trim()) ? (
              <View style={[styles.summaryCard, styles.summaryCardGap]}>
                <Text style={[styles.summaryEyebrow, styles.summaryEyebrowMuted]}>
                  SPECIFIC THINGS YOU ADDED
                </Text>
                <ChipRow labels={specificChips} />
                {!specificChips.length && answers.customText.trim() ? <Text style={styles.noteBody}>{answers.customText.trim()}</Text> : null}
              </View>
            ) : null}
            <Text style={styles.promise}>
              {emptySummary ? 'Diary will follow what was actually captured. You can set preferences later.' :
                'These preferences only affect how your content is selected and presented. Diary only uses moments that were actually captured.'}
            </Text>
            <Pressable onPress={onEditFromSummary} disabled={saving} style={styles.editLink}>
              <Text style={styles.editLinkText}>Go back and edit</Text>
            </Pressable>
          </>
        ) : null}
      </ScrollView>

      <View style={styles.footer}>
        <Pressable
          onPress={onPrimary}
          disabled={!canContinue || saving}
          accessibilityRole="button"
          accessibilityState={{ disabled: !canContinue || saving, busy: saving }}
          style={[styles.primary, !canContinue && styles.primaryDisabled]}
        >
          <Text style={styles.primaryLabel}>{saving ? strings.saving : primaryLabel}</Text>
        </Pressable>
        {secondaryLabel ? (
          <Pressable
            accessibilityRole="button"
            onPress={
              stepId === 'custom' || stepId === 'custom_review' ? onSkipStep : onSkipAll
            }
            style={styles.secondary}
            disabled={saving}
          >
            <Text style={styles.secondaryLabel}>{secondaryLabel}</Text>
          </Pressable>
        ) : (
          <Text style={styles.footerHint}>You can change this anytime in Settings.</Text>
        )}
      </View>
      </KeyboardAvoidingView>
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
  scrollViewport: { flex: 1 },
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
  bullets: { gap: 20, marginTop: 80 },
  bullet: { fontSize: 15, lineHeight: 18, color: colors.secondary },
  headingBlock: {
    minHeight: 122,
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
  gridCard: { flexBasis: '47%', flexGrow: 1 },
  gridLabel: { maxWidth: 116 },
  listCol: { gap: 8 },
  /** Figma Preference Option Card — unselected 1px divider; selected 1.5 ink */
  optionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    minHeight: 112,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.card,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  optionCardCompact: { minHeight: 54, width: '100%' },
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
    marginBottom: 0,
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
  unset: { fontSize: 15, lineHeight: 18, color: colors.secondary },
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
    marginBottom: 0,
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
    minHeight: 26,
    paddingVertical: 6,
  },
});
