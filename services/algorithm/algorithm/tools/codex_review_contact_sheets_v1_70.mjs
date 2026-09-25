// Local-only layout of unchanged evidence images for human/assistant inspection.
// No image generation, semantic changes, API calls or editing of source frames.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pack = process.argv[2];
if (!['1', '2', '3'].includes(pack)) throw new Error('Use an explicit pack');
const directory = path.join(root, `var/codex_v1_70_full_chain_execution/pack_${pack}/round_1`);
const destination = path.join(directory, 'codex_visual_review');
if (fs.existsSync(destination)) throw new Error('Never overwrite a visual review');
const manifest = JSON.parse(fs.readFileSync(path.join(directory, 'codex_manifest.json'), 'utf8'));
const frames = manifest.assets.flatMap(a => a.frames.map((f, index) => ({...f,
  asset_index: a.sequence_index + 1, frame_index: index + 1, source: path.join(directory, f.relative_path)})));
for (const f of frames) {
  if (crypto.createHash('sha256').update(fs.readFileSync(f.source)).digest('hex') !== f.sha256) throw new Error('Frame drift');
}
const playwrightPackage = process.env.CODEX_PLAYWRIGHT_PACKAGE_JSON;
if (!playwrightPackage) throw new Error('Set CODEX_PLAYWRIGHT_PACKAGE_JSON to a package.json that can resolve Playwright');
const { chromium } = createRequire(playwrightPackage)('playwright');
const browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--disable-background-networking']});
const outputs = [];
try {
  fs.mkdirSync(destination);
  const page = await browser.newPage({viewport: {width: 924, height: 1216}, deviceScaleFactor: 1});
  await page.route('**/*', r => r.abort());
  for (let start = 0; start < frames.length; start += 12) {
    const group = frames.slice(start, start + 12);
    await page.setContent(`<body style="margin:0;background:#fff;font:16px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,300px);gap:8px;padding:8px">${group.map(f => `<section style="height:290px;background:#eee;text-align:center"><div>Pack ${pack} / Asset ${f.asset_index} / Frame ${f.frame_index}</div><img style="width:298px;height:265px;object-fit:contain" src="data:image/jpeg;base64,${fs.readFileSync(f.source).toString('base64')}"></section>`).join('')}</div></body>`);
    await page.evaluate(async () => {await Promise.all([...document.images].map(i => i.decode()));});
    const name = `codex_sheet_${String(start / 12 + 1).padStart(2, '0')}.png`;
    await page.screenshot({path: path.join(destination, name)});
    outputs.push({file: name, frames: group.map(({source, ...f}) => f)});
  }
  fs.writeFileSync(path.join(destination, 'codex_sheet_index.json'), JSON.stringify({pack, note: 'Unchanged frames arranged for inspection; not semantic labels', outputs}, null, 2), {flag: 'wx'});
  console.log(JSON.stringify({pack, frames: frames.length, sheets: outputs.length, directory: destination}));
} finally { await browser.close(); }
