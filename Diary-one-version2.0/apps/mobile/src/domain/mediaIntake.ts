/** Lab / Device dev tools — not labeled as device capture in UI. */
export const PHOTO_LIBRARY_TEST_SOURCE = 'PHOTO_LIBRARY_TEST' as const;

/** Consumer Diary → Import from library (PRD IMP01). */
export const PHOTO_LIBRARY_USER_SOURCE = 'PHOTO_LIBRARY' as const;

export type MediaIntakeSource = typeof PHOTO_LIBRARY_TEST_SOURCE | typeof PHOTO_LIBRARY_USER_SOURCE;
