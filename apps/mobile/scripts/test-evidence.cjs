const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const ts = require('typescript');
// Compile pure algorithm modules with the app's pinned TypeScript compiler.
require.extensions['.ts'] = (module, filename) => {
  const source = fs.readFileSync(filename, 'utf8');
  module._compile(ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true } }).outputText, filename);
};
const { coverageV07 } = require('../src/evidence/mobileclip/coverageV07.ts');
const { preprocess, pixelQuality } = require('../src/evidence/mobileclip/pixels.ts');
const { endpointV05 } = require('../src/evidence/mobileclip/endpointV05.ts');
const { planProbeTimestampsMs } = require('../src/evidence/probePlan.ts');
const { routeSemanticClip } = require('../src/evidence/semanticRouter.ts');
const { MOBILECLIP_FP16_V07_PROFILE } = require('../src/evidence/types.ts');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const root = path.resolve(__dirname, '..');
const fixture = JSON.parse(fs.readFileSync(process.argv[2] || path.join(root, 'tests/evidence/reference.json')));
let maxObjectiveError = 0;
for (const test of fixture.cases) {
  const got = coverageV07(test.input);
  assert.deepEqual(got.anchors, test.expected.anchors, test.name);
  assert.equal(got.reason, test.expected.reason, test.name);
  maxObjectiveError = Math.max(maxObjectiveError, Math.abs(got.proposed.objective - test.expected.objective));
  assert.ok(Math.abs(got.proposed.objective - test.expected.objective) < 1e-6, `${test.name}: objective`);
}
for (const test of fixture.pixels) {
  const data = new Uint8Array(test.width * test.height * 4);
  for (let y = 0; y < test.height; y++) for (let x = 0; x < test.width; x++) {
    for (let c = 0; c < 3; c++) data[(y * test.width + x) * 4 + c] = (x * 7 + y * 13 + c * 47) % 256;
    data[(y * test.width + x) * 4 + 3] = 255;
  }
  const tensor = preprocess({ ...test, data });
  assert.equal(sha(new Uint8Array(tensor.buffer)), test.tensorSha256, `Pillow pixels ${test.width}x${test.height}`);
}
const black = { width: 32, height: 32, data: new Uint8Array(32*32*4) };
assert.equal(pixelQuality(black).eligibleForSelection, false);
const white = { ...black, data: new Uint8Array(32*32*4).fill(255) };
assert.equal(pixelQuality(white).eligibleForSelection, true);
assert.equal(pixelQuality(white).meanLuma, 255);
assert.ok(planProbeTimestampsMs(10000, MOBILECLIP_FP16_V07_PROFILE).length <= 12);
assert.throws(() => coverageV07({ points: [0,0], vectors: [[1],[1]], scores: [], baseline:[0] }));
assert.throws(() => coverageV07({ points: [0], vectors: [[NaN]], scores: [], baseline:[0] }));
const labels = [{identifier:'water',confidence:0.4},{identifier:'outdoor',confidence:0.6}];
const points = [{ vector:[1,0], classifications:[labels[0]], fullClassifications:labels },
  ...Array.from({length:2},()=>({ vector:[1,0], classifications:[labels[1]], fullClassifications:labels }))];
assert.equal(endpointV05(points, new Set([0])).size, 0);
const manifest = require('../assets/models/mobileclip-s0-fp16/manifest.json');
for (const [file, info] of Object.entries(manifest.files)) {
  const bytes = fs.readFileSync(path.join(root, 'assets/models/mobileclip-s0-fp16', file));
  assert.equal(bytes.length, info.bytes); assert.equal(sha(bytes), info.sha256);
}
// Smoke real descriptor routing, including full prompt scores (no network/native module).
const real = fixture.cases.find(c=>c.name.startsWith('real-'));
if (real) {
  const probes=real.input.points.map((t,i)=>({requestedMs:t,actualPtsMs:t,
    embedding:{vector:real.input.vectors[i], classifications:manifest.labels.map((identifier,j)=>({identifier,confidence:real.input.scores[i][j]})).sort((a,b)=>b.confidence-a.confidence).slice(0,3),
      fullClassifications:manifest.labels.map((identifier,j)=>({identifier,confidence:real.input.scores[i][j]}))},
    meanLuma:128,darkPixelRatio:0,sharpness:100,eligibleForSelection:true,qualityReasonCodes:[]}));
  const route=routeSemanticClip({profile:MOBILECLIP_FP16_V07_PROFILE,modelId:manifest.model_id,analyzerDegraded:false,probes});
  assert.ok(route.selectedTimestampsMs.length>0);
  assert.equal(new Set(route.selectedTimestampsMs).size,route.selectedTimestampsMs.length);
}
console.log(JSON.stringify({passed:true,coverageCases:fixture.cases.length,pixelCases:fixture.pixels.length,maxObjectiveError,modelSha256:manifest.files['image_encoder.onnx'].sha256}));
