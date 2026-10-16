<#
Start only X02 :8787 for the Docker production stack (does not touch BFF :8790).

  .\scripts\start-x02.ps1              # qwen if DASHSCOPE_API_KEY is set
  .\scripts\start-x02.ps1 -Adapter fixture
#>
param(
  [ValidateSet("fixture", "qwen")]
  [string]$Adapter = "qwen",
  [int]$X02Port = 8787
)

$ErrorActionPreference = "Stop"
$ServerRoot = Split-Path -Parent $PSScriptRoot

function Resolve-DiaryPython {
  if ($env:DIARY_ONE_PYTHON -and (Test-Path -LiteralPath $env:DIARY_ONE_PYTHON)) {
    return $env:DIARY_ONE_PYTHON
  }
  if (Test-Path "C:\Python314\python.exe") { return "C:\Python314\python.exe" }
  $pathDirs = ($env:PATH -split ';') | Where-Object { $_ -and $_ -notmatch 'Anaconda|conda|WindowsApps' }
  foreach ($dir in $pathDirs) {
    $candidate = Join-Path $dir.TrimEnd('\') 'python.exe'
    if (Test-Path -LiteralPath $candidate) { return $candidate }
  }
  return (Get-Command python -ErrorAction Stop).Source
}

$PythonExe = Resolve-DiaryPython
$AlgoRoot = $null
foreach ($c in @(
    (Join-Path $ServerRoot "..\algorithm\algorithm"),
    "E:\AI耳机\diary-one\services\algorithm\algorithm"
  )) {
  try {
    $resolved = Resolve-Path $c -ErrorAction Stop
    if (Test-Path (Join-Path $resolved "src\diary_one_ci\x01_server.py")) {
      $AlgoRoot = $resolved.Path
      break
    }
  } catch { }
}
if (-not $AlgoRoot) { throw "Algorithm path not found" }

if (-not $env:DASHSCOPE_API_KEY) {
  $userKey = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
  if ($userKey) { $env:DASHSCOPE_API_KEY = $userKey }
}

if ($Adapter -eq "qwen" -and -not $env:DASHSCOPE_API_KEY) {
  Write-Host "No DASHSCOPE_API_KEY — X02 fixture (not V1.75 quality)." -ForegroundColor Yellow
  $Adapter = "fixture"
}

Get-NetTCPConnection -LocalPort $X02Port -ErrorAction SilentlyContinue | ForEach-Object {
  Write-Host "Stopping PID $($_.OwningProcess) on :$X02Port"
  Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1

$__ea = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $PythonExe -m pip install -q legacy-cgi fastapi uvicorn httpx pydantic-settings python-multipart *> $null
$ErrorActionPreference = $__ea

$log = Join-Path $env:TEMP "diary-x02.log"
$env:PYTHONPATH = (Join-Path $AlgoRoot "src")
$env:PYTHONDONTWRITEBYTECODE = "1"

$p = Start-Process -WindowStyle Hidden -FilePath $PythonExe `
  -ArgumentList "-m","diary_one_ci.x01_server","--adapter",$Adapter,"--host","127.0.0.1","--port","$X02Port" `
  -WorkingDirectory $AlgoRoot `
  -RedirectStandardOutput $log `
  -RedirectStandardError "$log.err" `
  -PassThru

Write-Host "X02 PID $($p.Id) adapter=$Adapter python=$PythonExe" -ForegroundColor Cyan
Write-Host "Log: $log"

$ok = $false
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Seconds 2
  try {
    $h = Invoke-RestMethod "http://127.0.0.1:$X02Port/health" -TimeoutSec 3
    Write-Host ("health adapter={0} modelReady={1}" -f $h.adapter, $h.modelReady)
    $ok = $true
    break
  } catch {
    if ($p.HasExited) { throw "X02 exited. See $log.err" }
  }
}
if (-not $ok) { throw "X02 did not become healthy on :$X02Port" }
Write-Host "X02 ready  http://127.0.0.1:$X02Port" -ForegroundColor Green
