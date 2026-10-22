const fs = require('node:fs');
const path = require('node:path');
const { withDangerousMod } = require('expo/config-plugins');

// expo-video-encoder 1.0.23 puts its podspec at the package root. Expo's
// default discovery only searches subdirectories, so CocoaPods linked it as
// a React Native library without registering its Expo module or OS minimum.
function ensurePodspecPath(packageRoot) {
  const configPath = path.join(packageRoot, 'expo-module.config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const apple = config.apple ?? config.ios;
  if (!apple || apple.podspecPath) return;
  if (!fs.existsSync(path.join(packageRoot, 'ExpoVideoEncoder.podspec'))) {
    throw new Error('expo-video-encoder podspec moved; review the autolinking compatibility plugin.');
  }
  apple.podspecPath = 'ExpoVideoEncoder.podspec';
  fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);
}

module.exports = function withVideoEncoderAutolinking(config) {
  return withDangerousMod(config, ['ios', (cfg) => {
    const packageRoot = path.dirname(require.resolve('expo-video-encoder/package.json', {
      paths: [cfg.modRequest.projectRoot],
    }));
    ensurePodspecPath(packageRoot);
    return cfg;
  }]);
};
module.exports.ensurePodspecPath = ensurePodspecPath;
