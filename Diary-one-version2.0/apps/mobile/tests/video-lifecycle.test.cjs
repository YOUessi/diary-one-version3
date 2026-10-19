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
        if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx };
        if (name === '../theme') return { colors: {}, spacing: {} };
        if (name === 'react-native') return { View: 'View', Text: 'Text', Pressable: 'Pressable', StyleSheet: { create: s => s },
          AppState: { addEventListener(event, callback) { const remove = navigation.addListener('appState', callback); return { remove }; } } };
        if (name === '@react-navigation/native') return { useNavigation: () => navigation,
          useFocusEffect(callback) { React.useEffect(callback, [callback]); } };
        if (name === 'expo-video') return { VideoView: 'VideoView', useVideoPlayer(uri, setup) {
          return load(lifecyclePath).useReleasingSharedObjectWithLifecycle({ factory() {
            let released = false;
            const p = { uri, plays: 0, pauses: 0, releases: 0, failure: undefined,
              play() { if (released) throw Error('Unable to find native shared object'); if (p.failure) throw p.failure; p.plays++; },
              pause() { if (released) throw Error('Unable to find native shared object'); if (p.failure) throw p.failure; p.pauses++; },
              release() { if (!released) { released = true; p.releases++; } },
              addListener(event, callback) { const remove = navigation.addListener(event, callback); return { remove }; },
              get currentTime() { if (released) throw Error('Unable to find native shared object'); return 1; },
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
