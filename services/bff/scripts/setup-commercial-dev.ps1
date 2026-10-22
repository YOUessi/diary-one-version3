<#
.SYNOPSIS
  商用联调本机配置（默认不需要管理员）：写入 App .env、校正 server .env、自检。
  防火墙需单独用 -OpenFirewall（管理员）跑一次。
#>
param(
  [switch]$OpenFirewall,
  [switch]$StartStack,
  [ValidateSet("fixture", "qwen")]
  [string]$Adapter = "fixture"
)

$ErrorActionPreference = "Stop"
$ServerRoot = Split-Path -Parent $PSScriptRoot
# Monorepo App: diary-one/apps/mobile ; legacy sibling: diary-one-app
$appCandidates = @(
  (Join-Path $ServerRoot "..\..\apps\mobile"),
  (Join-Path $ServerRoot "..\diary-one-app"),
  "E:\AI耳机\diary-one\apps\mobile",
  "E:\AI耳机\diary-one-app"
)
$AppRoot = $null
foreach ($c in $appCandidates) {
  try {
    $resolved = Resolve-Path $c -ErrorAction Stop
    if (Test-Path (Join-Path $resolved "package.json")) {
      $AppRoot = $resolved.Path
      break
    }
  } catch { continue }
}
if (-not $AppRoot) { throw "App root not found (expected diary-one/apps/mobile)." }

. (Join-Path $PSScriptRoot "_lan-ip.ps1")
$lan = $DiaryLanIPv4

Write-Host "=== Diary One commercial-dev setup ===" -ForegroundColor Cyan
Write-Host "LAN IP: $lan"

if ($OpenFirewall) {
  $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
  )
  if (-not $isAdmin) {
    throw "OpenFirewall requires Administrator PowerShell."
  }
  $ruleName = "DiaryOne-DevLite-8790"
  if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 8790 -Action Allow | Out-Null
    Write-Host "Firewall: allowed inbound TCP 8790" -ForegroundColor Green
  } else {
    Write-Host "Firewall: rule already exists"
  }
}

$envPath = Join-Path $AppRoot ".env"
$keepLines = @()
if (Test-Path $envPath) {
  foreach ($line in Get-Content $envPath) {
    if ($line -match '^\s*#' -or $line -notmatch '=') { continue }
    $key = ($line -split '=', 2)[0].Trim()
    if ($key -in @('EXPO_PUBLIC_DEV_BFF_URL', 'EXPO_PUBLIC_DEV_BFF_TOKEN')) { continue }
    if ($key -like 'EXPO_PUBLIC_*') { $keepLines += $line }
  }
}
$envBody = @"
# Auto-written by setup-commercial-dev.ps1 — restart Metro after change
# Formal consumer App: OTP session only (empty token). Lab: EXPO_PUBLIC_ENABLE_LAB=1
EXPO_PUBLIC_DEV_BFF_URL=http://${lan}:8790
EXPO_PUBLIC_DEV_BFF_TOKEN=
"@
if ($keepLines.Count -gt 0) {
  $envBody = $envBody.TrimEnd() + "`r`n" + ($keepLines -join "`r`n") + "`r`n"
}
$envBody | Set-Content -Path $envPath -Encoding UTF8
Write-Host "Wrote $envPath (BFF http://${lan}:8790, token empty for OTP)"

$serverEnv = Join-Path $ServerRoot ".env"
if (-not (Test-Path $serverEnv)) {
  Copy-Item (Join-Path $ServerRoot ".env.example") $serverEnv
}
$lines = @(Get-Content $serverEnv)
$hasX02 = $false
$hasToken = $false
$out = foreach ($line in $lines) {
  if ($line -match '^X02_BASE_URL=') { $hasX02 = $true; "X02_BASE_URL=http://127.0.0.1:8787" }
  elseif ($line -match '^API_TOKEN=') { $hasToken = $true; $line }
  else { $line }
}
if (-not $hasX02) { $out += "X02_BASE_URL=http://127.0.0.1:8787" }
if (-not $hasToken) { $out += "API_TOKEN=dev-token" }
$out | Set-Content $serverEnv -Encoding UTF8
Write-Host "Updated server .env"

if ($StartStack) {
  & (Join-Path $PSScriptRoot "start-dev-lite.ps1") -Adapter $Adapter
  Start-Sleep -Seconds 4
}

try {
  $h = Invoke-RestMethod "http://127.0.0.1:8790/health" -TimeoutSec 5
  Write-Host "BFF health: mode=$($h.mode) x02.reachable=$($h.x02.reachable)" -ForegroundColor Green
} catch {
  Write-Host "BFF not up. Run: .\scripts\start-dev-lite.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Phone Expo Go:" -ForegroundColor Cyan
Write-Host "  Metro:  cd $AppRoot ; npx expo start --go --lan --clear"
Write-Host "  URL:    exp://${lan}:8081"
Write-Host "  BFF:    http://${lan}:8790   (OTP login; no shared app token)"
Write-Host "Admin once:  .\scripts\setup-commercial-dev.ps1 -OpenFirewall"
Write-Host "Quality:     .\scripts\start-quality-loop.ps1"
Write-Host "Formal App:  diary-one\docs\FORMAL_APP_ACCEPTANCE.md"
