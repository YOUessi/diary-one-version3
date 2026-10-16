# Daily Recap ffmpeg render smoke (Dev Lite or Docker BFF on :8790)
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8790"
$token = "dev-token"
$h = @{ Authorization = "Bearer $token"; Accept = "video/mp4" }

Write-Host "GET /health (ffmpeg)" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$base/health" -Headers @{ Authorization = "Bearer $token"; Accept = "application/json" }
if (-not $health.ffmpeg_available) {
  Write-Host "ffmpeg_available=false — install ffmpeg and restart BFF" -ForegroundColor Yellow
  exit 1
}

$tmp = Join-Path $env:TEMP "diary-recap-smoke.jpg"
# 1x1 red JPEG minimal
$bytes = [Convert]::FromBase64String("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA//2Q==")
[System.IO.File]::WriteAllBytes($tmp, $bytes)

Write-Host "POST /v1/share/daily-recap/render" -ForegroundColor Cyan
$out = Join-Path $env:TEMP "diary-recap-smoke.mp4"
curl.exe -s -S -X POST "$base/v1/share/daily-recap/render" -H "Authorization: Bearer $token" `
  -F "slide_count=2" -F "fps=24" -F "slide_duration_sec=1.5" `
  -F "slide_0=@$tmp;type=image/jpeg" -F "slide_1=@$tmp;type=image/jpeg" -o $out
if (-not (Test-Path $out) -or (Get-Item $out).Length -lt 500) {
  throw "recap mp4 missing or too small"
}
Write-Host "   wrote $out ($((Get-Item $out).Length) bytes)" -ForegroundColor Green
Write-Host "Recap smoke OK."
