const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const crypto = require('node:crypto');
const moduleUnderTest = { exports: {} };
vm.runInNewContext(ts.transpileModule(fs.readFileSync(require.resolve('../src/evidence/mobileclip/pixels.ts'), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText, { exports: moduleUnderTest.exports, setTimeout, Uint8Array, Float32Array, Float64Array });
const { preprocessAsync } = moduleUnderTest.exports;
const fixture = require('./evidence/reference.json');
function pixels(width, height) {
  const data = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    for (let c = 0; c < 3; c++) data[(y * width + x) * 4 + c] = (x * 7 + y * 13 + c * 47) % 256;
    data[(y * width + x) * 4 + 3] = 255;
  }
  return { width, height, data };
}
for (const sample of fixture.pixels) test(`async preprocessing retains Pillow tensor hash ${sample.width}x${sample.height}`, async () => {
  let ticked = false;
  setTimeout(() => { ticked = true; }, 0);
  const tensor = await preprocessAsync(pixels(sample.width, sample.height));
  assert.equal(crypto.createHash('sha256').update(new Uint8Array(tensor.buffer)).digest('hex'), sample.tensorSha256);
  assert.equal(ticked, true, 'the event loop must run before the tensor is complete');
});
test('preprocessing cancels mid-image and can process the next image', async () => {
  let cancelled = false;
  setTimeout(() => { cancelled = true; }, 0);
  await assert.rejects(preprocessAsync(pixels(1920, 1080), () => { if (cancelled) throw Error('session changed'); }), /session changed/);
  assert.equal((await preprocessAsync(pixels(32, 32))).length, 3 * 256 * 256);
});
test('invalid RGBA data fails before returning a model input', async () => {
  await assert.rejects(preprocessAsync({ width: 20, height: 20, data: new Uint8Array(1) }), /pixel size mismatch/);
});
