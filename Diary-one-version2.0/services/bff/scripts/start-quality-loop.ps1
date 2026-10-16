# One-shot: harden .env + start Dev Lite with real qwen (no mock) for local quality loop.
#
#   cd E:\AI耳机\diary-one\services\bff
#   .\scripts\start-quality-loop.ps1
#
# Requires: DASHSCOPE_API_KEY (User env or set-dashscope-key.ps1)
# Optional: SMTP already via set-smtp.ps1
param(
  [switch]$SkipHarden
)

$ErrorActionPreference = "Stop"
$scripts = $PSScriptRoot

Write-Host "=== Diary One · local quality loop ===" -ForegroundColor Cyan

$key = $env:DASHSCOPE_API_KEY
if (-not $key) { $key = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User") }
if (-not $key) {
  Write-Host "FIX: missing DASHSCOPE_API_KEY" -ForegroundColor Red
  Write-Host "  .\scripts\set-dashscope-key.ps1 -Key 'sk-...'" -ForegroundColor Yellow
  exit 1
}
Write-Host ("OK  DashScope key ({0}...)" -f $key.Substring(0, [Math]::Min(6, $key.Length))) -ForegroundColor Green

if (-not $SkipHarden) {
  & (Join-Path $scripts "prepare-multiuser-beta.ps1") -HardenEnv
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$stop = Join-Path $scripts "stop-dev-lite.ps1"
if (Test-Path $stop) {
  & $stop
  Start-Sleep -Seconds 1
}

& (Join-Path $scripts "start-dev-lite-background.ps1") -Adapter qwen
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Start-Sleep -Seconds 2
$h = Invoke-RestMethod "http://127.0.0.1:8790/health" -TimeoutSec 10
$provider = $null
try { $provider = [string]$h.x02.detail.provider } catch { }

Write-Host ""
Write-Host "Quality gate:" -ForegroundColor Cyan
$fail = 0
if ($h.allow_mock_preview -eq $true) {
  Write-Host "  FIX mock=true" -ForegroundColor Red; $fail++
} else {
  Write-Host "  OK  mock=false" -ForegroundColor Green
}
if (-not $h.x02.reachable) {
  Write-Host "  FIX x02 unreachable" -ForegroundColor Red; $fail++
} else {
  Write-Host "  OK  x02 up" -ForegroundColor Green
}
if ($provider -eq "fixture") {
  Write-Host "  FIX provider=fixture (want dashscope/qwen)" -ForegroundColor Red; $fail++
} else {
  Write-Host "  OK  provider=$provider" -ForegroundColor Green
}
if ($h.smtp_configured) {
  Write-Host "  OK  SMTP configured (expose_otp=$($h.expose_otp_in_response))" -ForegroundColor Green
} else {
  Write-Host "  WARN SMTP not configured - OTP may show dev_code only" -ForegroundColor Yellow
}

Write-Host ""
if ($fail -gt 0) {
  Write-Host "Result: $fail gate(s) failed - not a quality loop yet." -ForegroundColor Red
  exit 1
}

. (Join-Path $scripts "_lan-ip.ps1")
Write-Host "Result: quality loop ready." -ForegroundColor Green
Write-Host "  Phone same Wi-Fi -> Expo Go -> Lab Apply -> Ping (mock=no) -> Import / Demo"
Write-Host "  Guide: docs/LOCAL_QUALITY_LOOP.md"
Write-Host "  LAN BFF: http://${DiaryLanIPv4}:8790"
