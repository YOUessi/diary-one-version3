/**
 * Build channels (eas.json env):
 * - development: Metro + dev client, lab tools OK
 * - preview (TestFlight 内测): EXPO_PUBLIC_INTERNAL_BETA=1 — Figma 完整 UI，无 Lab
 * - production (App Store): EXPO_PUBLIC_STORE_RELEASE=1 — 隐藏未接线的 OAuth
 */
export const isStoreRelease = process.env.EXPO_PUBLIC_STORE_RELEASE === '1';

export const isInternalBetaBuild = process.env.EXPO_PUBLIC_INTERNAL_BETA === '1';

/** 仅本地 Metro 调试；TestFlight 包即使内测也不显示 Lab。 */
export const showInternalLabTools = __DEV__ && !isStoreRelease;
