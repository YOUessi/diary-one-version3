/**
 * Locked against:
 * - GitHub nexleap-diary-one @ codex/handoff-algorithm-v1.75-web-v1.63-20260921
 * - Local freeze: codex_diary_one_algorithm_v1_75_engineering_handoff_20260916
 *
 * App builds Bundle V04; the BFF accepts the legacy staged contract and the
 * Product V07 contract used by the R5_7 editor. The server health selects its route.
 */
export const ALGORITHM_LOCK = {
  candidate: 'Product V07 / R5_7',
  x02PreviewPath: '/x02/v0.4.1/preview',
  previewSchema: 'DIARY_ONE_X02_STAGED_PREVIEW_V04_1',
  previewContractSha256: '10f8c36cc0548873cc7a1c88cd8216da167fbb6f05ac9bd83768f61729679b13',
  productPreviewSchema: 'DIARY_ONE_X02_PRODUCT_PREVIEW_V01',
  resultContractVersion: 'DIARY_ONE_INPUT_BOUND_RESULT_V01',
  resultContractSha256: {
    DIARY_ONE_X02_STAGED_PREVIEW_V04_1: '10f8c36cc0548873cc7a1c88cd8216da167fbb6f05ac9bd83768f61729679b13',
    DIARY_ONE_X02_PRODUCT_PREVIEW_V01: '06a73f19246f2a5f729d9c9e349dc5fabd80efb6c55897793ee26a1de884ea48',
  },
  bundleV04: 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04',
  spatial: 'ASPECT_FIT_LETTERBOX',
  researchOptInOnly: true,
} as const;
