<#
Open the cloud bulk test channel (PC):

  host X02 :8787 (qwen + DASHSCOPE_API_KEY / 百炼)
  + Docker BFF/Worker :8790  (or Dev Lite)
  + optional -MediaDir pack run with -RequireGrounded

  .\scripts\open-cloud-bulk-channel.ps1
  .\scripts\open-cloud-bulk-channel.ps1 -MediaDir D:\packs\day1 -RequireGrounded
  .\scripts\open-cloud-bulk-channel.ps1 -Quality   # ALLOW_MOCK_PREVIEW=false + restart worker
#>
param(
  [string]$MediaDir = "",
  [switch]$RequireGrounded,
  [switch]$Quality,
  [int]$MaxAssets = 40,
  [switch]$SkipDockerRestart
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

# Load User DashScope into process
if (-not $env:DASHSCOPE_API_KEY) {
  $userKey = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
  if ($userKey) { $env:DASHSCOPE_API_KEY = $userKey }
}

Write-Host "=== Open cloud bulk channel ===" -ForegroundColor Cyan

if (-not $env:DASHSCOPE_API_KEY) {
  Write-Host "DASHSCOPE_API_KEY missing. For real V1.75:" -ForegroundColor Yellow
  Write-Host "  .\scripts\set-dashscope-key.ps1 -Key 'sk-...'"
  if ($RequireGrounded -or $Quality) {
    throw "RequireGrounded/Quality needs DashScope key"
  }
}

Write-Host "1) Start X02 qwen on :8787" -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "start-x02.ps1") -Adapter qwen
if ($LASTEXITCODE -ne 0) { throw "start-x02 failed" }

if (-not $SkipDockerRestart) {
  Write-Host "2) Ensure Docker stack (BFF+Worker → host.docker.internal:8787)" -ForegroundColor Cyan
  if ($Quality) {
    $env:ALLOW_MOCK_PREVIEW = "false"
    Write-Host "   ALLOW_MOCK_PREVIEW=false (quality)" -ForegroundColor Green
  } else {
    if (-not $env:ALLOW_MOCK_PREVIEW) { $env:ALLOW_MOCK_PREVIEW = "true" }
    Write-Host "   ALLOW_MOCK_PREVIEW=$($env:ALLOW_MOCK_PREVIEW) (UI path may mock empty days)" -ForegroundColor DarkYellow
  }
  docker compose up -d --build bff worker
  if ($LASTEXITCODE -ne 0) { throw "docker compose failed — is Docker Engine running?" }
  Start-Sleep -Seconds 5
}

Write-Host "3) Health" -ForegroundColor Cyan
$h = Invoke-RestMethod -Uri "http://127.0.0.1:8790/health" -TimeoutSec 15
Write-Host ("   BFF ok · x02.reachable={0} modelReady={1} mock={2}" -f $h.x02.reachable, $h.x02.modelReady, $h.allow_mock_preview)
try {
  $x = Invoke-RestMethod -Uri "http://127.0.0.1:8787/health" -TimeoutSec 10
  Write-Host ("   X02 ok · modelReady={0} productionReady={1} provider={2}" -f $x.modelReady, $x.productionReady, $x.provider)
} catch {
  Write-Host "   X02 health direct fail: $($_.Exception.Message)" -ForegroundColor Yellow
}

$report = Join-Path $env:TEMP "diary-cloud-pack-reports"
New-Item -ItemType Directory -Force -Path $report | Out-Null

if ($MediaDir) {
  Write-Host "4) Run pack through cloud" -ForegroundColor Cyan
  $args = @{
    MediaDir = $MediaDir
    MaxAssets = $MaxAssets
    ReportDir = $report
    TimeoutSec = 900
  }
  if ($RequireGrounded -or $Quality) { $args.RequireGrounded = $true }
  & (Join-Path $PSScriptRoot "smoke-cloud-pack.ps1") @args
} else {
  Write-Host "4) Skip pack run (no -MediaDir). Channel is up." -ForegroundColor DarkYellow
  Write-Host "   Next: .\scripts\smoke-cloud-pack.ps1 -MediaDir D:\your\photos -RequireGrounded -ReportDir $report"
}

Write-Host ""
Write-Host "Phone Expo Go still uses Lab A/B → same BFF :8790 on LAN." -ForegroundColor Cyan
Write-Host "Local algorithm (eval-web) stays separate; this is the CLOUD subscription path (百炼)." -ForegroundColor Cyan
