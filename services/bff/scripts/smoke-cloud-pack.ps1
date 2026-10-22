<#
Cloud bulk channel: media folder OR existing V04 bundle → BFF → Worker → X02 → report.

  # Real photos day (DashScope / 百炼 on host X02 :8787)
  .\scripts\smoke-cloud-pack.ps1 -MediaDir D:\packs\day1 -RequireGrounded

  # Prebuilt bundle (from eval-web export or prior run)
  .\scripts\smoke-cloud-pack.ps1 -BundleDir D:\packs\day1_bundle -RequireGrounded

  # UI-only path (ALLOW_MOCK_PREVIEW on BFF — not quality)
  .\scripts\smoke-cloud-pack.ps1 -MediaDir D:\packs\day1

Env:
  DIARY_BFF_URL   default http://127.0.0.1:8790
  DIARY_API_TOKEN default dev-token
#>
param(
  [string]$MediaDir = "",
  [string]$BundleDir = "",
  [int]$MaxAssets = 40,
  [switch]$RequireGrounded,
  [int]$TimeoutSec = 900,
  [string]$ReportDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$base = if ($env:DIARY_BFF_URL) { $env:DIARY_BFF_URL.TrimEnd('/') } else { "http://127.0.0.1:8790" }
$token = if ($env:DIARY_API_TOKEN) { $env:DIARY_API_TOKEN } else { "dev-token" }
$h = @{ Authorization = "Bearer $token"; Accept = "application/json" }

function Resolve-Python {
  if ($env:DIARY_ONE_PYTHON -and (Test-Path -LiteralPath $env:DIARY_ONE_PYTHON)) {
    return $env:DIARY_ONE_PYTHON
  }
  if (Test-Path "C:\Python314\python.exe") { return "C:\Python314\python.exe" }
  return (Get-Command python -ErrorAction Stop).Source
}

Write-Host "=== Cloud pack smoke ===" -ForegroundColor Cyan
Write-Host "BFF $base"

$health = Invoke-RestMethod -Uri "$base/health" -Headers $h -TimeoutSec 10
$mock = $health.allow_mock_preview
$x02ok = $health.x02.reachable
Write-Host "   mode=$($health.mode) x02=$x02ok mock=$mock modelReady=$($health.x02.modelReady)"

if ($RequireGrounded) {
  if (-not $x02ok) { throw "X02 not reachable from BFF — start .\scripts\start-quality-stack.ps1 (or start-x02 -Adapter qwen)" }
  if ($mock -eq $true) {
    throw @"
allow_mock_preview=true — Refuse quality gate.

Start quality stack:
  .\scripts\start-quality-stack.ps1
Or Dev Lite:
  .\scripts\start-dev-lite.ps1 -Adapter qwen -AllowMockPreview:`$false
"@
  }
  $model = [string]$health.x02.model
  $provider = [string]$health.x02.provider
  if ($provider -match 'fixture' -or $model -match 'fixture') {
    throw "X02 still on fixture — need qwen + DASHSCOPE_API_KEY (start-quality-stack.ps1)"
  }
}

if (-not $BundleDir) {
  if (-not $MediaDir) { throw "Pass -MediaDir or -BundleDir" }
  if (-not (Test-Path -LiteralPath $MediaDir)) { throw "MediaDir missing: $MediaDir" }
  $BundleDir = Join-Path $env:TEMP ("diary-cloud-pack-" + (Get-Date -Format "yyyyMMddHHmmss"))
  $py = Resolve-Python
  Write-Host "Building V04 bundle from $MediaDir (max $MaxAssets)…" -ForegroundColor Cyan
  & $py -m pip install -q pillow 2>$null | Out-Null
  & $py (Join-Path $ScriptRoot "build_pack_bundle.py") --media $MediaDir --out $BundleDir --max-assets $MaxAssets
  if ($LASTEXITCODE -ne 0) { throw "build_pack_bundle.py failed" }
}

$manifestPath = Join-Path $BundleDir "bundle.json"
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "bundle.json missing in $BundleDir" }
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$assetCount = @($manifest.assets).Count
Write-Host "Bundle assets=$assetCount version=$($manifest.bundle_version)"

$curlArgs = @(
  "-s", "-S", "-X", "POST", "$base/v1/day-revisions",
  "-H", "Authorization: Bearer $token",
  "-F", "manifest=@$manifestPath;type=application/json",
  "-F", "day_revision_id=dayrev_pack_$(Get-Date -Format 'yyyyMMddHHmmss')"
)
foreach ($asset in $manifest.assets) {
  foreach ($frame in $asset.frames) {
    $rel = [string]$frame.relative_path
    $fid = [string]$frame.frame_id
    $fp = Join-Path $BundleDir ($rel -replace '/', [IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $fp)) { throw "Missing frame file: $fp" }
    $curlArgs += @("-F", "${fid}=@$fp;type=image/jpeg")
  }
}

Write-Host "POST /v1/day-revisions ($assetCount assets)…" -ForegroundColor Cyan
$jobRaw = & curl.exe @curlArgs
$job = $jobRaw | ConvertFrom-Json
if (-not $job.job_id) { throw "day-revision failed: $jobRaw" }
Write-Host "   job_id=$($job.job_id)"

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$final = $null
do {
  Start-Sleep -Seconds 3
  $poll = Invoke-RestMethod -Uri "$base/v1/jobs/$($job.job_id)" -Headers $h
  Write-Host "   status=$($poll.status) · $($poll.message)"
  if ($poll.status -in @("succeeded", "failed")) { $final = $poll; break }
} while ((Get-Date) -lt $deadline)

if (-not $final) { throw "Job timed out after ${TimeoutSec}s" }
if ($final.status -ne "succeeded") { throw "Job failed: $($final.message)" }

$result = $final.result
$chapters = @($result.chapters)
$ahas = @($result.ahas)
$delivery = [string]$result.delivery_state
$semantic = [string]$result.semantic_day_state
$fallback = $result.dev_lite_fallback -eq $true

Write-Host ""
Write-Host "=== Result ===" -ForegroundColor Green
Write-Host "delivery=$delivery semantic=$semantic chapters=$($chapters.Count) ahas=$($ahas.Count) mock_fallback=$fallback"
foreach ($ch in $chapters | Select-Object -First 8) {
  Write-Host ("  · " + $ch.title)
}

if ($ReportDir) {
  New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
  $stamp = Get-Date -Format "yyyyMMddHHmmss"
  $reportPath = Join-Path $ReportDir "cloud_pack_$stamp.json"
  @{
    job_id = $job.job_id
    asset_count = $assetCount
    delivery_state = $delivery
    semantic_day_state = $semantic
    chapter_count = $chapters.Count
    aha_count = $ahas.Count
    mock_fallback = $fallback
    chapter_titles = @($chapters | ForEach-Object { $_.title })
    message = $final.message
  } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding UTF8
  $resultPath = Join-Path $ReportDir "cloud_pack_${stamp}_result.json"
  ($result | ConvertTo-Json -Depth 20) | Set-Content -LiteralPath $resultPath -Encoding UTF8
  Write-Host "Report: $reportPath"
}

if ($RequireGrounded) {
  if ($fallback) { throw "Got mock fallback — not grounded cloud quality" }
  if ($chapters.Count -eq 0 -and $ahas.Count -eq 0) {
    throw "NO_GROUNDED_MEMORY / empty memories — try richer real photos (not solid demo JPEG)"
  }
  if ($delivery -eq "NO_GROUNDED_MEMORY" -or $semantic -eq "EMPTY_DAY") {
    throw "Empty day delivery=$delivery semantic=$semantic"
  }
  # Copy / selection sanity (quality gate)
  $emptyTitle = @($chapters | Where-Object { -not [string]$_.title -or ([string]$_.title).Trim().Length -lt 2 })
  if ($emptyTitle.Count -gt 0) { throw "Grounded gate: $($emptyTitle.Count) chapter(s) missing title" }
  $thin = @($chapters | Where-Object {
      $body = [string]($_.body -as [string])
      if (-not $body) { $body = [string]($_.story -as [string]) }
      if (-not $body) { $body = [string]($_.ai_story -as [string]) }
      if (-not $body) { $body = [string]($_.summary -as [string]) }
      $body.Trim().Length -lt 12
    })
  if ($thin.Count -eq $chapters.Count -and $chapters.Count -gt 0) {
    Write-Host "WARNING: all chapter bodies look thin — check writer surface fields in result JSON" -ForegroundColor Yellow
  }
  Write-Host "RequireGrounded checks passed" -ForegroundColor Green
}

Write-Host "Cloud pack channel OK" -ForegroundColor Green
