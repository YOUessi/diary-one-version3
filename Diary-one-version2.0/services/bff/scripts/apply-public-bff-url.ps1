<#
.SYNOPSIS
  Write a public HTTPS BFF base URL into apps/mobile/eas.json preview.env
  (EXPO_PUBLIC_DEV_BFF_URL). Keeps EXPO_PUBLIC_DEV_BFF_TOKEN empty (OTP-only).

.EXAMPLE
  cd E:\AI耳机\diary-one\services\bff
  .\scripts\apply-public-bff-url.ps1 -Url https://xxxx.trycloudflare.com
#>
param(
  [Parameter(Mandatory = $true)][string]$Url,
  [string]$EasJson = ""
)

$ErrorActionPreference = "Stop"

$trimmed = $Url.Trim().TrimEnd("/")
if ($trimmed -notmatch '^https://[A-Za-z0-9._:-]+') {
  Write-Host "FIX: URL must be https://… (got: $trimmed)" -ForegroundColor Red
  exit 1
}
if ($trimmed -match 'REPLACE_WITH_PUBLIC_BFF_HOST|localhost|127\.0\.0\.1|192\.168\.|10\.') {
  Write-Host "WARN: URL looks like placeholder or LAN — TestFlight phones may not reach it." -ForegroundColor Yellow
}

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
if (-not $EasJson) {
  $EasJson = Join-Path $repoRoot "apps\mobile\eas.json"
}
if (-not (Test-Path $EasJson)) {
  Write-Host "Missing eas.json: $EasJson" -ForegroundColor Red
  exit 1
}

$raw = Get-Content $EasJson -Raw -Encoding UTF8
if ($raw -notmatch '"EXPO_PUBLIC_DEV_BFF_URL"\s*:') {
  Write-Host "eas.json missing EXPO_PUBLIC_DEV_BFF_URL under preview.env" -ForegroundColor Red
  exit 1
}

$prev = $null
if ($raw -match '"EXPO_PUBLIC_DEV_BFF_URL"\s*:\s*"([^"]*)"') {
  $prev = $Matches[1]
}

# Surgical replace — avoid ConvertTo-Json reordering the whole file
$updated = [regex]::Replace(
  $raw,
  '("EXPO_PUBLIC_DEV_BFF_URL"\s*:\s*")[^"]*(")',
  { param($m) $m.Groups[1].Value + $trimmed + $m.Groups[2].Value },
  1
)
$updated = [regex]::Replace(
  $updated,
  '("EXPO_PUBLIC_DEV_BFF_TOKEN"\s*:\s*")[^"]*(")',
  { param($m) $m.Groups[1].Value + $m.Groups[2].Value },
  1
)

if ($updated -eq $raw -and $prev -eq $trimmed) {
  Write-Host "OK  eas.json already points at $trimmed" -ForegroundColor Green
} else {
  $utf8NoBom = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($EasJson, $updated, $utf8NoBom)
  Write-Host "OK  eas.json preview EXPO_PUBLIC_DEV_BFF_URL" -ForegroundColor Green
  Write-Host "    was: $prev"
  Write-Host "    now: $trimmed"
}

Write-Host '    EXPO_PUBLIC_DEV_BFF_TOKEN = "" (OTP-only)' -ForegroundColor DarkGray
Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "  1) curl.exe -sS `"$trimmed/health`"   # allow_mock_preview should be false"
Write-Host "  2) powershell -File `"$repoRoot\scripts\check-internal-beta-ready.ps1`""
Write-Host "  3) cd `"$repoRoot\apps\mobile`" ; eas build --profile preview --platform ios"
