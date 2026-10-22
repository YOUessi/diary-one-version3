# Start X02 + Dev Lite BFF as hidden processes (no Conda pop-ups).
# Default: real qwen when DASHSCOPE_API_KEY is set; fixture only with -Adapter fixture.
#
#   .\scripts\start-dev-lite-background.ps1              # quality path (qwen if key present)
#   .\scripts\start-dev-lite-background.ps1 -Adapter fixture -AllowMockPreview  # UI only
param(
  [ValidateSet("qwen", "fixture")]
  [string]$Adapter = "qwen",
  [switch]$AllowMockPreview
)

$ErrorActionPreference = "Stop"
$ServerRoot = Split-Path -Parent $PSScriptRoot

# Gyan winget ffmpeg is often not on PATH for hidden processes
$ff = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter "ffmpeg.exe" -Recurse -ErrorAction SilentlyContinue |
  Select-Object -First 1
if ($ff) {
  $env:Path = "$($ff.DirectoryName);$env:Path"
}

if ($env:DIARY_ONE_PYTHON -and (Test-Path -LiteralPath $env:DIARY_ONE_PYTHON)) { $Py = $env:DIARY_ONE_PYTHON }
elseif (Test-Path "C:\Python314\python.exe") { $Py = "C:\Python314\python.exe" }
else { $Py = (Get-Command python -ErrorAction Stop).Source }

$AlgoRoot = (Resolve-Path (Join-Path $ServerRoot "..\algorithm\algorithm")).Path

# Load User env + .env into this process
foreach ($name in @(
  "DASHSCOPE_API_KEY", "API_TOKEN", "ALLOW_MOCK_PREVIEW", "EXPOSE_OTP_IN_RESPONSE",
  "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_SECURITY",
  "DAY_REVISION_DAILY_LIMIT", "DAY_REVISION_MAX_INFLIGHT"
)) {
  if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
    $v = [Environment]::GetEnvironmentVariable($name, "User")
    if ($v) { Set-Item -Path "Env:$name" -Value $v }
  }
}
$envFile = Join-Path $ServerRoot ".env"
if (Test-Path $envFile) {
  foreach ($line in Get-Content $envFile) {
    if ($line -match "^\s*#" -or $line -notmatch "=") { continue }
    $k, $val = $line.Split("=", 2)
    $k = $k.Trim()
    $val = $val.Trim().Trim('"').Trim("'")
    if ($k -and $val -ne "") {
      Set-Item -Path "Env:$k" -Value $val
    }
  }
}

if (-not $env:DASHSCOPE_API_KEY) {
  $userKey = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
  if ($userKey) { $env:DASHSCOPE_API_KEY = $userKey }
}

if ($Adapter -eq "qwen" -and -not $env:DASHSCOPE_API_KEY) {
  Write-Host "FIX: no DASHSCOPE_API_KEY - consumer App requires real qwen." -ForegroundColor Red
  Write-Host "  .\scripts\set-dashscope-key.ps1 -Key 'sk-...'" -ForegroundColor Yellow
  Write-Host "  Lab/UI only: .\scripts\start-dev-lite-background.ps1 -Adapter fixture -AllowMockPreview" -ForegroundColor DarkYellow
  exit 1
}

