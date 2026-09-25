/** IMP01 — internal photo library adapter; never shown as device Manual capture. */
export const PHOTO_LIBRARY_TEST_SOURCE = 'PHOTO_LIBRARY_TEST' as const;

export type MediaIntakeSource = typeof PHOTO_LIBRARY_TEST_SOURCE;
