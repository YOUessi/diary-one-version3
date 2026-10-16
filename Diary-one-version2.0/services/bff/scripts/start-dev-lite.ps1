<#
Start Dev Lite stack for Expo Go (no Docker) — REAL cloud by default.

  1) X02 on 127.0.0.1:8787  (adapter qwen → 阿里云百炼 DashScope)
  2) Dev Lite BFF on 0.0.0.0:8790

Usage:
  .\scripts\start-dev-lite.ps1                 # real qwen (needs DASHSCOPE_API_KEY)
  .\scripts\start-dev-lite.ps1 -Adapter fixture  # ONLY for offline UI debug — not quality
#>
param(
  [ValidateSet("fixture", "qwen")]
  [string]$Adapter = "qwen",
  [int]$BffPort = 8790,
  [int]$X02Port = 8787,
  [switch]$AllowMockPreview
)

$ErrorActionPreference = "Stop"
$ServerRoot = Split-Path -Parent $PSScriptRoot

function Resolve-DiaryPython {
  if ($env:DIARY_ONE_PYTHON -and (Test-Path -LiteralPath $env:DIARY_ONE_PYTHON)) {
    return $env:DIARY_ONE_PYTHON
  }
  $pathDirs = ($env:PATH -split ';') | Where-Object { $_ -and $_ -notmatch 'Anaconda|conda|WindowsApps' }
  foreach ($dir in $pathDirs) {
    $candidate = Join-Path $dir.TrimEnd('\') 'python.exe'
    if (Test-Path -LiteralPath $candidate) { return $candidate }
  }
  return (Get-Command python -ErrorAction Stop).Source
}

$PythonExe = Resolve-DiaryPython
$PythonExeEsc = $PythonExe.Replace("'", "''")
Write-Host "Python for X02/BFF: $PythonExe" -ForegroundColor DarkGray

# Monorepo: services/algorithm/algorithm ; legacy: ../nexleap-diary-one/algorithm or E:\AI耳机\nexleap-diary-one
$candidates = @(
  (Join-Path $ServerRoot "..\algorithm\algorithm"),
  (Join-Path $ServerRoot "..\..\nexleap-diary-one\algorithm"),
  "E:\AI耳机\nexleap-diary-one\algorithm",
  "E:\AI耳机\diary-one\services\algorithm\algorithm"
)
$AlgoRoot = $null
foreach ($c in $candidates) {
  $resolved = $null
  try { $resolved = Resolve-Path $c -ErrorAction Stop } catch { continue }
  if (Test-Path (Join-Path $resolved "src\diary_one_ci\x01_server.py")) {
    $AlgoRoot = $resolved.Path
    break
  }
}
if (-not $AlgoRoot) {
  Write-Error "Algorithm path not found. Expected diary_one_ci under services/algorithm/algorithm"
}

. (Join-Path $PSScriptRoot "_lan-ip.ps1")
$lan = $DiaryLanIPv4

# Prefer User-level DASHSCOPE if process env empty
if (-not $env:DASHSCOPE_API_KEY) {
  $userKey = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
  if ($userKey) { $env:DASHSCOPE_API_KEY = $userKey }
}

Write-Host "=== Diary One Dev Lite (REAL cloud default) ===" -ForegroundColor Cyan
Write-Host "LAN IP for Expo Go: $lan"
Write-Host "BFF:  http://${lan}:$BffPort   Token: dev-token"
Write-Host "X02:  http://127.0.0.1:$X02Port (PC only)"
Write-Host "Algo: $AlgoRoot"
Write-Host "Adapter: $Adapter"

if ($Adapter -eq "qwen") {
  if (-not $env:DASHSCOPE_API_KEY) {
    Write-Host ""
    Write-Host "FIX: MISSING DASHSCOPE_API_KEY — consumer App requires real qwen (no silent fixture)." -ForegroundColor Red
    Write-Host "  .\scripts\set-dashscope-key.ps1 -Key 'sk-...'" -ForegroundColor Yellow
    Write-Host "  Or engineer-only UI: .\scripts\start-dev-lite.ps1 -Adapter fixture -AllowMockPreview" -ForegroundColor DarkYellow
    exit 1
  }
  Write-Host "DashScope key: present ($($env:DASHSCOPE_API_KEY.Substring(0,[Math]::Min(6,$env:DASHSCOPE_API_KEY.Length)))...)" -ForegroundColor Green
} else {
  Write-Host "Fixture mode: NOT real algorithm — Lab/UI only. Do not use for consumer acceptance." -ForegroundColor Yellow
  if (-not $PSBoundParameters.ContainsKey('AllowMockPreview')) {
    $AllowMockPreview = $true
  }
}

$allowMock = if ($AllowMockPreview) { "true" } else { "false" }
# Load User-level SMTP into this process if present
foreach ($name in @("SMTP_HOST","SMTP_PORT","SMTP_USER","SMTP_PASSWORD","SMTP_FROM","SMTP_SECURITY","EXPOSE_OTP_IN_RESPONSE")) {
  if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
    $v = [Environment]::GetEnvironmentVariable($name, "User")
    if ($v) { Set-Item -Path "Env:$name" -Value $v }
  }
}
$exposeOtp = if ($env:SMTP_HOST) { "false" } else { "true" }
if ($null -ne $env:EXPOSE_OTP_IN_RESPONSE -and $env:EXPOSE_OTP_IN_RESPONSE -ne "") {
  $exposeOtp = $env:EXPOSE_OTP_IN_RESPONSE
}

