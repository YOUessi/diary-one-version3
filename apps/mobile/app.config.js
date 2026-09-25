/** @type {import('expo/config').ExpoConfig} */
const base = require('./app.json').expo;

const isStore = process.env.EXPO_PUBLIC_STORE_RELEASE === '1';

module.exports = {
  expo: {
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
    plugins: base.plugins,
  },
};
