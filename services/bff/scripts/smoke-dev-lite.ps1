# Dev Lite 冒烟（本机，无需手机）
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8790"
$token = "dev-token"
$h = @{ Authorization = "Bearer $token"; Accept = "application/json" }

Write-Host "1. GET /health" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$base/health" -Headers $h
Write-Host "   mode=$($health.mode) x02=$($health.x02.reachable) mock=$($health.allow_mock_preview)"

Write-Host "2. POST /v1/auth/otp/request" -ForegroundColor Cyan
$otp = Invoke-RestMethod -Uri "$base/v1/auth/otp/request" -Method POST -Headers $h `
  -ContentType "application/json" -Body '{"email":"smoke@diary.one"}'
if (-not $otp.ok) { throw "otp request failed" }
Write-Host "   delivery=$($otp.delivery)"

Write-Host "3. POST /v1/auth/otp/verify" -ForegroundColor Cyan
if (-not $otp.dev_code) { throw "need dev_code (enable EXPOSE_OTP or SMTP)" }
$verify = Invoke-RestMethod -Uri "$base/v1/auth/otp/verify" -Method POST -Headers $h `
  -ContentType "application/json" -Body (@{ email = "smoke@diary.one"; code = $otp.dev_code } | ConvertTo-Json)
if (-not $verify.session_token) { throw "verify failed" }
Write-Host "   session_token ok"
$sessionH = @{ Authorization = "Bearer $($verify.session_token)"; Accept = "application/json" }
$h = $sessionH

Write-Host "4. day-revisions idempotency (minimal manifest)" -ForegroundColor Cyan
$rev = "dayrev_smoke_$(Get-Date -Format 'yyyyMMddHHmmss')"
$manifestPath = Join-Path $env:TEMP "diary-one-smoke-manifest.json"
$manifestJson = '{"bundle_version":"DIARY_ONE_APP_LIBRARY_BUNDLE_V04","assets":[]}'
[System.IO.File]::WriteAllText($manifestPath, $manifestJson, [System.Text.UTF8Encoding]::new($false))
$job1 = curl.exe -s -S -X POST "$base/v1/day-revisions" -H "Authorization: Bearer $token" `
  -F "manifest=@$manifestPath;type=application/json" -F "day_revision_id=$rev"
$j1 = $job1 | ConvertFrom-Json
if (-not $j1.job_id) { throw "day-revision failed: $job1" }
Write-Host "   job1=$($j1.job_id)"

$job2 = curl.exe -s -S -X POST "$base/v1/day-revisions" -H "Authorization: Bearer $token" `
  -F "manifest=@$manifestPath;type=application/json" -F "day_revision_id=$rev"
$j2 = $job2 | ConvertFrom-Json
if ($j2.job_id -ne $j1.job_id) { throw "idempotent expected same job_id" }
Write-Host "   idempotent ok (same job_id)"

Write-Host "5. Poll /v1/jobs/$($j1.job_id) (max 90s)" -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds(90)
$final = $null
do {
  $poll = Invoke-RestMethod -Uri "$base/v1/jobs/$($j1.job_id)" -Headers $h
  Write-Host "   status=$($poll.status)"
  if ($poll.status -in @("succeeded", "failed")) { $final = $poll; break }
  Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)

if (-not $final) { throw "job did not reach terminal state in 90s" }
if ($final.status -eq "failed") {
  Write-Host "   WARN: job failed (X02 down or no DASHSCOPE_API_KEY?) — OTP/idempotent path OK" -ForegroundColor Yellow
}

Write-Host "`nSmoke done." -ForegroundColor Green
