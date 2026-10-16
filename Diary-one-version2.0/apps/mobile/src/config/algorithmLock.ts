/**
 * Locked against:
 * - GitHub nexleap-diary-one @ codex/handoff-algorithm-v1.75-web-v1.63-20260921
 * - Local freeze: codex_diary_one_algorithm_v1_75_engineering_handoff_20260916
 *
 * App never runs Python in-process. Phone builds Bundle V04, BFF/X01 runs V1.75 / X02 v0.4.1.
 */
export const ALGORITHM_LOCK = {
  candidate: 'V1.75',
  x02PreviewPath: '/x02/v0.4.1/preview',
  previewSchema: 'DIARY_ONE_X02_STAGED_PREVIEW_V04_1',
  bundleV04: 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04',
  spatial: 'ASPECT_FIT_LETTERBOX',
  researchOptInOnly: true,
} as const;
