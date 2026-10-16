# Checklist + optional .env harden + Docker quality compose up for multi-user beta.
#
#   cd E:\AI耳机\diary-one\services\bff
#   .\scripts\prepare-multiuser-beta.ps1 -HardenEnv
#   .\scripts\prepare-multiuser-beta.ps1 -Up
#   .\scripts\start-public-tunnel.ps1 -ApplyEas
param(
  [switch]$Up,
  [switch]$HardenEnv,
  [string]$EnvFile = ".env"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=== Diary One · multi-user beta prep ===" -ForegroundColor Cyan

$envPath = Join-Path $root $EnvFile
if (-not (Test-Path $envPath)) {
  $example = Join-Path $root ".env.example"
  if (Test-Path $example) {
    Copy-Item $example $envPath
    Write-Host "Created $EnvFile from .env.example - fill DASHSCOPE / SMTP next." -ForegroundColor Yellow
  } else {
    Write-Host "Missing $EnvFile - copy .env.example and fill keys." -ForegroundColor Red
    exit 1
  }
}

function Get-DotEnvValue([string]$key) {
  foreach ($line in Get-Content $envPath) {
    if ($line -match "^\s*#") { continue }
    if ($line -match "^\s*$key\s*=\s*(.*)$") {
      return $Matches[1].Trim().Trim('"').Trim("'")
    }
  }
  return ""
}

function Set-DotEnvValue([string]$key, [string]$value) {
  $lines = Get-Content $envPath
  $found = $false
  $out = foreach ($line in $lines) {
    if ($line -match "^\s*$key\s*=") {
      $found = $true
      "$key=$value"
    } else {
      $line
    }
  }
  if (-not $found) {
    $out = @($out) + "$key=$value"
  }
  Set-Content -Path $envPath -Value $out -Encoding UTF8
}

if ($HardenEnv) {
  Write-Host ""
  Write-Host "Hardening $EnvFile for public / multi-user beta..." -ForegroundColor Cyan
  $api = Get-DotEnvValue "API_TOKEN"
  if (-not $api -or $api -eq "dev-token") {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] 32
    $rng.GetBytes($bytes)
    $rng.Dispose()
    $newToken = -join ($bytes | ForEach-Object { $_.ToString("x2") })
    Set-DotEnvValue "API_TOKEN" $newToken
    Write-Host "  OK  API_TOKEN -> random 64-hex (was missing or dev-token)" -ForegroundColor Green
    Write-Host "      Lab-only secret - do NOT put into eas.json; testers use Email OTP." -ForegroundColor DarkGray
  } else {
    $prefix = $api.Substring(0, [Math]::Min(6, $api.Length))
    Write-Host "  OK  API_TOKEN already customized ($prefix...)" -ForegroundColor Green
  }

  Set-DotEnvValue "ALLOW_MOCK_PREVIEW" "false"
  Write-Host "  OK  ALLOW_MOCK_PREVIEW=false" -ForegroundColor Green

  $smtp = Get-DotEnvValue "SMTP_HOST"
  if (-not $smtp) {
    $userHost = [Environment]::GetEnvironmentVariable("SMTP_HOST", "User")
    if ($userHost) {
      Set-DotEnvValue "SMTP_HOST" $userHost
      foreach ($k in @("SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_SECURITY")) {
        $v = [Environment]::GetEnvironmentVariable($k, "User")
        if ($v) { Set-DotEnvValue $k $v }
      }
      Set-DotEnvValue "EXPOSE_OTP_IN_RESPONSE" "false"
      Write-Host "  OK  SMTP_* copied from User env; EXPOSE_OTP_IN_RESPONSE=false" -ForegroundColor Green
    } else {
      Write-Host "  WARN SMTP_HOST empty - run set-smtp.ps1 then -HardenEnv again (or edit .env)" -ForegroundColor Yellow
      Write-Host "       .\scripts\set-smtp.ps1 -SmtpHost ... -User ... -Password ... -From ..." -ForegroundColor Yellow
    }
  } else {
    Set-DotEnvValue "EXPOSE_OTP_IN_RESPONSE" "false"
    Write-Host "  OK  SMTP_HOST set; EXPOSE_OTP_IN_RESPONSE=false" -ForegroundColor Green
  }

  if (-not (Get-DotEnvValue "DAY_REVISION_DAILY_LIMIT")) {
    Set-DotEnvValue "DAY_REVISION_DAILY_LIMIT" "8"
    Write-Host "  OK  DAY_REVISION_DAILY_LIMIT=8" -ForegroundColor Green
  }
  if (-not (Get-DotEnvValue "DAY_REVISION_MAX_INFLIGHT")) {
    Set-DotEnvValue "DAY_REVISION_MAX_INFLIGHT" "2"
    Write-Host "  OK  DAY_REVISION_MAX_INFLIGHT=2" -ForegroundColor Green
  }

  Write-Host "  Restart BFF/Dev Lite so new .env takes effect." -ForegroundColor Yellow
  Write-Host ""
}

