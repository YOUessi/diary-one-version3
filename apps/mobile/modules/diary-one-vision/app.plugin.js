/**
 * Config plugin for DiaryOneVision — merges iOS Info.plist keys needed by Vision + photos.
 * Native Vision only works in Dev Client / prebuild — Expo Go ignores the module body.
 */
const { withInfoPlist } = require('expo/config-plugins');

function withDiaryOneVision(config) {
  return withInfoPlist(config, (cfg) => {
    const plist = cfg.modResults;
    if (!plist.NSPhotoLibraryUsageDescription) {
      plist.NSPhotoLibraryUsageDescription =
        'Diary One analyzes selected photos and video frames on-device to build your memory evidence.';
    }
    if (!plist.NSPhotoLibraryAddUsageDescription) {
      plist.NSPhotoLibraryAddUsageDescription =
        'Diary One saves images you choose to export to your photo library.';
    }
    // Vision runs on-device; camera not required for library intake.
    return cfg;
  });
}

module.exports = withDiaryOneVision;
