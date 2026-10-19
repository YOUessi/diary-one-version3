const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { withDangerousMod } = require('expo/config-plugins');
const patch = require('./patches/onnxruntime-1.24.3-lifecycle.json');

const hash = source => createHash('sha256').update(source).digest('hex');

// ORT 1.24.3 retains a JSI WeakObject beyond Hermes teardown. Backport only
// upstream's runtime-owned tensor constructor, without changing model/runtime
// versions. CNG reapplies this after a clean install; generated ios/ stays owned
// by Expo. Refuse unknown source so dependency updates require an explicit review.
function applyLifecyclePatch(packageRoot) {
  const version = JSON.parse(fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')).version;
  if (version !== patch.packageVersion) {
    throw new Error(`ONNX lifecycle patch expects ${patch.packageVersion}, found ${version}; review/remove the compatibility patch before upgrading.`);
  }
  const pending = patch.files.map(file => {
    const destination = path.join(packageRoot, file.path);
    const source = fs.readFileSync(destination, 'utf8');
    if (hash(source) === file.afterSha256) return null;
    if (hash(source) !== file.beforeSha256) {
      throw new Error(`ONNX lifecycle patch: unexpected ${file.path}; refusing to overwrite unreviewed native code.`);
    }
    let result = source;
    for (const replacement of file.replacements) {
      if (result.split(replacement.before).length !== 2) {
        throw new Error(`ONNX lifecycle patch: ambiguous replacement in ${file.path}.`);
      }
      result = result.replace(replacement.before, replacement.after);
    }
    if (hash(result) !== file.afterSha256) throw new Error(`ONNX lifecycle patch checksum mismatch: ${file.path}`);
    return { destination, result };
  });
  // Validate every source before modifying any file, including partial reruns.
  for (const change of pending) if (change) fs.writeFileSync(change.destination, change.result);
}

module.exports = function withOnnxRuntimeLifecycle(config) {
  for (const platform of ['ios', 'android']) {
    config = withDangerousMod(config, [platform, cfg => {
      const packageRoot = path.dirname(require.resolve('onnxruntime-react-native/package.json', {
        paths: [cfg.modRequest.projectRoot],
      }));
      applyLifecyclePatch(packageRoot);
      return cfg;
    }]);
  }
  return config;
};
module.exports.applyLifecyclePatch = applyLifecyclePatch;
