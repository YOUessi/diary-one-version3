const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

const originalResolve = config.resolver.resolveRequest;

config.resolver.resolveRequest = (context, moduleName, platform) => {
  const next = originalResolve
    ? (name) => originalResolve(context, name, platform)
    : (name) => context.resolveRequest(context, name, platform);

  if (moduleName === 'expo-media-library' || moduleName === 'expo-media-library/next') {
    return next('expo-media-library/legacy');
  }
  return next(moduleName);
};

module.exports = config;
