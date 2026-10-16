/** Smoke check for bffUrl rules (no Jest). Run: node scripts/check-bff-url.mjs */
function normalizeBffUrl(raw) {
  const url = String(raw ?? '').trim().replace(/\/+$/, '');
  if (!url) return '';
  if (/REPLACE_WITH_|YOUR_/i.test(url)) return '';
  return url;
}

const cases = [
  ['', ''],
  ['https://api.example.com/', 'https://api.example.com'],
  ['https://REPLACE_WITH_PUBLIC_BFF_HOST', ''],
  ['https://YOUR_HOST.example', ''],
  ['http://192.168.1.2:8790', 'http://192.168.1.2:8790'],
];

let fail = 0;
for (const [input, want] of cases) {
  const got = normalizeBffUrl(input);
  if (got !== want) {
    console.error(`FAIL: ${JSON.stringify(input)} → ${JSON.stringify(got)} want ${JSON.stringify(want)}`);
    fail += 1;
  }
}
if (fail) process.exit(1);
console.log(`OK ${cases.length} bffUrl cases`);
