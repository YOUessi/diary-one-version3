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
  PREFERENCE_SURVEY_STEPS,
  SURVEY_OPEN_TEXT_MAX,
  type SurveyAnswers,
} from '../../onboarding/preferenceSurvey';
import {
  applyPreferenceSurveyAndFinish,
  applyPreferenceSurveyFromAccount,
  skipPreferenceSurveyAndFinish,
} from '../../onboarding/applyPreferenceSurvey';
import {
  AVOID_TOPICS,
  TAG_CATEGORIES,
  WRITING_STYLES,
  categoryLabel,
  styleById,
  tagById,
  tagsForCategories,
  type TagCategoryId,
} from '../../onboarding/tagLibrary';
import { SurveyCategoryIcon, SurveyCheckMark } from '../../components/SurveyIcons';

type SurveyParams = OnboardingStackParamList['PreferenceSurvey'];
type Route = RouteProp<{ PreferenceSurvey: SurveyParams }, 'PreferenceSurvey'>;
type Nav = NativeStackNavigationProp<{ PreferenceSurvey: SurveyParams }>;

let sessionAnswers: SurveyAnswers = { ...EMPTY_SURVEY_ANSWERS };

const INTRO_POINTS = [
  'Takes about 1–2 minutes',
  'You can skip this step',
  'You can change these preferences anytime',
] as const;

