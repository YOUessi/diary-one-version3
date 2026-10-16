// Fresh V1.66 local decoding; archived V1.64 normalizer only, no semantic reuse or model calls.
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const started = performance.now();
const startedAt = new Date().toISOString();
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [packId, ...extra] = process.argv.slice(2);
const round = '1';
if (!['1', '2', '3'].includes(packId) || extra.length) {
  throw new Error('Usage: node tools/codex_prepare_editorial_evidence_v1_66.mjs <pack 1|2|3>');
}
const area = path.join(root, 'var/codex_v1_66_editorial_allocation');
const preparationPath = path.join(area, 'codex_preparation.json');
const preparation = JSON.parse(fs.readFileSync(preparationPath, 'utf8'));
const candidatePath = path.join(area, 'codex_candidate.json');
const candidate = JSON.parse(fs.readFileSync(candidatePath, 'utf8'));
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
if (candidate.preparation_sha256 !== hash(fs.readFileSync(preparationPath))
  || candidate.normalization_harness_sha256 !== hash(fs.readFileSync(fileURLToPath(import.meta.url)))) {
  throw new Error('Candidate preparation or normalization harness drift');
}
const pack = preparation.packs.find(item => String(item.pack_id) === packId);
if (!pack || !Array.isArray(pack.assets) || !pack.assets.length) throw new Error('Missing nonempty pack');
if (typeof pack.session_id !== 'string' || typeof pack.exported_at !== 'string') {
  throw new Error('Each pack needs fixed session_id and exported_at metadata');
}
const destination = path.join(area, `pack_${packId}`, `round_${round}`);
if (fs.existsSync(destination)) throw new Error('Refusing to overwrite an existing preparation round');
const snapshot = path.resolve(root, 'var/codex_v1_64_repeat_review/codex_web_normalizer');
if (preparation.normalizer_snapshot !== snapshot) throw new Error('Unexpected normalizer source');
const priorPreparationPath = path.resolve(root, 'var/codex_v1_64_repeat_review/codex_preparation.json');
if (hash(fs.readFileSync(priorPreparationPath)) !== preparation.prior_preparation_sha256) {
  throw new Error('Archived V1.64 preparation drift');
}
const stableUuid = value => {
  const h = hash(value);
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-4${h.slice(13, 16)}-8${h.slice(17, 20)}-${h.slice(20, 32)}`;
};
const runtime = process.env.CODEX_EDITORIAL_NODE_DEPENDENCIES;
if (!runtime) throw new Error('Set CODEX_EDITORIAL_NODE_DEPENDENCIES to a Node dependency directory containing Playwright');
const { chromium } = createRequire(path.join(runtime, 'package.json'))('playwright');
// Dependency only: executable normalization source always comes from the snapshot.
const typescriptModule = process.env.CODEX_EDITORIAL_TYPESCRIPT_MODULE
  || path.resolve(root, '../apps/eval-web/node_modules/typescript/lib/typescript.js');
const ts = createRequire(import.meta.url)(typescriptModule);
const moduleNames = ['media-evidence', 'result-contract', 'research-run-control', 'codex-runtime-policy'];
const modules = new Map();
const moduleHashes = {};
for (const name of moduleNames) {
  const source = fs.readFileSync(path.join(snapshot, `${name}.ts`), 'utf8');
  moduleHashes[name] = hash(source);
  const expected = preparation.normalizer_sha256?.[name]
    || preparation.normalizer_sha256?.[`${name}.ts`];
  if (!expected || moduleHashes[name] !== expected) throw new Error('Normalizer snapshot drift: ' + name);
  modules.set(name, ts.transpileModule(source, { compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022,
  }}).outputText);
}
const sourceRoot = await fsp.realpath(pack.source_root);
const inventoryStarted = performance.now();
const files = [];
const inventory = [];
const assetIds = new Set();
for (const asset of pack.assets) {
  if (typeof asset.relative_path !== 'string' || path.isAbsolute(asset.relative_path)) {
    throw new Error('Source paths must be relative to the pack');
  }
  const filename = await fsp.realpath(path.resolve(sourceRoot, asset.relative_path));
  if (!filename.startsWith(sourceRoot + path.sep)) throw new Error('Source escaped its pack');
  const bytes = await fsp.readFile(filename);
  const digest = hash(bytes);
  if (digest !== asset.sha256) throw new Error('Source drift: ' + asset.relative_path);
  const assetId = asset.asset_id || stableUuid(digest + '|' + asset.relative_path);
  if (typeof assetId !== 'string' || assetIds.has(assetId)) throw new Error('Invalid or duplicate asset ID');
  assetIds.add(assetId);
  files.push(filename);
  inventory.push({ relative_path: asset.relative_path, sha256: digest,
    bytes: bytes.length, asset_id: assetId });
}
const inventoryMs = performance.now() - inventoryStarted;
await fsp.mkdir(path.dirname(destination), { recursive: true });
await fsp.mkdir(destination);
const writeJson = (filename, value) => fsp.writeFile(path.join(destination, filename),
  JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
const savedFrames = [];
const server = http.createServer((request, response) => {
  const route = new URL(request.url, 'http://localhost').pathname;
  if (route === '/') {
    response.setHeader('Content-Type', 'text/html; charset=utf-8');
    response.end('<!doctype html><title>Codex isolated V1.66 evidence</title><input type="file" multiple><script type="module">window.mediaReady=import("/media-evidence");</script>');
    return;
  }
  const name = route.slice(1).replace(/\.(?:js|ts)$/, '');
  if (!modules.has(name)) { response.writeHead(404); response.end(); return; }
  response.setHeader('Content-Type', 'text/javascript; charset=utf-8');
  response.end(modules.get(name));
});
let browser;
let metrics = { status: 'PREPARATION_FAILED' };
let manifestDigest = null;
const browserStarted = performance.now();
try {
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch({ channel: 'chrome', headless: true,
    args: ['--disable-background-networking'] });
  const page = await browser.newPage();
  // Only the loopback snapshot server is reachable from this preparation page.
  await page.route('**/*', route => new URL(route.request().url()).origin === origin
    ? route.continue() : route.abort('blockedbyclient'));
  await page.exposeFunction('saveEvidence', async (relative, encoded) => {
    const target = path.resolve(destination, relative);
    if (!target.startsWith(destination + path.sep) || !relative.startsWith('evidence/')) {
      throw new Error('Invalid evidence output path');
    }
    const bytes = Buffer.from(encoded, 'base64');
    await fsp.mkdir(path.dirname(target), { recursive: true });
    await fsp.writeFile(target, bytes, { flag: 'wx' });
    savedFrames.push({ relative_path: relative, sha256: hash(bytes), bytes: bytes.length });
  });
  await page.exposeFunction('reportPreparation', data => console.log(JSON.stringify({ packId, round, ...data })));
  await page.goto(origin + '/');
  await page.locator('input').setInputFiles(files);
  const result = await page.evaluate(async config => {
    const { inspectFiles, buildEvidenceBundle } = await window.mediaReady;
    const preparationStarted = performance.now();
    const assets = await inspectFiles(Array.from(document.querySelector('input').files));
    const inspectedMs = performance.now() - preparationStarted;
    assets.forEach((asset, index) => {
      asset.id = config.assetIds[index];
      asset.name = config.names[index];
    });
    const failures = assets.filter(asset => asset.decodeStatus !== 'READY')
      .map(asset => ({ name: asset.name, reason: asset.decodeMessage }));
    if (failures.length) return { status: 'DECODE_FAILED', failures, inspectedMs };
    let lastIndex = -1;
    const bundleStarted = performance.now();
    const bundle = await buildEvidenceBundle(assets, (done, total, label) => {
      if (Math.floor(done) !== lastIndex) {
        lastIndex = Math.floor(done);
        window.reportPreparation({ stage: 'EVIDENCE_PREPARATION', done: lastIndex, total, label });
      }
    });
    const buildEvidenceMs = performance.now() - bundleStarted;
    if (bundle.manifest.bundle_version !== 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04'
      || bundle.manifest.normalization.spatial_transform !== 'ASPECT_FIT_LETTERBOX'
      || bundle.manifest.normalization.width !== 768 || bundle.manifest.normalization.height !== 1024) {
      throw new Error('Snapshot did not produce the V04 full-frame letterbox contract');
    }
    // Export metadata is fixed for repeat comparability; never treated as capture time.
    bundle.manifest.session.session_id = config.sessionId;
    bundle.manifest.session.exported_at = config.exportedAt;
    bundle.manifest.device.device_id = config.deviceId;
    const saveStarted = performance.now();
    for (const frame of bundle.frames) {
      const bytes = new Uint8Array(await frame.blob.arrayBuffer());
      let binary = '';
      for (let index = 0; index < bytes.length; index += 8192) {
        binary += String.fromCharCode(...bytes.subarray(index, index + 8192));
      }
      await window.saveEvidence(frame.relativePath, btoa(binary));
    }
    return { status: 'READY', manifest: bundle.manifest, inspectedMs, buildEvidenceMs,
      evidenceSaveMs: performance.now() - saveStarted,
      browserPreparationMs: performance.now() - preparationStarted,
      frameCount: bundle.frames.length, evidenceBytes: bundle.evidenceBytes };
  }, {
    assetIds: inventory.map(asset => asset.asset_id), names: inventory.map(asset => asset.relative_path),
    sessionId: pack.session_id, exportedAt: pack.exported_at,
    deviceId: pack.device_id || `web-test-${pack.session_id.slice(0, 8)}`,
  });
  const { manifest, ...preparationMetrics } = result;
  metrics = preparationMetrics;
  if (manifest) {
    if (manifest.assets.length !== inventory.length) throw new Error('Normalizer dropped source assets');
    for (const [index, asset] of manifest.assets.entries()) {
      if (asset.original_sha256 !== inventory[index].sha256 || asset.sequence_index !== index) {
        throw new Error('Normalizer changed source identity or order');
      }
      for (const frame of asset.frames) {
        const saved = savedFrames.find(item => item.relative_path === frame.relative_path);
        if (!saved || saved.sha256 !== frame.sha256 || frame.spatial_transform !== 'ASPECT_FIT_LETTERBOX') {
          throw new Error('Saved evidence differs from manifest');
        }
      }
    }
    if (savedFrames.length !== manifest.assets.reduce((sum, asset) => sum + asset.frames.length, 0)) {
      throw new Error('Evidence cardinality mismatch');
    }
    await writeJson('codex_manifest.json', manifest);
    manifestDigest = hash(await fsp.readFile(path.join(destination, 'codex_manifest.json')));
  }
} catch (error) {
  metrics = { ...metrics, status: 'PREPARATION_FAILED', error: error.message };
  process.exitCode = 1;
} finally {
  const browserVersion = browser?.version() || null;
  if (browser) await browser.close();
  if (server.listening) await new Promise(resolve => server.close(resolve));
  await writeJson('codex_normalization.json', {
    ...metrics, pack_id: packId, round: Number(round), browserVersion, moduleHashes,
    started_at: startedAt, completed_at: new Date().toISOString(),
    preparation_sha256: hash(await fsp.readFile(preparationPath)),
    candidate_sha256: hash(await fsp.readFile(candidatePath)),
    normalizer_source: snapshot, typescriptVersion: ts.version,
    typescriptModuleSha256: hash(await fsp.readFile(typescriptModule)),
    harness_sha256: hash(await fsp.readFile(fileURLToPath(import.meta.url))),
    inventory, sourceInventorySha256: hash(JSON.stringify(inventory)),
    frames: savedFrames, manifest_sha256: manifestDigest, inventoryVerificationMs: inventoryMs,
    browserAndPreparationMs: performance.now() - browserStarted,
    totalPreparationMs: performance.now() - started, captureTimeUsed: false,
    freshDecodeAndExtraction: true, externalNetworkAllowed: false,
    exportedAtMeaning: 'FIXED_EXPORT_METADATA_ONLY_NOT_CAPTURE_TIME',
  });
  console.log(JSON.stringify({ ...metrics, packId, round, destination, manifest_sha256: manifestDigest }));
  if (metrics.status !== 'READY') process.exitCode = 1;
}