$api = Get-DotEnvValue "API_TOKEN"
$mock = Get-DotEnvValue "ALLOW_MOCK_PREVIEW"
$smtp = Get-DotEnvValue "SMTP_HOST"
$quota = Get-DotEnvValue "DAY_REVISION_DAILY_LIMIT"
$worker = Get-DotEnvValue "WORKER_MAX_CONCURRENT"
$expose = Get-DotEnvValue "EXPOSE_OTP_IN_RESPONSE"

Write-Host ""
Write-Host "Checklist (fix .env before public HTTPS):" -ForegroundColor Yellow
if ($api -and $api -ne "dev-token") {
  $prefix = $api.Substring(0, [Math]::Min(6, $api.Length))
  Write-Host "  [ ] API_TOKEN not 'dev-token'     -> OK ($prefix...)" 
} else {
  Write-Host "  [ ] API_TOKEN not 'dev-token'     -> FIX: .\scripts\prepare-multiuser-beta.ps1 -HardenEnv"
}
if ($mock -eq "false") {
  Write-Host "  [ ] ALLOW_MOCK_PREVIEW=false     -> OK"
} else {
  Write-Host "  [ ] ALLOW_MOCK_PREVIEW=false     -> FIX: -HardenEnv (or set false)"
}
if ($smtp) {
  Write-Host "  [ ] SMTP_HOST set               -> OK"
} else {
  Write-Host "  [ ] SMTP_HOST set               -> FIX: .\scripts\set-smtp.ps1 ... then -HardenEnv"
}
if ($expose -eq "false") {
  Write-Host "  [ ] EXPOSE_OTP_IN_RESPONSE=false -> OK"
} else {
  Write-Host "  [ ] EXPOSE_OTP_IN_RESPONSE=false -> WARN: set false after SMTP works"
}
if ($quota) {
  Write-Host "  [ ] DAY_REVISION_DAILY_LIMIT    -> $quota"
} else {
  Write-Host "  [ ] DAY_REVISION_DAILY_LIMIT    -> default 8"
}
if ($worker) {
  Write-Host "  [ ] WORKER_MAX_CONCURRENT       -> $worker"
} else {
  Write-Host "  [ ] WORKER_MAX_CONCURRENT       -> default 1 via compose"
}
Write-Host "  [ ] X02 :8787 on host with DASHSCOPE_API_KEY (App rejects mock)"
Write-Host "  [ ] HTTPS -> :8790 via .\scripts\start-public-tunnel.ps1 -ApplyEas"
Write-Host "  [ ] App eas.json preview EXPO_PUBLIC_DEV_BFF_URL=https://... (token empty)"
Write-Host ""

if (-not $Up) {
  Write-Host "Dry run only (no docker up)." -ForegroundColor DarkYellow
  Write-Host "  Harden:  .\scripts\prepare-multiuser-beta.ps1 -HardenEnv"
  Write-Host "  Tunnel:  .\scripts\start-public-tunnel.ps1 -ApplyEas"
  Write-Host "  Docker:  .\scripts\prepare-multiuser-beta.ps1 -Up"
  exit 0
}

Write-Host "Starting quality stack..." -ForegroundColor Green
docker compose -f docker-compose.yml -f docker-compose.quality.yml --env-file $EnvFile up -d --build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "  1) curl.exe -sS http://127.0.0.1:8790/health  (allow_mock_preview=false)"
Write-Host "  2) .\scripts\start-public-tunnel.ps1 -ApplyEas"
Write-Host "  3) .\scripts\smoke-cloud-pack.ps1 -RequireGrounded"
Write-Host "  4) powershell -File ..\..\scripts\check-internal-beta-ready.ps1"
Write-Host "  5) Testers: Continue with Email (OTP), not shared API_TOKEN"
