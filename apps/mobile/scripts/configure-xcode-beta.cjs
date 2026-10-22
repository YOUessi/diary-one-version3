// Give Xcode's GUI archive the same public configuration as EAS preview.
// This does not select an Apple team, create certificates, or upload a build.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const profile = JSON.parse(fs.readFileSync(path.join(root, 'eas.json'), 'utf8')).build.preview;
const env = profile.env;
if (profile.ios.simulator !== false || profile.distribution !== 'store' ||
    env.EXPO_PUBLIC_DEV_BFF_URL !== 'https://bff.diary.luxe' ||
    env.EXPO_PUBLIC_DEV_BFF_TOKEN !== '' || env.EXPO_PUBLIC_STORE_RELEASE !== '0' ||
    env.EXPO_PUBLIC_INTERNAL_BETA !== '1' || env.EXPO_PUBLIC_INCLUDE_VISION !== '1') {
  throw new Error('Unexpected beta profile. Review eas.json before configuring Xcode.');
}
for (const [key, value] of Object.entries(env)) {
  if (!/^EXPO_PUBLIC_[A-Z0-9_]+$/.test(key) || typeof value !== 'string' ||
      (/TOKEN|SECRET|PASSWORD|API_KEY/.test(key) && value !== '')) {
    throw new Error('Beta configuration must contain only public values and empty shared tokens.');
  }
}
const file = path.join(root, 'ios/.xcode.env.local');
if (!fs.existsSync(path.dirname(file))) throw new Error('Generate the iOS project with expo prebuild first.');
const quote = value => "'" + value.replace(/'/g, "'\\''") + "'";
const values = { NODE_BINARY: process.execPath, EXPO_NO_DOTENV: '1', EXPO_PUBLIC_DEV_CLIENT: '0', ...env };
const begin = '# BEGIN DIARY ONE IOS BETA';
const end = '# END DIARY ONE IOS BETA';
const block = begin + '\n' + Object.entries(values).map(([key, value]) => `export ${key}=${quote(value)}`).join('\n') + '\n' + end;
const before = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '';
const pattern = /# BEGIN DIARY ONE IOS BETA\n[\s\S]*?# END DIARY ONE IOS BETA/;
const after = pattern.test(before) ? before.replace(pattern, block) : before.trimEnd() + '\n' + block + '\n';
if (process.argv.includes('--write')) fs.writeFileSync(file, after);
console.log(JSON.stringify({
  mode: process.argv.includes('--write') ? 'written' : 'check_only',
  file, bundleIdentifier: 'com.nexleap.diaryone.dev', publicBff: env.EXPO_PUBLIC_DEV_BFF_URL,
  privacyPolicyConfigured: Boolean(env.EXPO_PUBLIC_PRIVACY_POLICY_URL || env.EXPO_PUBLIC_PRIVACY_URL),
  termsConfigured: Boolean(env.EXPO_PUBLIC_TERMS_URL),
  signing: 'Choose the authorized Apple team in Xcode; not changed by this script.',
}, null, 2));
