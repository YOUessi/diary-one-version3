// Actual TS storage/resolution, real temporary files and real SQLite; no native UI or cloud.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { DatabaseSync } = require('node:sqlite');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
const oldId = '11111111-1111-4111-8111-111111111111', newId = '22222222-2222-4222-8222-222222222222';
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const filePath = uri => decodeURIComponent(uri.replace(/^file:\/\//, ''));
function harness(t) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'diary-media-'));
  const base = `file://${temp}/Containers/Data/Application/`;
  const oldDocuments = `${base}${oldId}/Documents/`, documents = `${base}${newId}/Documents/`;
  const cache = `${base}${newId}/Library/Caches/`;
  const calls = { copied: [], moved: [], deleted: [] }, faults = {};
  const adapter = {
    documentDirectory: documents, cacheDirectory: cache, EncodingType: { Base64: 'base64' },
    getInfoAsync: async uri => { try { const info = fs.statSync(filePath(uri)); return { exists: true, isDirectory: info.isDirectory() }; } catch { return { exists: false }; } },
    makeDirectoryAsync: async uri => fs.mkdirSync(filePath(uri), { recursive: true }),
    copyAsync: async ({ from, to }) => { calls.copied.push({ from, to }); fs.copyFileSync(filePath(from), filePath(to)); await faults.copy?.(to); },
    moveAsync: async ({ from, to }) => { calls.moved.push({ from, to }); fs.renameSync(filePath(from), filePath(to)); },
    deleteAsync: async uri => { calls.deleted.push(uri); fs.rmSync(filePath(uri), { force: true, recursive: true }); },
    readAsStringAsync: async (uri, opts) => fs.readFileSync(filePath(uri), opts?.encoding === 'base64' ? 'base64' : 'utf8'),
    writeAsStringAsync: async (uri, value) => fs.writeFileSync(filePath(uri), value),
  };
  const db = new DatabaseSync(':memory:');
  const sql = { execAsync: async query => db.exec(query),
    getFirstAsync: async (query, ...args) => db.prepare(query).get(...args),
    getAllAsync: async (query, ...args) => db.prepare(query).all(...args),
    withExclusiveTransactionAsync: async callback => { db.exec("BEGIN"); try { await callback(sql); db.exec("COMMIT"); } catch (e) { db.exec("ROLLBACK"); throw e; } },
    runAsync: async (query, ...args) => db.prepare(query).run(...(Array.isArray(args[0]) ? args[0] : args)) };
  const modules = new Map();
  function load(relative) {
    const filename = path.resolve(root, relative);
    if (modules.has(filename)) return modules.get(filename).exports;
    const module = { exports: {} }; modules.set(filename, module);
    const code = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true } }).outputText;
    vm.runInNewContext(code, { module, exports: module.exports, Date, AbortController, atob, Uint8Array, ArrayBuffer,
      require(name) {
        if (name === 'expo-file-system/legacy') return adapter;
        if (name === 'expo-file-system') return { File: class {
          constructor(uri) { this.uri = uri; }
          async bytes() { return fs.readFileSync(filePath(this.uri)); }
        } };
        if (name === 'expo-sqlite') return { openDatabaseAsync: async () => sql };
        if (name === 'expo-crypto') return { randomUUID: crypto.randomUUID, CryptoDigestAlgorithm: { SHA256: 'sha256' }, digest: async (algo, bytes) => Uint8Array.from(crypto.createHash(algo).update(bytes).digest()).buffer };
        if (name === './evidenceNormalize') return { EVIDENCE_FRAME: { width: 768, height: 1024 }, writeNormalizedFrame: async (source, dest) => fs.copyFileSync(filePath(source), filePath(dest)) };
        if (name === '../evidence/runSemanticVideoEvidence') return {};
        if (name.startsWith('.')) return load(path.relative(root, path.resolve(path.dirname(filename), name + '.ts')));
        throw Error('Unmocked ' + name);
      },
    }, { filename });
    return module.exports;
  }
  function write(uri, value) { fs.mkdirSync(path.dirname(filePath(uri)), { recursive: true }); fs.writeFileSync(filePath(uri), value); }
  t.after(() => { db.close(); fs.rmSync(temp, { recursive: true, force: true }); });
  return { base, oldDocuments, documents, cache, adapter, load, calls, faults, write, db };
}


