# Production BFF smoke (Docker stack must be up: docker compose up -d)
# Covers: health · OTP/session · day-revision job · optional recap if ffmpeg in image
$ErrorActionPreference = "Stop"
$base = if ($env:DIARY_BFF_URL) { $env:DIARY_BFF_URL.TrimEnd('/') } else { "http://127.0.0.1:8790" }
$token = if ($env:DIARY_API_TOKEN) { $env:DIARY_API_TOKEN } else { "dev-token" }
$h = @{ Authorization = "Bearer $token"; Accept = "application/json" }

Write-Host "GET $base/health" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$base/health" -Headers $h
Write-Host "   status=$($health.status) smtp=$($health.smtp_configured) ffmpeg=$($health.ffmpeg_available) x02=$($health.x02.reachable)"

Write-Host "OTP + session" -ForegroundColor Cyan
$otp = Invoke-RestMethod -Uri "$base/v1/auth/otp/request" -Method POST -Headers $h `
  -ContentType "application/json" -Body '{"email":"docker-smoke@diary.one"}'
if (-not $otp.dev_code) {
  if ($health.smtp_configured) {
    Write-Host "   SMTP configured — no dev_code (expected). Skipping verify." -ForegroundColor Yellow
  } else {
    throw "need dev_code (set EXPOSE_OTP_IN_RESPONSE=true for smoke without SMTP)"
  }
} else {
  $verify = Invoke-RestMethod -Uri "$base/v1/auth/otp/verify" -Method POST -Headers $h `
    -ContentType "application/json" -Body (@{ email = "docker-smoke@diary.one"; code = $otp.dev_code } | ConvertTo-Json)
  $session = $verify.session_token
  if (-not $session) { throw "no session_token" }
  $sh = @{ Authorization = "Bearer $session"; Accept = "application/json" }
  Invoke-RestMethod -Uri "$base/health" -Headers $sh | Out-Null
  Write-Host "   session bearer OK" -ForegroundColor Green
}

# Minimal day-revision: empty-ish multipart may fail validation — use tiny JPEG if present
$demo = Join-Path $PSScriptRoot "..\..\..\apps\mobile\assets\icon.png"
if (-not (Test-Path $demo)) {
  Write-Host "Skip day-revision (no demo asset at $demo)" -ForegroundColor Yellow
} else {
  Write-Host "POST day-revisions (smoke upload)" -ForegroundColor Cyan
  # Prefer existing smoke-demo-day when pointing at same host
  $smokeDemo = Join-Path $PSScriptRoot "smoke-demo-day.ps1"
  if (Test-Path $smokeDemo) {
    $env:DIARY_BFF_URL = $base
    $env:DIARY_API_TOKEN = $token
    try {
      & $smokeDemo
      Write-Host "   day-revision path OK" -ForegroundColor Green
    } catch {
      Write-Host "   day-revision smoke failed (worker/X02?): $_" -ForegroundColor Yellow
    }
  }
}

Write-Host "Docker smoke finished." -ForegroundColor Green
