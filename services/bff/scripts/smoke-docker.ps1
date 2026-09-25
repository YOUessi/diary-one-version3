# Production BFF smoke (Docker stack must be up: docker compose up -d)
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8790"
$token = "dev-token"
$h = @{ Authorization = "Bearer $token"; Accept = "application/json" }

Write-Host "GET /health (production BFF)" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$base/health" -Headers $h
Write-Host "   status=$($health.status)"

Write-Host "OTP + session (shared module)" -ForegroundColor Cyan
$otp = Invoke-RestMethod -Uri "$base/v1/auth/otp/request" -Method POST -Headers $h `
  -ContentType "application/json" -Body '{"email":"docker-smoke@diary.one"}'
if (-not $otp.dev_code) { throw "need dev_code (EXPOSE_OTP_IN_RESPONSE=true)" }
$verify = Invoke-RestMethod -Uri "$base/v1/auth/otp/verify" -Method POST -Headers $h `
  -ContentType "application/json" -Body (@{ email = "docker-smoke@diary.one"; code = $otp.dev_code } | ConvertTo-Json)
$session = $verify.session_token
if (-not $session) { throw "no session_token" }

$sh = @{ Authorization = "Bearer $session"; Accept = "application/json" }
Invoke-RestMethod -Uri "$base/health" -Headers $sh | Out-Null
Write-Host "   session bearer accepted on /health" -ForegroundColor Green
Write-Host "Docker smoke OK (day-revisions needs MinIO+worker — run smoke-dev-lite for full job path)."
