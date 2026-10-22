const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function harness(deviceLinkState, language = 'zh-Hans') {
  const routes = [];
  const state = { deviceLinkState, language, cloudProcessingConsent: false };
  const jsx = (type, props) => ({ type, props: props || {} });
  function load(file) {
    const module = { exports: {} };
    const text = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
      compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX },
    }).outputText;
    vm.runInNewContext(text, { module, exports: module.exports, __DEV__: false,
      require(name) {
        if (name === 'react') return {};
        if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx, Fragment: 'Fragment' };
        if (name === 'react-native') return { Pressable: 'Pressable', ScrollView: 'ScrollView', Text: 'Text', View: 'View', StyleSheet: { create: x => x } };
        if (name === 'react-native-safe-area-context') return { SafeAreaView: 'SafeAreaView' };
        if (name === '@react-navigation/native') return { useNavigation: () => ({ navigate: (...args) => routes.push(args) }) };
        if (name.endsWith('/store/useAppStore')) return { useAppStore: selector => selector(state) };
        if (name.endsWith('/theme')) return { colors: {}, layout: {}, spacing: {}, type: {} };
        if (name.endsWith('/domain/strings')) return load(path.resolve(path.dirname(file), name + '.ts'));
        if (name.includes('/components/')) return new Proxy({}, { get: (_, key) => key });
        throw Error('Unexpected dependency: ' + name);
      },
    }, { filename: file });
    return module.exports;
  }
  const base = path.resolve(__dirname, '../src/screens/onboarding');
  return { routes, state, pairing: () => load(path.join(base, 'pairingScreens.tsx')).PairingStartScreen(),
    legacyPairing: name => load(path.join(base, 'pairingScreens.tsx'))[name](),
    legacyPermission: name => load(path.join(base, 'permissionScreens.tsx'))[name](),
    setup: () => load(path.join(base, 'SetupCompleteScreen.tsx')).default() };
}
for (const state of ['disconnected', 'lab_linked']) {
  test(`restored legacy setup routes never simulate a connected device or a system prompt: ${state}`, () => {
    const h = harness(state);
    for (const name of ['PairingBluetoothPermissionScreen', 'PairingBluetoothDeniedScreen',
      'PairingSearchingScreen', 'PairingFoundScreen', 'PairingConnectingScreen', 'PairingConnectedScreen']) {
      const screen = h.legacyPairing(name);
      assert.equal(screen.props.title, '连接设备');
      assert.match(screen.props.lead, /暂不支持连接设备/);
      screen.props.onPrimary();
      assert.equal(h.routes.at(-1)[0], 'PreferenceSurvey');
    }
    for (const name of ['PermissionBluetoothRequestScreen', 'PermissionLocalNetworkDeniedScreen',
      'PermissionPhotosRequestScreen', 'PermissionNotificationsRequestScreen']) {
      const screen = h.legacyPermission(name);
      assert.equal(screen.props.title, '按需授权');
      assert.match(screen.props.lead, /不会自动授权/);
      screen.props.onPrimary();
      assert.equal(h.routes.at(-1)[0], 'PreferenceSurvey');
    }
    assert.equal(h.state.deviceLinkState, state);
    assert.equal(h.state.cloudProcessingConsent, false);
  });
}
function nodes(tree) {
  if (!tree || typeof tree !== 'object') return [];
  return [tree, ...[tree.props?.children].flat(Infinity).flatMap(nodes)];
}
test('no-device continuation reaches skippable preferences without device permissions or consent changes', () => {
  const h = harness('disconnected');
  h.pairing().props.onSecondary();
  assert.equal(h.routes[0][0], 'PreferenceSurvey');
  assert.equal(h.routes[0][1].step, 'welcome');
  assert.equal(h.state.deviceLinkState, 'disconnected');
  assert.equal(h.state.cloudProcessingConsent, false);
});
for (const state of ['disconnected', 'lab_linked', 'hardware_linked']) {
  test(`setup reports only a real hardware connection: ${state}`, () => {
    const h = harness(state), tree = nodes(h.setup());
    const copy = tree.filter(n => n.type === 'Text').map(n => n.props.children).join(' ');
    assert.equal(copy.includes('Diary One 已连接'), state === 'hardware_linked');
    tree.find(n => n.type === 'Pressable').props.onPress();
    assert.equal(h.routes[0][0], state === 'hardware_linked' ? 'HardwareBasics' : 'PreferenceSurvey');
  });
}
