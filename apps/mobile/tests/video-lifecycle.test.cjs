const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
// Execute installed Expo shared-object lifecycle and actual app component.
// Native handle is a strict test double: access after release throws.
function playerHarness(componentName) {
  const slots = [], pendingEffects = new Set(), players = [], intervals = new Map(), subscriptions = new Map();
  let cursor = 0, nextTimer = 1, tree, component, props, pendingRender = false;
  const sameDeps = (a, b) => a && b && a.length === b.length && a.every((v, i) => Object.is(v, b[i]));
  const React = {
    useRef(initial) { const i = cursor++; if (!slots[i]) slots[i] = { current: initial }; return slots[i]; },
    useMemo(create, deps) { const i = cursor++; if (!slots[i] || !sameDeps(slots[i].deps, deps)) slots[i] = { deps, value: create() }; return slots[i].value; },
    useCallback(fn, deps) { return React.useMemo(() => fn, deps); },
    useState(initial) { const i = cursor++; if (!slots[i]) slots[i] = { value: typeof initial === 'function' ? initial() : initial };
      return [slots[i].value, value => { slots[i].value = typeof value === 'function' ? value(slots[i].value) : value; pendingRender = true; }]; },
    useEffect(create, deps) { const i = cursor++, previous = slots[i]; if (!previous || !sameDeps(previous.deps, deps)) {
      slots[i] = { ...previous, deps, create }; pendingEffects.add(i);
    } },
  };
  const jsx = (type, props) => ({ type, props: props || {} });
  const navigation = { addListener(event, callback) { const id = Symbol(); subscriptions.set(id, { event, callback }); return () => subscriptions.delete(id); } };
  const modules = new Map();
  const lifecyclePath = path.join(root, 'node_modules/expo-modules-core/src/hooks/useReleasingSharedObjectWithLifecycle.ts');
  function load(filename) {
    if (modules.has(filename)) return modules.get(filename).exports;
    const module = { exports: {} }; modules.set(filename, module);
    const compiled = ts.transpileModule(fs.readFileSync(filename, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true } }).outputText;
    vm.runInNewContext(compiled, { module, exports: module.exports, console,
      setInterval(fn) { const id = nextTimer++; intervals.set(id, fn); return id; }, clearInterval(id) { intervals.delete(id); },
      require(name) {
        if (name === 'react') return React;
        if (name.endsWith('/store/useAppStore')) return { useAppStore: selector => selector({ language: 'zh-Hans' }) };
        if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx };
        if (name === '../theme') return { colors: {}, spacing: {}, layout: { heroHome: 198 } };
        if (name === 'react-native') return { View: 'View', Text: 'Text', Pressable: 'Pressable', StyleSheet: { create: s => s },
          AppState: { addEventListener(event, callback) { const remove = navigation.addListener('appState', callback); return { remove }; } } };
        if (name === '@react-navigation/native') return { useNavigation: () => navigation,
          useFocusEffect(callback) { React.useEffect(callback, [callback]); } };
        if (name === 'expo-video') return { VideoView: 'VideoView', useVideoPlayer(uri, setup) {
          return load(lifecyclePath).useReleasingSharedObjectWithLifecycle({ factory() {
            let released = false, currentTime = 0;
            const p = { uri, plays: 0, pauses: 0, releases: 0, failure: undefined, playing: false,
              play() { if (released) throw Error('Unable to find native shared object'); if (p.failure) throw p.failure; p.plays++; },
              pause() { if (released) throw Error('Unable to find native shared object'); if (p.failure) throw p.failure; p.pauses++; },
              release() { if (!released) { released = true; p.releases++; } },
              addListener(event, callback) { const remove = navigation.addListener(event, callback); return { remove }; },
              get currentTime() { if (released) throw Error('Unable to find native shared object'); return currentTime; },
              set currentTime(value) { if (released) throw Error('Unable to find native shared object'); currentTime = value; },
              get duration() { if (released) throw Error('Unable to find native shared object'); return 10; },
              get released() { return released; },
            };
            setup?.(p); players.push(p); return p;
          } }, [uri]);
        } };
        if (/\/i18n$/.test(name)) return { t: value => value, useLocale() {} };
        if (name.startsWith('.')) {
          const base = path.resolve(path.dirname(filename), name);
          return load(base + (fs.existsSync(base + '.ts') ? '.ts' : '.tsx'));
        }
        throw Error('Unmocked player dependency: ' + name);
      },
    }, { filename });
    return module.exports;
  }
  function render(nextProps) {
    props = nextProps; cursor = 0; pendingRender = false; tree = component(props);
    const effects = Array.from(pendingEffects); pendingEffects.clear();
    for (const i of effects) slots[i].cleanup?.();
    for (const i of effects) slots[i].cleanup = slots[i].create();
    return tree;
  }
  component = load(path.join(root, `src/components/${componentName}.tsx`))[componentName];
  return { players, intervals, render, get tree() { return tree; },
    rerender() { if (pendingRender) render(props); },
    emit(event, value) { for (const s of Array.from(subscriptions.values())) if (s.event === event) s.callback(value); },
    unmount({ repeatCleanup = false } = {}) { const cleanup = slots.filter(s => s?.cleanup).map(s => s.cleanup); for (const fn of cleanup) fn(); if (repeatCleanup) for (const fn of cleanup) fn(); },
  };
}

