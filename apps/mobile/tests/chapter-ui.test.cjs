// Execute the actual screen functions. Native drawing is separately checked in Simulator.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),ts=require('typescript');
const root=path.resolve(__dirname,'../src');
function harness() {
 const state={language:'zh-Hans',todayStatus:'READY',selectedDateKey:'2026-10-21',chapters:[],smallMemoriesByDate:{},
   historyLoadState:'idle',historyVisibleCount:3,pipelineTasks:[],deviceLinkState:'disconnected'};
 const cache=new Map();
 const jsx=(type,props)=>({type,props:props??{}});
 const react={useMemo:fn=>fn(),useCallback:fn=>fn,useRef:value=>({current:value}),useState:value=>[value,()=>{}]};
 function load(file) {
  if(cache.has(file))return cache.get(file).exports;
  const m={exports:{}};cache.set(file,m);
  const code=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText;
  vm.runInNewContext(code,{module:m,exports:m.exports,console,Intl,Date,
   require(name){
    if(name==='react')return react;
    if(name==='react/jsx-runtime')return {jsx,jsxs:jsx};
    if(name==='react-native')return {View:'View',Text:'Text',Image:'Image',Pressable:'Pressable',ScrollView:'ScrollView',StyleSheet:{create:s=>s}};
    if(name==='react-native-safe-area-context')return {SafeAreaView:'SafeAreaView'};
    if(name==='@react-navigation/native')return {useNavigation:()=>({}),useRoute:()=>({params:{chapterId:'chapter'}}),useFocusEffect:()=>{}};
    if(name.endsWith('/store/useAppStore'))return {useAppStore:selector=>selector(state),
      chaptersForDate:(all,day)=>all.filter(c=>c.dateKey===day),smallMemoriesForDate:(all,day)=>all[day]??[]};
    if(name.endsWith('/theme'))return {colors:{},layout:{},radius:{},spacing:{},type:{}};
    if(name.endsWith('/domain/dayKey'))return {diaryTodayKey:()=> '2026-10-21'};
    const actual=['strings','buildDiaryFeed','model','chapterPresentation','chapterSlides','formatChapterDate','pipelineActive','appSettings'];
    if(actual.includes(path.basename(name)))return load(path.resolve(path.dirname(file),name+'.ts'));
    const id=path.basename(name);return new Proxy({}, {get:(_,prop)=> prop==='__esModule'?true:prop===id&&name.includes('/components/')? id:()=>{}});
   }}, {filename:file});
  return m.exports;
 }
 const render=relative=>load(path.join(root,relative)).default();
 return {state,render,load};
}
function nodes(tree){return !tree||typeof tree!=='object'?[]:[tree,...[tree.props?.children].flat(Infinity).flatMap(nodes)];}
const chapter={id:'chapter',dateKey:'2026-10-21',title:'A grounded title',aiStory:'Detailed original body.',previewStory:'Short grounded preview.',tags:[],detailTags:['Detail'],moments:[]};
test('home renders preview, falls back for legacy data, and supplies historical Aha media',()=>{
 const h=harness();h.state.chapters=[{...chapter}];h.state.smallMemoriesByDate={'2026-10-20':[{id:'a',text:'real small memory',posterUri:'frame.jpg'}]};
 let tree=nodes(h.render('screens/diary/DiaryHomeScreen.tsx'));
 assert.equal(tree.find(n=>n.type==='ChapterBlock').props.aiStory,chapter.previewStory);
 assert.equal(tree.find(n=>n.type==='SmallMemory').props.posterUri,'frame.jpg');
 h.state.chapters[0].previewStory=' ';
 tree=nodes(h.render('screens/diary/DiaryHomeScreen.tsx'));
 assert.equal(tree.find(n=>n.type==='ChapterBlock').props.aiStory,chapter.aiStory);
});
test('detail renders the original highlight at its matching image once and passes focus to playback',()=>{
 const h=harness(),media={id:'m',label:'Moment 1',posterUri:'same.jpg',playbackUri:'right.mp4',capturedByYou:true};
 h.state.chapters=[{...chapter,moments:[media],highlights:[{id:'h',text:'Original highlight',media:[{...media,id:'hm',focusTimeSec:8}]}]}];
 const tree=nodes(h.render('screens/diary/ChapterDetailScreen.tsx'));
 const players=tree.filter(n=>n.type==='MomentMedia');assert.equal(players.length,1);
 assert.equal(players[0].props.playbackUri,'right.mp4');assert.equal(players[0].props.focusTimeSec,8);
 assert.equal(tree.find(n=>n.type==='SmallMemory').props.text,'Original highlight');
 const text=tree.filter(n=>n.type==='Text').map(n=>n.props.children);
 assert.ok(text.includes('由你拍摄'));assert.ok(text.includes('关于这段记忆'));
 h.state.chapters[0].highlights=[{id:'old',text:'Legacy highlight'}];
 assert.ok(nodes(h.render('screens/diary/ChapterDetailScreen.tsx')).some(n=>n.type==='SmallMemory'&&n.props.text==='Legacy highlight'));
});
test('independent Aha remains non-interactive with or without its thumbnail',()=>{
 const h=harness(),component=h.load(path.join(root,'components/SmallMemory.tsx')).SmallMemory;
 for(const posterUri of [undefined,'frame.jpg']){
  const tree=nodes(component({text:'Unchanged original text',posterUri}));
  assert.equal(tree.filter(n=>n.type==='Pressable'||n.props.onPress).length,0);
  assert.equal(tree.filter(n=>n.type==='Image').length,posterUri?1:0);
  assert.ok(tree.some(n=>n.type==='Text'&&n.props.children==='Unchanged original text'));
 }
});
