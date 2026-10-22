const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { applyLifecyclePatch } = require('../plugins/withOnnxRuntimeLifecycle');
const patch = require('../plugins/patches/onnxruntime-1.24.3-lifecycle.json');
const packageRoot = path.dirname(require.resolve('onnxruntime-react-native/package.json'));
const hash = value => createHash('sha256').update(value).digest('hex');

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'diary-onnx-patch-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({ version: patch.packageVersion }));
  fs.mkdirSync(path.join(root, 'cpp'));
  for (const file of patch.files) {
    let source = fs.readFileSync(path.join(packageRoot, file.path), 'utf8');
    // A development install may already be patched. Recover the exact upstream
    // fixture and require its original digest before exercising the plugin.
    if (hash(source) === file.afterSha256) {
      for (const { before, after } of [...file.replacements].reverse()) {
        if (!after) source = source.replace('  std::shared_ptr<Ort::Env> ortEnv_;', `${before}  std::shared_ptr<Ort::Env> ortEnv_;`);
        else source = source.replace(after, before);
      }
    }
    assert.equal(hash(source), file.beforeSha256);
    fs.writeFileSync(path.join(root, file.path), source);
  }
  return root;
}

test('clean install and repeat prebuild produce the reviewed runtime-owned constructor backport', t => {
  const root = fixture(t);
  applyLifecyclePatch(root);
  const first = patch.files.map(f => fs.readFileSync(path.join(root, f.path), 'utf8'));
  first.forEach((source, i) => assert.equal(hash(source), patch.files[i].afterSha256));
  assert.ok(!first[0].includes('shared_ptr<facebook::jsi::WeakObject>'));
  assert.match(first[0], /runtime\.global\(\)[\s\S]*__tensorConstructor/);
  applyLifecyclePatch(root);
  first.forEach((source, i) => assert.equal(fs.readFileSync(path.join(root, patch.files[i].path), 'utf8'), source));
});

test('unknown ORT version is rejected without replacing any source', t => {
  const root = fixture(t);
  fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({ version: '1.25.0' }));
  assert.throws(() => applyLifecyclePatch(root), /expects 1.24.3, found 1.25.0/);
  for (const file of patch.files) assert.equal(hash(fs.readFileSync(path.join(root, file.path))), file.beforeSha256);
});

test('unexpected second source cannot leave the first source half-patched', t => {
  const root = fixture(t);
  fs.appendFileSync(path.join(root, patch.files[1].path), '\n// another patch\n');
  assert.throws(() => applyLifecyclePatch(root), /unexpected cpp\/JsiMain.cpp/);
  assert.equal(hash(fs.readFileSync(path.join(root, patch.files[0].path))), patch.files[0].beforeSha256);
});

test('an interrupted previous write is completed idempotently', t => {
  const root = fixture(t);
  const first = patch.files[0];
  let source = fs.readFileSync(path.join(root, first.path), 'utf8');
  for (const { before, after } of first.replacements) source = source.replace(before, after);
  fs.writeFileSync(path.join(root, first.path), source);
  applyLifecyclePatch(root);
  for (const file of patch.files) assert.equal(hash(fs.readFileSync(path.join(root, file.path))), file.afterSha256);
});