function nodes(node) {
  return !node || typeof node !== 'object' ? [] : [node, ...[node.props?.children].flat(Infinity).flatMap(nodes)];
}
function control(h, label) {
  return nodes(h.tree).find(n => n.type === 'Pressable' && n.props.accessibilityLabel === label);
}

test('native fullscreen keeps the same source and seek; native pause/mute are reflected inline', async () => {
  const h = playerHarness('VideoPlayback');
  h.render({ uri: 'file:///highlight.mp4', initialPositionSec: 4.5 });
  h.emit('sourceLoad', { duration: 10 }); h.rerender();
  const p = h.players[0];
  p.currentTime = 6.25;
  const view = nodes(h.tree).find(n => n.type === 'VideoView');
  let presentations = 0;
  view.props.ref.current = { enterFullscreen: async () => { presentations++; } };
  await control(h, '全屏查看视频').props.onPress();
  assert.equal(presentations, 1);
  assert.equal(h.players.length, 1);
  assert.equal(p.currentTime, 6.25);
  assert.equal(view.props.player, p);
  assert.equal(view.props.contentFit, 'contain');
  view.props.onFullscreenEnter(); h.rerender();
  assert.equal(nodes(h.tree).find(n => n.type === 'VideoView').props.nativeControls, true,
    'iOS fullscreen explicitly enables native controls, including close');
  p.currentTime = 8; p.playing = true;
  h.emit('playingChange', { isPlaying: true }); h.rerender();
  assert.ok(control(h, '暂停视频'), 'native play updates inline button');
  p.currentTime = 3; p.playing = false; p.muted = true;
  view.props.onFullscreenExit(); h.rerender();
  assert.equal(nodes(h.tree).find(n => n.type === 'VideoView').props.nativeControls, false);
  assert.equal(p.currentTime, 3, 'return does not reset highlight position');
  assert.ok(control(h, '播放视频'));
  assert.equal(control(h, '播放进度').props.accessibilityValue.now, 3);
  assert.ok(nodes(h.tree).some(n => n.type === 'Text' && n.props.children === '开启声音'));
  h.unmount();
});

