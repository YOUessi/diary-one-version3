/** @param {import('expo/config').ConfigContext} context */
module.exports = ({ config: base }) => {
  const isStore = process.env.EXPO_PUBLIC_STORE_RELEASE === '1';
  // Legacy module name retained for AVFoundation decoding; Expo Go cannot load this native module.
  const includeVision =
    process.env.EXPO_PUBLIC_INCLUDE_VISION === '1' ||
    process.env.EAS_BUILD === 'true' ||
    process.env.EXPO_PUBLIC_DEV_CLIENT === '1';

  const plugins = (base.plugins ?? []).filter((p) => {
    const name = Array.isArray(p) ? p[0] : p;
    if (name === './modules/diary-one-vision' || name === './modules/diary-one-vision/app.plugin.js') return includeVision;
    return true;
  });
  if (!plugins.some((p) => (Array.isArray(p) ? p[0] : p) === 'expo-asset')) {
    plugins.push('expo-asset');
  }

  return {
    ...base,
    name: isStore ? 'Diary One' : 'Diary One Dev',
    ios: {
      ...base.ios,
      bundleIdentifier: isStore ? 'com.nexleap.diaryone' : base.ios.bundleIdentifier,
    },
    android: {
      ...base.android,
      package: isStore ? 'com.nexleap.diaryone' : base.android.package,
    },
    plugins,
    extra: {
      ...(base.extra ?? {}),
      eas: {
        ...(base.extra?.eas ?? {}),
        // Run `cd apps/mobile && npx eas init` once, then paste projectId here.
        projectId: process.env.EAS_PROJECT_ID || base.extra?.eas?.projectId || undefined,
      },
      privacyPolicyUrl:
        process.env.EXPO_PUBLIC_PRIVACY_POLICY_URL ||
        process.env.EXPO_PUBLIC_PRIVACY_URL ||
        '',
      termsUrl: process.env.EXPO_PUBLIC_TERMS_URL || '',
    },
  };
};