test('real SQLite stores relative managed URIs and restores after sandbox relocation', async t => {
 const h=harness(t),api=h.load('src/db/sqlite.ts');await api.initDatabase();
 const dir=h.documents+'bundles/bundle-task/',frame=dir+'frames/a.jpg',video=dir+'sources/a.mp4';
 await api.saveSnapshot({...api.emptySnapshot(),chapters:[{id:'c',heroUri:frame,yourStory:'keep file:///notes',moments:[{posterUri:frame,playbackUri:video}]}],pipelineTasks:[{id:'task',bundleDir:dir,bundleJsonPath:dir+'bundle.json'}]});
 const raw=JSON.parse(h.db.prepare('SELECT json FROM app_snapshot').get().json);
 assert.equal(raw.chapters[0].heroUri,'diary-documents://bundles/bundle-task/frames/a.jpg');
 const newer=h.documents.replace(newId,oldId);h.adapter.documentDirectory=newer;
 const restored=await api.loadSnapshot();assert.equal(restored.chapters[0].heroUri,newer+'bundles/bundle-task/frames/a.jpg');
 assert.equal(restored.chapters[0].moments[0].playbackUri,newer+'bundles/bundle-task/sources/a.mp4');
 assert.equal(restored.pipelineTasks[0].bundleJsonPath,newer+'bundles/bundle-task/bundle.json');assert.equal(restored.chapters[0].yourStory,'keep file:///notes');
});
test('legacy absolute snapshot recovers only proven bundle roots and leaves unrelated paths alone',async t=>{
 const h=harness(t),api=h.load('src/db/sqlite.ts');await api.initDatabase();const dir=h.oldDocuments+'bundles/bundle-task/';
 const snapshot={...api.emptySnapshot(),chapters:[{id:'c',heroUri:dir+'frames/a.jpg',moments:[{playbackUri:'file:///unrelated/a.mp4'}]}],pipelineTasks:[{id:'task',bundleDir:dir,bundleJsonPath:dir+'bundle.json'}]};
 h.db.prepare('INSERT INTO app_snapshot(id,json,updated_at) VALUES(1,?,?)').run(JSON.stringify(snapshot),'now');
 const restored=await api.loadSnapshot();assert.equal(restored.chapters[0].heroUri,h.documents+'bundles/bundle-task/frames/a.jpg');assert.equal(restored.chapters[0].moments[0].playbackUri,'file:///unrelated/a.mp4');
});
for(const fault of ['guard_before','guard_after','missing_asset_hash'])test('SQLite publication rollback '+fault,async t=>{
 const h=harness(t),api=h.load('src/db/sqlite.ts');await api.initDatabase();await api.saveSnapshot({...api.emptySnapshot(),chapters:[{id:'prior'}]});
 let calls=0;const guard=()=>{calls++;if((fault==='guard_before'&&calls===1)||(fault==='guard_after'&&calls===2))throw Error('account changed');};
 await assert.rejects(api.saveSnapshot({...api.emptySnapshot(),chapters:[{id:'incoming'}]},guard,[{asset_id:'a',original_sha256:fault==='missing_asset_hash'?undefined:hash('video')} ]));
 assert.equal((await api.loadSnapshot()).chapters[0].id,'prior');assert.equal(h.db.prepare('SELECT COUNT(*) n FROM raw_assets').get().n,0);
});
test('corrupt persisted JSON is an error and never becomes a new empty library',async t=>{
 const h=harness(t),api=h.load('src/db/sqlite.ts');await api.initDatabase();h.db.prepare('INSERT INTO app_snapshot(id,json,updated_at) VALUES(1,?,?)').run('{bad','now');
 await assert.rejects(api.loadSnapshot(),/Could not load saved data/);assert.equal(h.db.prepare('SELECT json FROM app_snapshot').get().json,'{bad');
});

for(const fault of ['none','missing_video','changed_video','changed_frame','legacy_uri'])test('attach exact media with file/hash verification: '+fault,async t=>{
 const h=harness(t),api=h.load('src/pipeline/attachChapterMedia.ts');
 const dir=h.documents+'bundles/bundle-task/',frame=dir+'frames/f.jpg',video=dir+'sources/a.mp4';
 h.write(frame,fault==='changed_frame'?'changed':'frame');
 if(fault!=='missing_video')h.write(video,fault==='changed_video'?'changed':'video');
 h.write(dir+'source_uris.json',JSON.stringify({a:{uri:fault==='legacy_uri'?h.oldDocuments+'bundles/bundle-task/sources/a.mp4':video,media_kind:'VIDEO'}}));
 h.write(dir+'bundle.json',JSON.stringify({assets:[{asset_id:'a',media_kind:'VIDEO',original_sha256:hash('video'),frames:[{frame_id:'f',relative_path:'frames/f.jpg',sha256:hash('frame')}]}]}));
 const run=api.attachChapterMediaFromBundle([{id:'c',moments:[]}],[{id:'c',hero_asset_id:'a',hero_frame_id:'f',selected_media:[{role:'HERO',asset_id:'a',evidence_frame_ids:['f']}]}],dir,dir+'bundle.json');
 if(['none','legacy_uri'].includes(fault))assert.equal((await run)[0].moments[0].playbackUri,video);
 else await assert.rejects(run,/unavailable|bytes changed/);
});

test('managed URI decoder rejects traversal and does not rewrite arbitrary sandbox UUIDs',t=>{
 const h=harness(t),api=h.load('src/pipeline/localMediaPaths.ts');
 for(const bad of ['../private','bundles/bundle-a/../private','bundles/bundle-a/%2e%2e/x','bundles/bundle-a/%252e%252e/x'])assert.throws(()=>api.resolveAppMediaUri('diary-documents://'+bad));
 const other=h.oldDocuments+'bundles/bundle-other/frame.jpg';assert.equal(api.resolveAppMediaUri(other),other);
 assert.equal(api.resolveBundleSourceUri(other,h.documents+'bundles/bundle-task/'),other);
});

test('real SQLITE_FULL rolls back incoming diary and dedupe together',async t=>{
 const h=harness(t),api=h.load('src/db/sqlite.ts');await api.initDatabase();await api.saveSnapshot({...api.emptySnapshot(),chapters:[{id:'prior'}]});
 const pages=h.db.prepare('PRAGMA page_count').get().page_count;h.db.exec('PRAGMA max_page_count='+pages);
 await assert.rejects(api.saveSnapshot({...api.emptySnapshot(),chapters:[{id:'large',aiStory:'x'.repeat(1_000_000)}]},()=>{},[{asset_id:'a',original_sha256:hash('video')}]),/full/i);
 assert.equal((await api.loadSnapshot()).chapters[0].id,'prior');assert.equal(h.db.prepare('SELECT COUNT(*) n FROM raw_assets').get().n,0);
});
