const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { ensurePodspecPath } = require('../plugins/withVideoEncoderAutolinking');
function fixture(t, config, hasPodspec = true) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'diary-encoder-config-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  fs.writeFileSync(path.join(dir, 'expo-module.config.json'), JSON.stringify(config));
  if (hasPodspec) fs.writeFileSync(path.join(dir, 'ExpoVideoEncoder.podspec'), 'fixture');
  return dir;
}
for (const platform of ['ios', 'apple']) test(`encoder ${platform} registration gains root podspec path without changing module metadata`, t => {
  const config = { platforms: [platform], [platform]: { modules: ['VideoEncoderModule'] } };
  const dir = fixture(t, config); ensurePodspecPath(dir); ensurePodspecPath(dir);
  const actual = JSON.parse(fs.readFileSync(path.join(dir, 'expo-module.config.json')));
  assert.deepEqual(actual, { ...config, [platform]: { ...config[platform], podspecPath: 'ExpoVideoEncoder.podspec' } });
});
test('future encoder metadata with an explicit path remains unchanged', t => {
  const config = { platforms: ['apple'], apple: { podspecPath: 'ios/ExpoVideoEncoder.podspec', modules: ['VideoEncoderModule'] } };
  const dir = fixture(t, config); const before = fs.readFileSync(path.join(dir, 'expo-module.config.json'), 'utf8');
  ensurePodspecPath(dir); assert.equal(fs.readFileSync(path.join(dir, 'expo-module.config.json'), 'utf8'), before);
});
test('an unexpected encoder package layout fails before mutating config', t => {
  const dir = fixture(t, { platforms: ['ios'], ios: { modules: ['VideoEncoderModule'] } }, false);
  const before = fs.readFileSync(path.join(dir, 'expo-module.config.json'), 'utf8');
  assert.throws(() => ensurePodspecPath(dir), /podspec moved/);
  assert.equal(fs.readFileSync(path.join(dir, 'expo-module.config.json'), 'utf8'), before);
});