# Stop old listeners
Get-NetTCPConnection -LocalPort 8787, 8790 -ErrorAction SilentlyContinue | ForEach-Object {
  Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1

$__ea = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $Py -m pip install -q legacy-cgi fastapi uvicorn httpx pydantic-settings python-multipart *> $null
$ErrorActionPreference = $__ea

# MobileCLIP reference package
$EvidenceRouterRoot = $null
foreach ($er in @(
  (Join-Path $ServerRoot "..\..\diary_one_app_evidence_v0_2_dev8_mobileclip_router"),
  "E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router"
)) {
  try {
    $erResolved = Resolve-Path $er -ErrorAction Stop
    if (Test-Path (Join-Path $erResolved "src\diary_one_app\engine\semantic.py")) {
      $EvidenceRouterRoot = $erResolved.Path
      break
    }
  } catch { continue }
}
if (-not $env:DIARY_ONE_EVIDENCE_ROUTER_ROOT -and $EvidenceRouterRoot) {
  $env:DIARY_ONE_EVIDENCE_ROUTER_ROOT = $EvidenceRouterRoot
}
if (-not $env:DIARY_ONE_MOBILECLIP_CHECKPOINT) {
  $userCkpt = [Environment]::GetEnvironmentVariable("DIARY_ONE_MOBILECLIP_CHECKPOINT", "User")
  if ($userCkpt) { $env:DIARY_ONE_MOBILECLIP_CHECKPOINT = $userCkpt }
}
if (-not $env:DIARY_ONE_MOBILECLIP_CHECKPOINT -and $EvidenceRouterRoot) {
  foreach ($rel in @("checkpoints\mobileclip_s0.pt", "local_experiments\mobileclip_s0.pt", "mobileclip_s0.pt")) {
    $cand = Join-Path $EvidenceRouterRoot $rel
    if (Test-Path -LiteralPath $cand) {
      $env:DIARY_ONE_MOBILECLIP_CHECKPOINT = $cand
      break
    }
  }
}
$EvidenceSrc = if ($env:DIARY_ONE_EVIDENCE_ROUTER_ROOT) { Join-Path $env:DIARY_ONE_EVIDENCE_ROUTER_ROOT "src" } else { "" }

if (-not $env:API_TOKEN -or $env:API_TOKEN -eq "") { $env:API_TOKEN = "dev-token" }
$env:X02_BASE_URL = "http://127.0.0.1:8787"

if ($AllowMockPreview) {
  $env:ALLOW_MOCK_PREVIEW = "true"
} elseif ($env:ALLOW_MOCK_PREVIEW -ne "true") {
  $env:ALLOW_MOCK_PREVIEW = "false"
}

if ($env:SMTP_HOST) {
  if (-not $env:EXPOSE_OTP_IN_RESPONSE -or $env:EXPOSE_OTP_IN_RESPONSE -eq "") {
    $env:EXPOSE_OTP_IN_RESPONSE = "false"
  }
} elseif (-not $env:EXPOSE_OTP_IN_RESPONSE) {
  $env:EXPOSE_OTP_IN_RESPONSE = "true"
}

if (-not $env:DIARY_ONE_MOBILECLIP_DEVICE) { $env:DIARY_ONE_MOBILECLIP_DEVICE = "auto" }
if (-not $env:DIARY_ONE_MOBILECLIP_PROMPTS) { $env:DIARY_ONE_MOBILECLIP_PROMPTS = "1" }

$env:PYTHONPATH = "$AlgoRoot\src"
$x02Args = @("-m", "diary_one_ci.x01_server", "--adapter", $Adapter, "--host", "127.0.0.1", "--port", "8787")
Start-Process -WindowStyle Hidden -FilePath $Py -ArgumentList $x02Args -WorkingDirectory $AlgoRoot

Start-Sleep -Seconds 2
$env:PYTHONPATH = if ($EvidenceSrc -and (Test-Path $EvidenceSrc)) { "$ServerRoot;$EvidenceSrc" } else { $ServerRoot }
Start-Process -WindowStyle Hidden -FilePath $Py -ArgumentList "-m", "uvicorn", "dev_lite.app:app", "--host", "0.0.0.0", "--port", "8790" -WorkingDirectory $ServerRoot

Start-Sleep -Seconds 5
. (Join-Path $PSScriptRoot "_lan-ip.ps1")
$lan = $DiaryLanIPv4
$tokenHint = if ($env:API_TOKEN -eq "dev-token") { "dev-token" } else { ($env:API_TOKEN.Substring(0, [Math]::Min(6, $env:API_TOKEN.Length)) + "...") }

Write-Host "Dev Lite background: http://${lan}:8790  X02:127.0.0.1:8787  adapter=$Adapter  Python: $Py" -ForegroundColor Green
Write-Host "Phone Lab URL: http://${lan}:8790   Token: $tokenHint   mock=$($env:ALLOW_MOCK_PREVIEW)  expose_otp=$($env:EXPOSE_OTP_IN_RESPONSE)" -ForegroundColor Cyan

$h = Invoke-RestMethod "http://127.0.0.1:8790/health" -Headers @{ Authorization = "Bearer $($env:API_TOKEN)" }
$mc = if ($h.mobileclip.available) { "yes" } else { "no ($($h.mobileclip.reason))" }
$provider = $null
try { $provider = $h.x02.detail.provider } catch { }
Write-Host "health: x02=$($h.x02.reachable) ffmpeg=$($h.ffmpeg_available) mc=$mc mock=$($h.allow_mock_preview) provider=$provider"

if ($Adapter -eq "qwen" -and "$provider" -eq "fixture") {
  Write-Host "WARN: requested qwen but X02 still reports fixture - check DASHSCOPE_API_KEY and X02 logs." -ForegroundColor Yellow
}
if ($Adapter -eq "qwen" -and $h.allow_mock_preview -eq $true) {
  Write-Host "WARN: mock=true on quality path - App internal beta will reject. Harden .env and restart." -ForegroundColor Yellow
}