Push-Location $ServerRoot
$__ea = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $PythonExe -m pip install -q legacy-cgi *> $null
$ErrorActionPreference = $__ea
& $PythonExe -c "import cgi" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing legacy-cgi for X02 (Python 3.13+)..."
  & $PythonExe -m pip install legacy-cgi
  & $PythonExe -c "import cgi"
  if ($LASTEXITCODE -ne 0) { throw "X02 requires: $PythonExe -m pip install legacy-cgi" }
}
& $PythonExe -c "import fastapi,uvicorn,httpx,pydantic_settings" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing Python deps (fastapi/uvicorn/httpx)..."
  & $PythonExe -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.32" "httpx>=0.28" "pydantic-settings>=2.6" "python-multipart>=0.0.17"
}
Pop-Location

$dashEscaped = $env:DASHSCOPE_API_KEY -replace "'", "''"

$x02Cmd = @"
Set-Location '$AlgoRoot'
`$env:PYTHONPATH = 'src'
`$env:PYTHONDONTWRITEBYTECODE = '1'
`$env:DASHSCOPE_API_KEY = '$dashEscaped'
Write-Host 'Starting X02 on 127.0.0.1:$X02Port adapter=$Adapter'
'$PythonExeEsc' -m diary_one_ci.x01_server --adapter $Adapter --host 127.0.0.1 --port $X02Port
"@

# MobileCLIP reference package (Windows local light semantic analyze)
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
# Default checkpoint locations (user must place Apple research weight here)
if (-not $env:DIARY_ONE_MOBILECLIP_CHECKPOINT) {
  $userCkpt = [Environment]::GetEnvironmentVariable("DIARY_ONE_MOBILECLIP_CHECKPOINT", "User")
  if ($userCkpt) { $env:DIARY_ONE_MOBILECLIP_CHECKPOINT = $userCkpt }
}
if (-not $env:DIARY_ONE_MOBILECLIP_CHECKPOINT -and $EvidenceRouterRoot) {
  foreach ($rel in @(
    "local_experiments\mobileclip_s0.pt",
    "checkpoints\mobileclip_s0.pt",
    "mobileclip_s0.pt"
  )) {
    $cand = Join-Path $EvidenceRouterRoot $rel
    if (Test-Path -LiteralPath $cand) {
      $env:DIARY_ONE_MOBILECLIP_CHECKPOINT = $cand
      break
    }
  }
}
$EvidenceSrc = if ($env:DIARY_ONE_EVIDENCE_ROUTER_ROOT) {
  Join-Path $env:DIARY_ONE_EVIDENCE_ROUTER_ROOT "src"
} else { "" }
$BffPythonPath = if ($EvidenceSrc -and (Test-Path $EvidenceSrc)) {
  "$ServerRoot;$EvidenceSrc"
} else { $ServerRoot }

Write-Host "MobileCLIP checkpoint: $(if ($env:DIARY_ONE_MOBILECLIP_CHECKPOINT) { $env:DIARY_ONE_MOBILECLIP_CHECKPOINT } else { '(not set — semantic-analyze returns 501)' })" -ForegroundColor $(if ($env:DIARY_ONE_MOBILECLIP_CHECKPOINT) { 'Green' } else { 'Yellow' })

$ckptEsc = ($env:DIARY_ONE_MOBILECLIP_CHECKPOINT -replace "'", "''")
$erEsc = ($env:DIARY_ONE_EVIDENCE_ROUTER_ROOT -replace "'", "''")
$pyPathEsc = $BffPythonPath -replace "'", "''"

$bffCmd = @"
Set-Location '$ServerRoot'
`$env:PYTHONPATH = '$pyPathEsc'
`$env:API_TOKEN = '$(if ($env:API_TOKEN) { $env:API_TOKEN -replace "'","''" } else { "dev-token" })'
`$env:X02_BASE_URL = 'http://127.0.0.1:$X02Port'
`$env:DEV_LITE_PORT = '$BffPort'
`$env:ALLOW_MOCK_PREVIEW = '$allowMock'
`$env:EXPOSE_OTP_IN_RESPONSE = '$exposeOtp'
`$env:DIARY_ONE_EVIDENCE_ROUTER_ROOT = '$erEsc'
`$env:DIARY_ONE_MOBILECLIP_CHECKPOINT = '$ckptEsc'
`$env:DIARY_ONE_MOBILECLIP_DEVICE = '$(if ($env:DIARY_ONE_MOBILECLIP_DEVICE) { $env:DIARY_ONE_MOBILECLIP_DEVICE } else { 'auto' })'
`$env:DIARY_ONE_MOBILECLIP_PROMPTS = '$(if ($env:DIARY_ONE_MOBILECLIP_PROMPTS) { $env:DIARY_ONE_MOBILECLIP_PROMPTS } else { '1' })'
`$env:SMTP_HOST = '$($env:SMTP_HOST)'
`$env:SMTP_PORT = '$($env:SMTP_PORT)'
`$env:SMTP_USER = '$($env:SMTP_USER)'
`$env:SMTP_PASSWORD = '$($env:SMTP_PASSWORD -replace "'","''")'
`$env:SMTP_FROM = '$($env:SMTP_FROM)'
`$env:SMTP_SECURITY = '$($env:SMTP_SECURITY)'
if (`$env:SMTP_HOST) { Write-Host "SMTP OTP enabled via `$env:SMTP_HOST" } else { Write-Host "OTP: no SMTP — set via .\scripts\set-smtp.ps1 (see docs/REAL_CLOUD_SETUP.md)" }
Write-Host 'Starting Dev Lite BFF on 0.0.0.0:$BffPort (allow_mock=$allowMock)'
Write-Host "MobileCLIP ckpt=`$env:DIARY_ONE_MOBILECLIP_CHECKPOINT"
'$PythonExeEsc' -m uvicorn dev_lite.app:app --host 0.0.0.0 --port $BffPort
"@

Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", $x02Cmd
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoProfile", "-NoExit", "-Command", $bffCmd

Write-Host ""
Write-Host "Opened 2 terminals (X02 + BFF)." -ForegroundColor Green
Write-Host "Phone Lab: Apply → Ping (x02=up) → Demo photo"
Write-Host "Health: http://${lan}:$BffPort/health"
Write-Host "Mock preview: $allowMock (must be false for real quality)"