test('fullscreen repeated taps and failed presentation do not reset or release playback', async () => {
  const h = playerHarness('VideoPlayback'); h.render({ uri: 'file:///a.mp4', initialPositionSec: 2 });
  const p = h.players[0];
  const view = nodes(h.tree).find(n => n.type === 'VideoView');
  let calls = 0, reject;
  view.props.ref.current = { enterFullscreen: () => { calls++; return new Promise((resolve, fail) => { reject = fail; }); } };
  const first = control(h, '全屏查看视频').props.onPress();
  await control(h, '全屏查看视频').props.onPress();
  assert.equal(calls, 1);
  reject(Error('Presentation unavailable'));
  await first; h.rerender();
  assert.ok(nodes(h.tree).some(n => n.props.accessibilityRole === 'alert'));
  assert.equal(p.currentTime, 2); assert.equal(p.releases, 0);
  view.props.ref.current = { enterFullscreen: async () => { calls++; } };
  await control(h, '全屏查看视频').props.onPress(); h.rerender();
  assert.equal(calls, 2);
  assert.ok(!nodes(h.tree).some(n => n.props.accessibilityRole === 'alert'));
  h.emit('statusChange', { status: 'error' }); h.rerender();
  assert.equal(control(h, '全屏查看视频').props.disabled, true);
  await control(h, '全屏查看视频').props.onPress();
  assert.equal(calls, 2);
  h.unmount();
});


for (const autoPlay of [false, true]) {
  test(`unmount autoplay=${autoPlay}: no call after Expo releases handle`, () => {
    const h = playerHarness('VideoPlayback'); h.render({ uri: 'file:///a.mp4', autoPlay });
    h.unmount({ repeatCleanup: true }); assert.equal(h.players[0].releases, 1);
  });
  test(`source replacement autoplay=${autoPlay}: old handle released safely`, () => {
    const h = playerHarness('VideoPlayback'); h.render({ uri: 'file:///a.mp4', autoPlay });
    h.render({ uri: 'file:///b.mp4', autoPlay });
    assert.equal(h.players[0].releases, 1); assert.equal(h.players[1].released, false); h.unmount();
  });
}
test('screen blur and app background pause only while handle is live', () => {
  const h = playerHarness('VideoPlayback'); h.render({ uri: 'file:///a.mp4', autoPlay: true });
  const before = h.players[0].pauses; h.emit('blur'); assert.ok(h.players[0].pauses > before);
  h.emit('appState', 'background'); assert.ok(h.players[0].pauses > before + 1);
  h.unmount(); h.emit('blur'); h.emit('appState', 'background');
});

test('focus seeks once, preserves manual scrubbing, resets for another source, and replays from focus', () => {
  const h = playerHarness('VideoPlayback');
  h.render({ uri: 'file:///highlight.mp4', autoPlay: true, initialPositionSec: 4.5 });
  assert.equal(h.players[0].currentTime, 4.5);
  h.emit('sourceLoad', { duration: 10 }); h.rerender();
  h.players[0].currentTime = 7;
  h.emit('timeUpdate', { currentTime: 7 }); h.rerender();
  h.emit('sourceLoad', { duration: 10 }); h.rerender();
  assert.equal(h.players[0].currentTime, 7);
  h.emit('playToEnd'); h.rerender();
  function all(node) { return !node || typeof node !== 'object' ? [] : [node, ...[node.props?.children].flat(Infinity).flatMap(all)]; }
  all(h.tree).find(n => n.type === 'Pressable' && n.props.accessibilityLabel === '重播视频').props.onPress();
  assert.equal(h.players[0].currentTime, 4.5);
  h.render({ uri: 'file:///other.mp4', autoPlay: true, initialPositionSec: 2 });
  assert.equal(h.players[0].releases, 1); assert.equal(h.players[1].currentTime, 2);
  h.unmount();
});
for (const [requested, expected] of [[NaN, 0], [-3, 0], [Infinity, 0], [99, 9.95], [0, 0]]) {
  test(`focus defense for initial position ${requested}`, () => {
    const h = playerHarness('VideoPlayback'); h.render({ uri: 'file:///a.mp4', initialPositionSec: requested });
    h.emit('sourceLoad', { duration: 10 }); h.rerender();
    assert.equal(h.players[0].currentTime, expected); h.unmount();
  });
}
