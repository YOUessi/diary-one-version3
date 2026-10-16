/**
 * Build channels:
 * - Expo Go / Metro / TestFlight / Store → formal consumer App only
 * - No Lab / Research / Demo UI in any consumer build
 *
 * Product rule: packaged OR Expo Go must match Figma end-user App.
 */
export const isStoreRelease = process.env.EXPO_PUBLIC_STORE_RELEASE === '1';

export const isInternalBetaBuild = process.env.EXPO_PUBLIC_INTERNAL_BETA === '1';

/** Permanently off — consumer App never exposes Lab tools. */
export const isLabToolsEnabled = false;

/** @deprecated Always false. Kept for existing imports. */
export const showInternalLabTools = false;

/** Always true for shipping UI. */
export const isFormalConsumerApp = true;

/** Fail-closed cloud auth (Apple / Google / email OTP → session_token). */
export const requireCloudAuth = true;
