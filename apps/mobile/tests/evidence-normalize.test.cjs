const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function harness({ platform = 'ios', native = {}, webResult = { uri: 'file:///web.jpg', width:768,height:1024 } } = {}) {
  const copies=[], deletes=[], calls=[];
  const module={exports:{}};
  const code=ts.transpileModule(fs.readFileSync(path.resolve(__dirname,'../src/pipeline/evidenceNormalize.ts'),'utf8'),{
    compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;
  vm.runInNewContext(code,{module,exports:module.exports,require(name){return {
    'expo':{requireOptionalNativeModule:()=>native}, 'react-native':{Platform:{OS:platform}},
    'expo-file-system/legacy':{copyAsync:async x=>copies.push(x),deleteAsync:async x=>deletes.push(x)},
    'expo-image-manipulator':{SaveFormat:{JPEG:'jpeg'},manipulateAsync:async (...x)=>{calls.push(x);return webResult;}},
  }[name];}});
  return {run:(mode='ASPECT_FIT_LETTERBOX',w=1920,h=1080)=>module.exports.writeNormalizedFrame('file:///source.jpg','file:///result.jpg',mode,w,h),copies,deletes,calls};
}
const good={uri:'file:///result.jpg',width:768,height:1024,format:'JPEG',spatialTransform:'ASPECT_FIT_LETTERBOX'};
for(const dims of [[1920,1080],[1080,1920],[1000,1000],[undefined,undefined],[0,0]]) {
  test('iOS uses actual decoded pixels instead of picker size '+dims.join('x'),async()=>{
    const calls=[];
    const h=harness({native:{normalizePhotoEvidenceFrame:async(...args)=>{calls.push(args);return good;}}});
    await h.run('ASPECT_FIT_LETTERBOX',...dims);
    assert.deepEqual(calls,[['file:///source.jpg','file:///result.jpg','ASPECT_FIT_LETTERBOX']]);
    assert.equal(h.calls.length,0);assert.equal(h.copies.length,0);
  });
}
for(const [name,result] of [['missing',undefined],['width',{...good,width:432}],['height',{...good,height:768}],['format',{...good,format:'PNG'}],['destination',{...good,uri:'file:///wrong.jpg'}],['transform',{...good,spatialTransform:'CENTER_CROP_ASPECT_FILL'}]]) {
  test('reject native '+name+' mismatch before a bundle can be built',async()=>{
    const h=harness({native:{normalizePhotoEvidenceFrame:async()=>result}});
    await assert.rejects(h.run,/EVIDENCE_IMAGE_INVALID/);
    assert.deepEqual(h.deletes,['file:///result.jpg']);assert.equal(h.copies.length,0);
  });
}
test('old iOS module fails visibly rather than falling back to a stretched image',async()=>{
  const h=harness();await assert.rejects(h.run,/EVIDENCE_IMAGE_MODULE_MISSING/);assert.equal(h.calls.length,0);
});
test('native decode failure propagates with no fallback write',async()=>{
  const h=harness({native:{normalizePhotoEvidenceFrame:async()=>{throw Error('EVIDENCE_IMAGE_INVALID');}}});
  await assert.rejects(h.run,/EVIDENCE_IMAGE_INVALID/);assert.equal(h.calls.length,0);
});
test('center crop mode is forwarded to native',async()=>{
  const h=harness({native:{normalizePhotoEvidenceFrame:async(s,d,mode)=>({...good,spatialTransform:mode})}});
  await h.run('CENTER_CROP_ASPECT_FILL');
});
test('Web output dimensions must be checked even when extent silently does nothing',async()=>{
  const h=harness({platform:'web',webResult:{uri:'file:///bad.jpg',width:768,height:432}});
  await assert.rejects(h.run,/EVIDENCE_IMAGE_INVALID/);assert.equal(h.copies.length,0);
});
test('Web valid output is copied, Android does not claim Web-only letterboxing',async()=>{
  const h=harness({platform:'web'});await h.run();assert.equal(h.copies.length,1);
  await assert.rejects(harness({platform:'android'}).run,/EVIDENCE_IMAGE_MODULE_MISSING/);
});
