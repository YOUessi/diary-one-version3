"""
Start Dev Lite stack for Expo Go (no Docker):

  1) X02 research server on 127.0.0.1:8787
  2) Dev Lite BFF on 0.0.0.0:8790 (phone uses LAN IP)

Usage:
  .\scripts\start-dev-lite.ps1                 # fixture adapter (pipeline only)
  .\scripts\start-dev-lite.ps1 -Adapter qwen  # real V1.75 (needs DASHSCOPE_API_KEY)
"""
param(
  [ValidateSet("fixture", "qwen")]
  [string]$Adapter = "fixture",
  [int]$BffPort = 8790,
  [int]$X02Port = 8787
)

$ErrorActionPreference = "Stop"
$ServerRoot = Split-Path -Parent $PSScriptRoot
$AlgoRoot = Resolve-Path (Join-Path $ServerRoot "..\nexleap-diary-one\algorithm")

if (-not (Test-Path $AlgoRoot)) {
  Write-Error "Algorithm path not found: $AlgoRoot"
}

$lan = Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' } |
  Select-Object -First 1 -ExpandProperty IPAddress

Write-Host "=== Diary One Dev Lite ===" -ForegroundColor Cyan
Write-Host "LAN IP for Expo Go: $lan"
Write-Host "BFF:  http://${lan}:$BffPort   Token: dev-token"
Write-Host "X02:  http://127.0.0.1:$X02Port (PC only)"
Write-Host "Adapter: $Adapter"
if ($Adapter -eq "qwen") {
  if (-not $env:DASHSCOPE_API_KEY) {
    Write-Host "WARNING: DASHSCOPE_API_KEY not set — qwen adapter will report modelReady=false" -ForegroundColor Yellow
  }
} else {
  Write-Host "Fixture mode: App pipeline works; algorithm quality is NOT claimed." -ForegroundColor Yellow
}

# Install minimal Python deps for BFF if missing
Push-Location $ServerRoot
python -c "import fastapi,uvicorn,httpx,pydantic_settings" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Installing Python deps (fastapi/uvicorn/httpx)..."
  python -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.32" "httpx>=0.28" "pydantic-settings>=2.6" "python-multipart>=0.0.17"
}
Pop-Location

$x02Cmd = @"
Set-Location '$AlgoRoot'
`$env:PYTHONPATH = 'src'
`$env:PYTHONDONTWRITEBYTECODE = '1'
Write-Host 'Starting X02 on 127.0.0.1:$X02Port adapter=$Adapter'
python -m diary_one_ci.x01_server --adapter $Adapter --host 127.0.0.1 --port $X02Port
"@

$bffCmd = @"
Set-Location '$ServerRoot'
`$env:PYTHONPATH = '$ServerRoot'
`$env:API_TOKEN = 'dev-token'
`$env:X02_BASE_URL = 'http://127.0.0.1:$X02Port'
`$env:DEV_LITE_PORT = '$BffPort'
Write-Host 'Starting Dev Lite BFF on 0.0.0.0:$BffPort'
python -m uvicorn dev_lite.app:app --host 0.0.0.0 --port $BffPort
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $x02Cmd
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", $bffCmd

Write-Host ""
Write-Host "Opened 2 terminals (X02 + BFF)." -ForegroundColor Green
Write-Host "On phone Expo Go Lab:"
Write-Host "  Cloud target = Production BFF"
Write-Host "  URL = http://${lan}:$BffPort"
Write-Host "  Token = dev-token"
Write-Host "OTP: request returns JSON field dev_code (no real email yet)."
Write-Host "Health: http://${lan}:$BffPort/health"
