const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { pathToFileURL, fileURLToPath } = require('node:url');
const ts = require('typescript');
const source = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../src/pipeline/sha256File.ts'), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
function harness(faults = {}) {
  const calls = { byteDigests: [], stringDigests: [] };
  const module = { exports: {} };
  vm.runInNewContext(source, { module, exports: module.exports, atob, Uint8Array, ArrayBuffer, require(name) {
    if (name === 'expo-file-system') return { File: class {
      constructor(uri) { this.uri = uri; }
      async bytes() {
        if (faults.readError) throw faults.readError;
        return fs.readFileSync(fileURLToPath(this.uri));
      } } };
    if (name === 'expo-crypto') return { CryptoDigestAlgorithm: { SHA256: 'SHA-256' },
      digest: async (algorithm, input) => {
        assert.equal(algorithm, 'SHA-256');
        assert.ok(input instanceof Uint8Array, 'Expo native Crypto.digest requires TypedArray, not ArrayBuffer');
        calls.byteDigests.push(Buffer.from(input));
        if (faults.digestError) throw faults.digestError;
        const digest = crypto.createHash('sha256').update(input).digest();
        return digest.buffer.slice(digest.byteOffset, digest.byteOffset + digest.byteLength);
      },
      digestStringAsync: async (algorithm, text) => {
        assert.equal(algorithm, 'SHA-256'); calls.stringDigests.push(text);
        return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
      } };
    throw Error('Unexpected dependency: ' + name);
  } });
  return { ...module.exports, calls };
}
const fixtures = [
  ['empty', Buffer.alloc(0), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'],
  ['abc', Buffer.from('abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'],
  ['all-byte-values', Buffer.from(Array.from({ length: 256 }, (_, i) => i)), '40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880'],
];
for (const [name, bytes, expected] of fixtures) test(`raw file ${name} preserves all original bytes and matches independently known SHA-256`, async t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'diary-hash-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const file = path.join(dir, 'input.bin'); fs.writeFileSync(file, bytes); const h = harness();
  assert.equal(await h.sha256File(pathToFileURL(file).href), expected);
  assert.equal(h.calls.byteDigests.length, 1); assert.deepEqual(h.calls.byteDigests[0], bytes);
  assert.equal(h.calls.stringDigests.length, 0, 'file content must not be hashed as UTF-8/base64 text');
});
test('file read failure remains visible and never calls Crypto', async () => {
  const original = Error('file unavailable'); const h = harness({ readError: original });
  await assert.rejects(h.sha256File('file:///missing'), error => error === original);
  assert.equal(h.calls.byteDigests.length, 0);
});
test('native Crypto failure remains visible without fallback or fake hash', async t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'diary-hash-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const file = path.join(dir, 'input'); fs.writeFileSync(file, 'abc'); const original = Error('native failed');
  const h = harness({ digestError: original });
  await assert.rejects(h.sha256File(pathToFileURL(file).href), error => error === original);
  assert.equal(h.calls.byteDigests.length, 1);
});
test('submitted manifest keeps compact JSON text hash semantics', async () => {
  const h = harness(); const manifest = { title: '骑行', count: 1 };
  const expected = crypto.createHash('sha256').update(JSON.stringify(manifest), 'utf8').digest('hex');
  assert.equal(await h.sha256SubmittedManifest(manifest), expected);
  assert.deepEqual(h.calls.stringDigests, [JSON.stringify(manifest)]); assert.equal(h.calls.byteDigests.length, 0);
});