export default function PreferenceSurveyScreen() {
  const params = useRoute<Route>().params;
  const step = Number.isFinite(params?.step) ? Math.max(0, Math.floor(params.step)) : 0;
  const mode = params?.mode === 'account' ? 'account' : 'onboarding';
  const navigation = useNavigation<Nav>();
  const page = PREFERENCE_SURVEY_STEPS[step];
  const [answers, setAnswers] = useState<SurveyAnswers>(() => ({
    ...sessionAnswers,
    categories: [...sessionAnswers.categories],
    interestTags: [...sessionAnswers.interestTags],
    avoidTopics: [...sessionAnswers.avoidTopics],
  }));

  const visibleTags = useMemo(
    () => tagsForCategories(answers.categories),
    [answers.categories],
  );

  const canContinue = useMemo(() => {
    if (!page) return false;
    switch (page.kind) {
      case 'intro':
      case 'text':
      case 'review':
        return true;
      case 'category_grid':
        return answers.categories.length > 0;
      case 'tag_chips':
        return answers.interestTags.length > 0;
      case 'style_list':
        return Boolean(answers.styleId);
      case 'avoid_chips':
        return true;
      case 'consent':
        return answers.consent === 'agree' || answers.consent === 'local';
      default:
        return false;
    }
  }, [page, answers]);

  if (!page) {
    navigation.replace('PreferenceSurvey', { step: 0, mode });
    return null;
  }

  const persist = (next: SurveyAnswers) => {
    sessionAnswers = { ...next };
    setAnswers(next);
  };

  const leaveAccountSurvey = () => {
    sessionAnswers = { ...EMPTY_SURVEY_ANSWERS };
    if (navigation.canGoBack()) {
      navigation.pop(step + 1);
    }
  };

  const toggleCategory = (id: TagCategoryId) => {
    const on = answers.categories.includes(id);
    const categories = on
      ? answers.categories.filter((c) => c !== id)
      : [...answers.categories, id];
    const allowed = new Set(tagsForCategories(categories).map((t) => t.id));
    const interestTags = answers.interestTags.filter((t) => allowed.has(t));
    persist({ ...answers, categories, interestTags });
  };

  const toggleTag = (id: string) => {
    const on = answers.interestTags.includes(id);
    persist({
      ...answers,
      interestTags: on
        ? answers.interestTags.filter((t) => t !== id)
        : [...answers.interestTags, id],
    });
  };

  const toggleAvoid = (id: string) => {
    const on = answers.avoidTopics.includes(id);
    persist({
      ...answers,
      avoidTopics: on
        ? answers.avoidTopics.filter((t) => t !== id)
        : [...answers.avoidTopics, id],
    });
  };

  const onPrimary = () => {
    sessionAnswers = { ...answers };
    if (step >= PREFERENCE_SURVEY_STEPS.length - 1) {
      if (mode === 'account') {
        applyPreferenceSurveyFromAccount(sessionAnswers);
        leaveAccountSurvey();
      } else {
        applyPreferenceSurveyAndFinish(sessionAnswers);
        sessionAnswers = { ...EMPTY_SURVEY_ANSWERS };
      }
      return;
    }
    navigation.push('PreferenceSurvey', { step: step + 1, mode });
  };

  const onSkipAll = () => {
    sessionAnswers = { ...EMPTY_SURVEY_ANSWERS };
    if (mode === 'account') {
      leaveAccountSurvey();
      return;
    }
    skipPreferenceSurveyAndFinish();
  };

  const onBack = () => {
    if (step > 0) {
      navigation.goBack();
      return;
    }
    if (mode === 'account') {
      leaveAccountSurvey();
      return;
    }
    if (navigation.canGoBack()) navigation.goBack();
  };

  const progress = (step + 1) / PREFERENCE_SURVEY_STEPS.length;
  /** Figma 2145: Get started → Next (mid) → Continue (review) → Finish / Save. */
  const primaryLabel =
    page.kind === 'intro'
      ? 'Get started'
      : step >= PREFERENCE_SURVEY_STEPS.length - 1
        ? mode === 'account'
          ? 'Save preferences'
          : 'Finish and personalize'
        : page.kind === 'review'
          ? 'Continue'
          : 'Next';

  const showBack = step > 0 || mode === 'account';

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      {/* Figma 2145: ‹ left · progress · ✕ right */}
      <View style={styles.topBar}>
        {showBack ? (
          <Pressable onPress={onBack} style={styles.iconBtn} hitSlop={12} accessibilityLabel="Back">
            <Text style={styles.backText}>‹</Text>
          </Pressable>
        ) : (
          <View style={styles.iconBtn} />
        )}
        <View style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${Math.round(progress * 100)}%` }]} />
        </View>
        <Pressable onPress={onSkipAll} style={styles.iconBtn} hitSlop={12} accessibilityLabel="Close">
          <Text style={styles.closeText}>✕</Text>
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {page.kind === 'intro' ? (
          <Text style={styles.welcomeEyebrow}>WELCOME TO DIARY</Text>
        ) : null}
        <Text style={styles.title}>{page.title}</Text>
        {page.lead ? <Text style={styles.lead}>{page.lead}</Text> : null}

        {page.kind === 'intro' ? (
          <View style={styles.bullets}>
            {INTRO_POINTS.map((line) => (
              <View key={line} style={styles.bulletRow}>
                <SurveyCheckMark />
                <Text style={styles.bullet}>{line}</Text>
              </View>
            ))}
          </View>
        ) : null}

        {page.kind === 'category_grid' ? (
          <View style={styles.grid}>
            {TAG_CATEGORIES.map((cat) => {
              const on = answers.categories.includes(cat.id);
              return (
                <Pressable
                  key={cat.id}
                  onPress={() => toggleCategory(cat.id)}
                  style={[styles.tile, on && styles.tileOn]}
                  accessibilityRole="button"
                  accessibilityState={{ selected: on }}
                >
                  <SurveyCategoryIcon id={cat.id} />
                  <Text style={[styles.tileLabel, on && styles.tileLabelOn]}>{cat.label}</Text>
                  {on ? (
                    <View style={styles.checkCorner}>
                      <Text style={styles.checkMark}>✓</Text>
                    </View>
                  ) : (
                    <View style={styles.radioCorner} />
                  )}
                </Pressable>
              );
            })}
          </View>
        ) : null}

        {page.kind === 'text' ? (
          <TextInput
            value={answers.openText}
            onChangeText={(t) =>
              persist({ ...answers, openText: t.slice(0, SURVEY_OPEN_TEXT_MAX) })
            }
            placeholder="e.g. quiet mornings…"
            placeholderTextColor={colors.tertiary}
            multiline
            style={styles.textArea}
            maxLength={SURVEY_OPEN_TEXT_MAX}
          />
        ) : null}

        {page.kind === 'tag_chips' ? (
          <View style={styles.chipSections}>
            {(answers.categories.length ? answers.categories : TAG_CATEGORIES.map((c) => c.id)).map(
              (catId) => {
                const tags = visibleTags.filter((t) => t.categoryId === catId);
                if (!tags.length) return null;
                return (
                  <View key={catId} style={styles.chipBlock}>
                    <Text style={styles.chipSectionTitle}>{categoryLabel(catId)}</Text>
                    <View style={styles.chipRow}>
                      {tags.map((tag) => {
                        const on = answers.interestTags.includes(tag.id);
                        return (
                          <Pressable
                            key={tag.id}
                            onPress={() => toggleTag(tag.id)}
                            style={[styles.chip, on && styles.chipOn]}
                          >
                            <Text style={[styles.chipText, on && styles.chipTextOn]}>
                              {tag.label}
                            </Text>
                          </Pressable>
                        );
                      })}
                    </View>
                  </View>
                );
              },
            )}
          </View>
        ) : null}

        {page.kind === 'style_list' ? (
          <View style={styles.styleList}>
            {WRITING_STYLES.map((style) => {
              const on = answers.styleId === style.id;
              return (
                <Pressable
                  key={style.id}
                  onPress={() => persist({ ...answers, styleId: style.id })}
                  style={[styles.styleCard, on && styles.styleCardOn]}
                >
                  <View style={styles.styleCopy}>
                    <Text style={[styles.styleTitle, on && styles.styleTitleOn]}>{style.label}</Text>
                    <Text style={styles.styleDesc}>{style.description}</Text>
                  </View>
                  <View style={[styles.radio, on && styles.radioOn]}>
                    {on ? <View style={styles.radioDot} /> : null}
                  </View>
                </Pressable>
              );
            })}
          </View>
        ) : null}

        {page.kind === 'avoid_chips' ? (
          <View style={styles.chipRow}>
            {AVOID_TOPICS.map((topic) => {
              const on = answers.avoidTopics.includes(topic.id);
              return (
                <Pressable
                  key={topic.id}
                  onPress={() => toggleAvoid(topic.id)}
                  style={[styles.chip, on && styles.chipAvoidOn]}
                >
                  <Text style={[styles.chipText, on && styles.chipTextOn]}>{topic.label}</Text>
                  {on ? <Text style={styles.chipX}> ×</Text> : null}
                </Pressable>
              );
            })}
          </View>
        ) : null}

        {page.kind === 'review' ? (
          <View style={styles.review}>
            <ReviewRow
              label="Preferred categories"
              value={
                answers.categories.length
                  ? answers.categories.map(categoryLabel).join(', ')
                  : 'None'
              }
            />
            <ReviewRow
              label="Interest tags"
              value={
                answers.interestTags.length
                  ? answers.interestTags.map((id) => tagById(id)?.label ?? id).join(', ')
                  : 'None'
              }
            />
            <ReviewRow
              label="Writing style"
              value={answers.styleId ? styleById(answers.styleId)?.label ?? '—' : 'None'}
            />
            <ReviewRow
              label="Topics to avoid"
              value={
                answers.avoidTopics.length
                  ? answers.avoidTopics
                      .map((id) => AVOID_TOPICS.find((a) => a.id === id)?.label ?? id)
                      .join(', ')
                  : 'None'
              }
            />
            {answers.openText.trim() ? (
              <ReviewRow label="Anything else" value={answers.openText.trim()} />
            ) : null}
          </View>
        ) : null}

        {page.kind === 'consent' ? (
          <View style={styles.styleList}>
            {(
              [
                {
                  id: 'agree' as const,
                  label: 'Agree and continue',
                  description: 'Allow cloud evidence upload for memory generation.',
                },
                {
                  id: 'local' as const,
                  label: 'Browse on this device only for now',
                  description: 'You can turn cloud processing on later in Privacy & Data.',
                },
              ] as const
            ).map((opt) => {
              const on = answers.consent === opt.id;
              return (
                <Pressable
                  key={opt.id}
                  onPress={() => persist({ ...answers, consent: opt.id })}
                  style={[styles.styleCard, on && styles.styleCardOn]}
                >
                  <View style={styles.styleCopy}>
                    <Text style={[styles.styleTitle, on && styles.styleTitleOn]}>{opt.label}</Text>
                    <Text style={styles.styleDesc}>{opt.description}</Text>
                  </View>
                  <View style={[styles.radio, on && styles.radioOn]}>
                    {on ? <View style={styles.radioDot} /> : null}
                  </View>
                </Pressable>
              );
            })}
            <Text style={styles.footnote}>
              You can change cloud processing later in Privacy & Data. Signing in is not the same as
              this consent.
            </Text>
          </View>
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
        <Pressable onPress={onSkipAll} style={styles.secondary}>
          <Text style={styles.secondaryLabel}>
            {mode === 'account' ? 'Cancel' : 'Skip for now'}
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.reviewRow}>
      <Text style={styles.reviewLabel}>{label}</Text>
      <Text style={styles.reviewValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.paper },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingBottom: spacing.md,
    gap: spacing.sm,
  },
  iconBtn: {
    width: layout.minTouch,
    height: layout.minTouch,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeText: { fontSize: 16, color: colors.ink, fontWeight: '500' },
  backText: { fontSize: 28, color: colors.ink, fontWeight: '300', marginTop: -2 },
  progressTrack: {
    flex: 1,
    height: 3,
    borderRadius: 2,
    backgroundColor: colors.divider,
    overflow: 'hidden',
  },
  progressFill: { height: 3, backgroundColor: colors.ink, borderRadius: 2 },
  scroll: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.xl,
    flexGrow: 1,
  },
  welcomeEyebrow: {
    ...type.metadata,
    fontWeight: '600',
    color: colors.accent,
    letterSpacing: 0.8,
    marginBottom: spacing.md,
  },
  title: {
    ...type.titleSection,
    color: colors.ink,
    marginBottom: spacing.sm,
  },
  lead: { ...type.bodyStory, color: colors.secondary, marginBottom: spacing.xl },
  bullets: { gap: spacing.md, marginBottom: spacing.lg },
  bulletRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  bullet: { ...type.bodyStory, color: colors.ink, flex: 1 },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  tile: {
    width: '48%',
    flexGrow: 1,
    minHeight: 108,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.media,
    backgroundColor: colors.card,
    padding: spacing.md,
    justifyContent: 'flex-end',
    gap: spacing.sm,
  },
  tileOn: {
    borderColor: colors.ink,
    backgroundColor: colors.card,
  },
  tileLabel: { ...type.captionEmphasis, color: colors.ink },
  tileLabelOn: { fontWeight: '700' },
  radioCorner: {
    position: 'absolute',
    top: 10,
    right: 10,
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: colors.divider,
  },
  checkCorner: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkMark: { color: colors.paper, fontSize: 12, fontWeight: '700', lineHeight: 14 },
  radioDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.ink },
  textArea: {
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.media,
    padding: spacing.md,
    minHeight: 148,
    ...type.bodyStory,
    color: colors.ink,
    textAlignVertical: 'top',
    backgroundColor: colors.card,
    marginBottom: spacing.md,
  },
  chipSections: { gap: spacing.lg, marginBottom: spacing.md },
  chipBlock: { gap: spacing.sm },
  chipSectionTitle: {
    ...type.metadata,
    fontWeight: '700',
    color: colors.tertiary,
    letterSpacing: 0.6,
    textTransform: 'uppercase',
  },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.pill,
    paddingVertical: 10,
    paddingHorizontal: 14,
    backgroundColor: colors.card,
  },
  chipOn: {
    borderColor: colors.accentSoft,
    backgroundColor: colors.accentSoft,
  },
  chipAvoidOn: {
    borderColor: colors.accentSoft,
    backgroundColor: colors.accentSoft,
  },
  chipText: { ...type.caption, color: colors.ink },
  chipTextOn: { fontWeight: '700', color: colors.ink },
  chipX: { ...type.caption, color: colors.secondary },
  styleList: { gap: spacing.sm, marginBottom: spacing.md },
  styleCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: radius.media,
    padding: spacing.md,
    backgroundColor: colors.card,
  },
  styleCardOn: { borderColor: colors.ink, backgroundColor: colors.card },
  styleCopy: { flex: 1 },
  styleTitle: { ...type.bodyStory, fontWeight: '600', color: colors.ink },
  styleTitleOn: { fontWeight: '700' },
  styleDesc: { ...type.caption, color: colors.secondary, marginTop: 4 },
  radio: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 1.5,
    borderColor: colors.divider,
    alignItems: 'center',
    justifyContent: 'center',
  },
  radioOn: { borderColor: colors.ink },
  review: { gap: spacing.lg, marginBottom: spacing.md },
  reviewRow: {
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.divider,
    paddingBottom: spacing.md,
  },
  reviewLabel: {
    ...type.caption,
    fontWeight: '600',
    color: colors.tertiary,
    marginBottom: 6,
  },
  reviewValue: { ...type.bodyStory, color: colors.ink },
  footnote: {
    ...type.metadata,
    color: colors.tertiary,
    lineHeight: 18,
    marginTop: spacing.sm,
  },
  footer: {
    paddingHorizontal: layout.gutterDiary,
    paddingBottom: spacing.md,
    gap: spacing.sm,
  },
  /** Align with onboarding CTA metrics — 52×r12 */
  primary: {
    backgroundColor: colors.ink,
    borderRadius: 12,
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryDisabled: { opacity: 0.4 },
  primaryLabel: { fontSize: 15, lineHeight: 20, color: colors.paper, fontWeight: '600' },
  secondary: { minHeight: layout.minTouch, alignItems: 'center', justifyContent: 'center' },
  secondaryLabel: { ...type.bodyStory, color: colors.accent, fontWeight: '600' },
});
