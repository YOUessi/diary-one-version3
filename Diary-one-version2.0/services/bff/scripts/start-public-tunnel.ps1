<#
.SYNOPSIS
  Expose local Dev Lite (:8790) via Cloudflare quick tunnel (HTTPS).
  Prints the trycloudflare.com URL and can write it into eas.json preview.

.NOTES
  - Requires Dev Lite (or Docker BFF) listening on 127.0.0.1:8790
  - Requires cloudflared on PATH (winget install Cloudflare.cloudflared)
  - Quick tunnel URL changes every run; keep this PC awake while testers use it
  - For a stable hostname use a Named Tunnel (see docs/INTERNAL_BETA_OPS_CHECKLIST.md)

.EXAMPLE
  cd E:\AI耳机\diary-one\services\bff
  .\scripts\start-dev-lite-background.ps1   # if not already up
  .\scripts\start-public-tunnel.ps1 -ApplyEas
#>
param(
  [string]$LocalBase = "http://127.0.0.1:8790",
  [switch]$ApplyEas,
  [switch]$SkipHealthCheck,
  [int]$UrlWaitSeconds = 90
)

$ErrorActionPreference = "Stop"
$scripts = $PSScriptRoot

function Test-LocalHealth([string]$base) {
  $u = $base.TrimEnd("/") + "/health"
  try {
    return Invoke-RestMethod -Uri $u -TimeoutSec 5
  } catch {
    return $null
  }
}

Write-Host "=== Diary One · public HTTPS tunnel (Cloudflare quick) ===" -ForegroundColor Cyan

if (-not $SkipHealthCheck) {
  $health = Test-LocalHealth $LocalBase
  if (-not $health) {
    Write-Host "FIX: $LocalBase/health not reachable." -ForegroundColor Red
    Write-Host "  Start Dev Lite first:" -ForegroundColor Yellow
    Write-Host "    .\scripts\start-dev-lite-background.ps1"
    Write-Host "  Or Docker quality stack:" -ForegroundColor Yellow
    Write-Host "    .\scripts\prepare-multiuser-beta.ps1 -HardenEnv"
    Write-Host "    .\scripts\prepare-multiuser-beta.ps1 -Up"
    exit 1
  }
  $mock = $health.allow_mock_preview
  Write-Host ("OK  local health  mock={0}" -f $mock) -ForegroundColor Green
  if ($mock -eq $true -or "$mock" -eq "True") {
    Write-Host "WARN: allow_mock_preview=true — internal beta App will reject mock. Harden .env:" -ForegroundColor Yellow
    Write-Host "  .\scripts\prepare-multiuser-beta.ps1 -HardenEnv" -ForegroundColor Yellow
    Write-Host "  then restart BFF" -ForegroundColor Yellow
  }
}

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
  Write-Host "FIX: cloudflared not on PATH." -ForegroundColor Red
  Write-Host "  Install: winget install Cloudflare.cloudflared" -ForegroundColor Yellow
  Write-Host "  Or: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" -ForegroundColor Yellow
  Write-Host "  Then open a new terminal and re-run this script." -ForegroundColor Yellow
  exit 1
}

$target = $LocalBase.TrimEnd("/")
$stamp = [guid]::NewGuid().ToString("n")
$outLog = Join-Path $env:TEMP ("diary-one-cloudflared-{0}.out.log" -f $stamp)
$errLog = Join-Path $env:TEMP ("diary-one-cloudflared-{0}.err.log" -f $stamp)
Write-Host "Starting: cloudflared tunnel --url $target" -ForegroundColor DarkGray
Write-Host "Log: $errLog" -ForegroundColor DarkGray
Write-Host "cloudflared stays running after this script finds the URL. Stop-Process to tear down." -ForegroundColor Yellow
Write-Host ""

# Separate out/err files — Windows forbids redirecting both to the same path.
$argList = @("tunnel", "--url", $target)
$proc = Start-Process -FilePath $cloudflared.Source -ArgumentList $argList `
  -RedirectStandardOutput $outLog -RedirectStandardError $errLog `
  -PassThru -WindowStyle Hidden

