// Isolated experiment adapter: execute unchanged Web normalization, not a new policy.
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [variant, packId = '1'] = process.argv.slice(2);
if (!['baseline', 'candidate'].includes(variant) || !['1', '2', '3'].includes(packId)) {
  throw new Error('Usage: node tools/codex_prepare_full_run_evidence.mjs baseline|candidate 1|2|3');
}
const area = path.join(root, 'var/codex_content_handoff_ab_v1_47');
const preparation = JSON.parse(fs.readFileSync(path.join(area, 'codex_preparation_manifest.json')));
const pack = preparation.packs.find(p => p.pack_id === packId);
const destination = path.join(area, `codex_v1_48_person${packId}`, variant);
const web = process.env.CODEX_WEB_ROOT || path.resolve(root, '../apps/eval-web');
const requireWeb = createRequire(path.join(web, 'package.json'));
const ts = requireWeb('typescript');
const runtime = process.env.CODEX_FULL_RUN_NODE_DEPENDENCIES;
if (!runtime) throw new Error('Set CODEX_FULL_RUN_NODE_DEPENDENCIES to a Node dependency directory containing Playwright');
const { chromium } = createRequire(path.join(runtime, 'package.json'))('playwright');
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const stableUuid = value => {
  const h = hash(value);
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-4${h.slice(13, 16)}-8${h.slice(17, 20)}-${h.slice(20, 32)}`;
};

if (fs.existsSync(destination) && fs.readdirSync(destination).length) throw new Error('Refusing to overwrite existing experiment evidence');
if (hash(fs.readFileSync(path.resolve(root, preparation.normalizer_reference.path))) !== preparation.normalizer_reference.sha256) {
  throw new Error('Normalizer source drifted');
}
const files = pack.assets.map(asset => {
  const filename = path.join(pack.source_root, asset.relative_path);
  if (hash(fs.readFileSync(filename)) !== asset.sha256) throw new Error('Source drift: ' + asset.relative_path);
  return filename;
});
await fsp.mkdir(destination, { recursive: true });
const moduleNames = new Set(['media-evidence', 'result-contract', 'research-run-control']);
const moduleHashes = {};
const server = http.createServer((request, response) => {
  const route = new URL(request.url, 'http://localhost').pathname;
  if (route === '/') {
    response.setHeader('Content-Type', 'text/html; charset=utf-8');
    response.end('<!doctype html><title>Codex isolated evidence preparation</title><input type="file" multiple><script type="module">window.mediaReady=import("/media-evidence");</script>');
    return;
  }
  const name = route.slice(1);
  if (!moduleNames.has(name)) { response.writeHead(404); response.end(); return; }
  const source = fs.readFileSync(path.join(web, 'app/lib', name + '.ts'), 'utf8');
  moduleHashes[name] = hash(source);
  const compiled = ts.transpileModule(source, { compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022,
  }}).outputText;
  response.setHeader('Content-Type', 'text/javascript; charset=utf-8');
  response.end(compiled);
});
await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
let browser;
try {
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage();
  await page.exposeFunction('saveEvidence', async (relative, encoded) => {
    const target = path.resolve(destination, relative);
    if (!target.startsWith(destination + path.sep) || !relative.startsWith('evidence/')) throw new Error('Invalid output path');
    await fsp.mkdir(path.dirname(target), { recursive: true });
    await fsp.writeFile(target, Buffer.from(encoded, 'base64'), { flag: 'wx' });
  });
  await page.exposeFunction('reportPreparation', data => console.log(JSON.stringify(data)));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.locator('input').setInputFiles(files);
  const result = await page.evaluate(async config => {
    const { inspectFiles, buildEvidenceBundle } = await window.mediaReady;
    const started = performance.now();
    const assets = await inspectFiles(Array.from(document.querySelector('input').files));
    const inspectedMs = performance.now() - started;
    assets.forEach((asset, i) => { asset.id = config.assetIds[i]; asset.name = config.names[i]; });
    const failures = assets.filter(a => a.decodeStatus !== 'READY').map(a => ({ name: a.name, reason: a.decodeMessage }));
    if (failures.length) return { status: 'DECODE_FAILED', failures, inspectedMs };
    let lastIndex = -1;
    const bundle = await buildEvidenceBundle(assets, (done, total, label) => {
      if (Math.floor(done) !== lastIndex) {
        lastIndex = Math.floor(done);
        window.reportPreparation({ stage: 'EVIDENCE_PREPARATION', done: lastIndex, total, label });
      }
    });
    bundle.manifest.session.session_id = config.sessionId;
    bundle.manifest.device.device_id = `web-test-${config.sessionId.slice(0, 8)}`;
    for (const frame of bundle.frames) {
      const bytes = new Uint8Array(await frame.blob.arrayBuffer());
      let binary = '';
      for (let i = 0; i < bytes.length; i += 8192) binary += String.fromCharCode(...bytes.subarray(i, i + 8192));
      await window.saveEvidence(frame.relativePath, btoa(binary));
    }
    return { status: 'READY', manifest: bundle.manifest, inspectedMs,
      totalMs: performance.now() - started, frameCount: bundle.frames.length,
      evidenceBytes: bundle.evidenceBytes };
  }, {
    assetIds: pack.assets.map(a => stableUuid(a.sha256 + '|' + a.relative_path)),
    names: pack.assets.map(a => a.relative_path),
    sessionId: stableUuid('codex-v148-pack-' + pack.inventory_sha256),
  });
  const { manifest, ...metrics } = result;
  if (manifest) await fsp.writeFile(path.join(destination, 'codex_manifest.json'), JSON.stringify(manifest, null, 2), { flag: 'wx' });
  await fsp.writeFile(path.join(destination, 'codex_normalization.json'), JSON.stringify({
    ...metrics, variant, packId, browserVersion: browser.version(), moduleHashes,
    sourceInventorySha256: pack.inventory_sha256, captureTimeUsed: false,
  }, null, 2), { flag: 'wx' });
  console.log(JSON.stringify({ ...metrics, variant, destination }));
  if (result.status !== 'READY') process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
