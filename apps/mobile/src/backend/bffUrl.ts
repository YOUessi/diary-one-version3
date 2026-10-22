/**
 * Normalize / validate Production BFF base URL (ACC03 / SYS02).
 * Rejects eas.json placeholders so OTP / upload never hit garbage hosts.
 */
export function normalizeBffUrl(raw: string): string {
  const url = raw.trim().replace(/\/+$/, '');
  if (!url) return '';
  if (/REPLACE_WITH_|YOUR_/i.test(url)) return '';
  return url;
}

export function resolveConfiguredBffUrl(opts: {
  storeUrl?: string;
  envUrl?: string;
  envAlias?: string;
}): string {
  const candidates = [opts.storeUrl, opts.envUrl, opts.envAlias];
  for (const c of candidates) {
    const n = normalizeBffUrl(c ?? '');
    if (n) return n;
  }
  return '';
}