function Get-TunnelUrlFromLogs {
  foreach ($p in @($errLog, $outLog)) {
    if (-not (Test-Path $p)) { continue }
    $text = Get-Content $p -Raw -ErrorAction SilentlyContinue
    if ($text -and $text -match 'https://[a-zA-Z0-9-]+\.trycloudflare\.com') {
      return $Matches[0].TrimEnd("/")
    }
  }
  return $null
}

$publicUrl = $null
$deadline = [DateTime]::UtcNow.AddSeconds($UrlWaitSeconds)
while ([DateTime]::UtcNow -lt $deadline -and -not $publicUrl) {
  Start-Sleep -Milliseconds 500
  $publicUrl = Get-TunnelUrlFromLogs
  if ($proc.HasExited -and -not $publicUrl) { break }
}

if (-not $publicUrl) {
  Write-Host "FIX: did not see trycloudflare.com URL within ${UrlWaitSeconds}s." -ForegroundColor Red
  Write-Host "--- stderr ---" -ForegroundColor Yellow
  if (Test-Path $errLog) { Get-Content $errLog -Tail 40 }
  Write-Host "--- stdout ---" -ForegroundColor Yellow
  if (Test-Path $outLog) { Get-Content $outLog -Tail 20 }
  if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
  exit 1
}

Write-Host ""
Write-Host "PUBLIC_BFF_URL=$publicUrl" -ForegroundColor Green
Write-Host "cloudflared PID=$($proc.Id)  (Stop-Process -Id $($proc.Id) to tear down)" -ForegroundColor DarkGray
Write-Host "Health: curl.exe -4 -sS `"$publicUrl/health`"" -ForegroundColor Cyan

# Prefer IPv4: some Windows DNS stacks fail trycloudflare AAAA first
try {
  $verify = & curl.exe -4 -sS -m 40 "$publicUrl/health" 2>$null
  if ($verify -match '"allow_mock_preview"\s*:\s*false') {
    Write-Host "OK  public /health allow_mock_preview=false" -ForegroundColor Green
  } elseif ($verify -match '"status"\s*:\s*"ok"') {
    Write-Host "WARN public /health ok but mock flag not false - run -HardenEnv and restart BFF" -ForegroundColor Yellow
  } else {
    Write-Host "WARN public /health unexpected; try: curl.exe -4 -sS `"$publicUrl/health`"" -ForegroundColor Yellow
  }
} catch {
  Write-Host "WARN could not verify public health from this shell" -ForegroundColor Yellow
}

# Persist last URL for other scripts / docs
$stateDir = Join-Path (Split-Path -Parent $scripts) ".local"
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
$stateFile = Join-Path $stateDir "last-public-bff-url.txt"
Set-Content -Path $stateFile -Value $publicUrl -Encoding UTF8
Write-Host "Saved: $stateFile" -ForegroundColor DarkGray

if ($ApplyEas) {
  & (Join-Path $scripts "apply-public-bff-url.ps1") -Url $publicUrl
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host ""
  Write-Host "Write into eas.json preview:" -ForegroundColor Yellow
  Write-Host "  .\scripts\apply-public-bff-url.ps1 -Url $publicUrl"
}

Write-Host ""
Write-Host "Next checklist:" -ForegroundColor Cyan
Write-Host "  1) .\scripts\prepare-multiuser-beta.ps1 -HardenEnv   # if API_TOKEN still dev-token"
Write-Host "  2) SMTP: .\scripts\set-smtp.ps1 ... then restart BFF"
Write-Host "  3) powershell -File ..\..\scripts\check-internal-beta-ready.ps1"
Write-Host "  4) cd ..\..\apps\mobile ; eas build --profile preview --platform ios"
Write-Host ""
Write-Host "Tunnel is running in background. This script exits; keep PID $($proc.Id) alive." -ForegroundColor Green
