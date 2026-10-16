# Minimal day-revision with 1 JPEG frame — verifies Demo→cloud path (mock or X02)
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8790"
$token = "dev-token"
$h = @{ Authorization = "Bearer $token"; Accept = "application/json" }

Write-Host "GET /health" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$base/health" -Headers $h
Write-Host "   mode=$($health.mode) x02=$($health.x02.reachable) mock=$($health.allow_mock_preview) ffmpeg=$($health.ffmpeg_available)"

$tmp = Join-Path $env:TEMP "diary-demo-smoke"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$jpg = Join-Path $tmp "asset-0-f0.jpg"
# Valid tiny JPEG (same as smoke-recap)
$bytes = [Convert]::FromBase64String("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA//2Q==")
[System.IO.File]::WriteAllBytes($jpg, $bytes)

$sha = (Get-FileHash -Algorithm SHA256 -Path $jpg).Hash.ToLower()
$manifest = @{
  bundle_version = "DIARY_ONE_APP_LIBRARY_BUNDLE_V04"
  research_only = $true
  session = @{
    session_id = [guid]::NewGuid().ToString()
    exported_at = (Get-Date).ToString("o")
    timezone = "Asia/Shanghai"
  }
  device = @{
    device_id = "PHOTO_LIBRARY_TEST"
    hardware_revision = "N/A"
    firmware_version = "N/A"
    sdk_version = "smoke-demo"
  }
  normalization = @{
    width = 768
    height = 1024
    orientation = "PORTRAIT"
    aspect_ratio = "3:4"
    spatial_transform = "ASPECT_FIT_LETTERBOX"
    temporal_transform = "PHONE_TEST_DURATION_WINDOWS_V01"
    canonical_frame_offsets_ms = @(1500, 4500, 7500)
    evidence_profile_version = "PHONE_TEST_DURATION_WINDOWS_V01"
  }
  assets = @(
    @{
      asset_id = "asset-0"
      source_display_name = "demo-photo.jpg"
      media_kind = "PHOTO"
      media_source = "PHONE_LIBRARY_DAY_TEST"
      original_file_extension = "jpg"
      original_sha256 = $sha
      original_bytes = (Get-Item $jpg).Length
      original_width = 1
      original_height = 1
      original_duration_ms = $null
      original_included = $false
      sequence_index = 0
      logical_asset_duration_ms = 9000
      materialized_video = $false
      evidence_sampling_profile = "PHOTO_SINGLE_FRAME"
      evidence_window_count = 1
      frames = @(
        @{
          frame_id = "asset-0-f0"
          window_index = 0
          window_count = 1
          sample_role = "PHOTO_REPRESENTATIVE"
          canonical_offset_ms = 4500
          source_timestamp_ms = $null
          relative_path = "frames/asset-0_0.jpg"
          sha256 = $sha
          width = 768
          height = 1024
          spatial_transform = "ASPECT_FIT_LETTERBOX"
        }
      )
    }
  )
}
$manifestPath = Join-Path $tmp "bundle.json"
[System.IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 8 -Compress), [System.Text.UTF8Encoding]::new($false))

$rev = "dayrev_demo_smoke_$(Get-Date -Format 'yyyyMMddHHmmss')"
Write-Host "POST /v1/day-revisions (1 photo frame)" -ForegroundColor Cyan
$jobRaw = curl.exe -s -S -X POST "$base/v1/day-revisions" -H "Authorization: Bearer $token" `
  -F "manifest=@$manifestPath;type=application/json" `
  -F "day_revision_id=$rev" `
  -F "asset-0-f0=@$jpg;type=image/jpeg"
$job = $jobRaw | ConvertFrom-Json
if (-not $job.job_id) { throw "day-revision failed: $jobRaw" }
Write-Host "   job_id=$($job.job_id)"

$deadline = (Get-Date).AddSeconds(120)
$final = $null
do {
  $poll = Invoke-RestMethod -Uri "$base/v1/jobs/$($job.job_id)" -Headers $h
  Write-Host "   status=$($poll.status) · $($poll.message)"
  if ($poll.status -in @("succeeded", "failed")) { $final = $poll; break }
  Start-Sleep -Seconds 2
} while ((Get-Date) -lt $deadline)

if (-not $final) { throw "job did not finish in 120s" }
if ($final.status -ne "succeeded") {
  throw "Demo smoke FAILED: $($final.message)"
}
$chapters = @($final.result.chapters)
Write-Host "Demo smoke OK — chapters=$($chapters.Count) title=$($chapters[0].title)" -ForegroundColor Green
