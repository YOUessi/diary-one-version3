# Preflight for multi-user iOS internal beta (code + env placeholders).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$mobile = Join-Path $root "apps\mobile"
$bff = Join-Path $root "services\bff"
$fail = 0

function Ok($m) { Write-Host "  OK  $m" -ForegroundColor Green }
function Bad($m) { Write-Host "  FIX $m" -ForegroundColor Red; $script:fail++ }
function Warn($m) { Write-Host "  WARN $m" -ForegroundColor Yellow }

Write-Host "=== Diary One internal beta preflight ===" -ForegroundColor Cyan

$eas = Get-Content (Join-Path $mobile "eas.json") -Raw
if ($eas -match 'REPLACE_WITH_PUBLIC_BFF_HOST') {
  Bad "eas.json preview EXPO_PUBLIC_DEV_BFF_URL still placeholder"
} else {
  Ok "eas.json BFF URL looks filled"
}
if ($eas -match '"EXPO_PUBLIC_DEV_BFF_TOKEN":\s*"[^"]+"' -and $eas -notmatch '"EXPO_PUBLIC_DEV_BFF_TOKEN":\s*""') {
  Warn "eas.json preview still has non-empty DEV_BFF_TOKEN - OTP-only is preferred"
} else {
  Ok "eas.json preview token empty (OTP path)"
}

$envFile = Join-Path $bff ".env"
if (-not (Test-Path $envFile)) {
  Bad "services/bff/.env missing"
} else {
  $envText = Get-Content $envFile -Raw
  if ($envText -match 'ALLOW_MOCK_PREVIEW\s*=\s*true') {
    Bad "ALLOW_MOCK_PREVIEW=true"
  } else {
    Ok "ALLOW_MOCK_PREVIEW not true"
  }
  if ($envText -match 'API_TOKEN\s*=\s*dev-token') {
    Bad "API_TOKEN is still dev-token"
  } else {
    Ok "API_TOKEN customized (or unset)"
  }
  if ($envText -match 'SMTP_HOST\s*=\s*\S+') {
    Ok "SMTP_HOST set"
  } else {
    Warn "SMTP_HOST empty - OTP mail needed for many testers"
  }
}

$files = @(
  "apps\mobile\src\cloud\deliveryAdmit.ts",
  "apps\mobile\src\cloud\validatePreviewResult.ts",
  "apps\mobile\src\store\applyDiaryDay.ts",
  "apps\mobile\src\screens\device\DeviceScreen.tsx",
  "apps\mobile\src\backend\resolveProductionBearer.ts",
  "apps\mobile\src\pipeline\launchEvidenceImport.ts"
)

$accountStack = Get-Content (Join-Path $mobile "src\navigation\AccountStack.tsx") -Raw
if ($accountStack -match 'name="SignIn"' -and $accountStack -match 'name="EmailOtp"') {
  Ok "AccountStack SignIn + EmailOtp (beta OTP)"
} else {
  Bad "AccountStack missing SignIn/EmailOtp for beta OTP"
}
foreach ($rel in $files) {
  $p = Join-Path $root $rel
  if (Test-Path $p) { Ok $rel } else { Bad "missing $rel" }
}

$checkUrl = Join-Path $mobile "scripts\check-bff-url.mjs"
if (Test-Path $checkUrl) {
  try {
    node $checkUrl | Out-Null
    if ($LASTEXITCODE -eq 0) { Ok "bffUrl placeholder rules" } else { Bad "bffUrl smoke failed" }
  } catch {
    Warn "node not available for bffUrl smoke"
  }
}

$tunnelScripts = @(
  "services\bff\scripts\start-public-tunnel.ps1",
  "services\bff\scripts\apply-public-bff-url.ps1",
  "services\bff\scripts\prepare-multiuser-beta.ps1"
)
foreach ($rel in $tunnelScripts) {
  $p = Join-Path $root $rel
  if (Test-Path $p) { Ok $rel } else { Bad "missing $rel" }
}

Write-Host ""
Write-Host "Public tunnel helpers (when ready):" -ForegroundColor Cyan
Write-Host "  services/bff/scripts/prepare-multiuser-beta.ps1 -HardenEnv"
Write-Host "  services/bff/scripts/start-public-tunnel.ps1 -ApplyEas"
Write-Host "  services/bff/scripts/apply-public-bff-url.ps1 -Url https://..."

Write-Host ""
if ($fail -gt 0) {
  Write-Host "Result: $fail item(s) to fix before TestFlight blast." -ForegroundColor Red
  Write-Host "Ops checklist: docs/INTERNAL_BETA_OPS_CHECKLIST.md" -ForegroundColor Yellow
  exit 1
}
Write-Host "Result: code preflight green. Still need public HTTPS + eas build." -ForegroundColor Green
Write-Host "Ops checklist: docs/INTERNAL_BETA_OPS_CHECKLIST.md" -ForegroundColor Cyan
