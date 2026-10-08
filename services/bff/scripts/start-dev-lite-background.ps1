# Start X02 + BFF without Conda pop-up windows (hidden processes)
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
Get-NetTCPConnection -LocalPort 8787,8790 -ErrorAction SilentlyContinue | ForEach-Object {
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

$env:PYTHONPATH = "$AlgoRoot\src"
Start-Process -WindowStyle Hidden -FilePath $Py -ArgumentList "-m","diary_one_ci.x01_server","--adapter","fixture","--host","127.0.0.1","--port","8787" -WorkingDirectory $AlgoRoot

Start-Sleep -Seconds 2
$env:PYTHONPATH = if ($EvidenceSrc -and (Test-Path $EvidenceSrc)) { "$ServerRoot;$EvidenceSrc" } else { $ServerRoot }
$env:API_TOKEN = "dev-token"
$env:X02_BASE_URL = "http://127.0.0.1:8787"
$env:EXPOSE_OTP_IN_RESPONSE = "true"
# Fixture Expo Go loop: mock Diary write-back if X02 rejects empty/minimal bundles
$env:ALLOW_MOCK_PREVIEW = "true"
if (-not $env:DIARY_ONE_MOBILECLIP_DEVICE) { $env:DIARY_ONE_MOBILECLIP_DEVICE = "auto" }
if (-not $env:DIARY_ONE_MOBILECLIP_PROMPTS) { $env:DIARY_ONE_MOBILECLIP_PROMPTS = "1" }
Start-Process -WindowStyle Hidden -FilePath $Py -ArgumentList "-m","uvicorn","dev_lite.app:app","--host","0.0.0.0","--port","8790" -WorkingDirectory $ServerRoot

Start-Sleep -Seconds 5
. (Join-Path $PSScriptRoot "_lan-ip.ps1")
$lan = $DiaryLanIPv4
Write-Host "Dev Lite background: http://${lan}:8790  X02:127.0.0.1:8787  Python: $Py" -ForegroundColor Green
Write-Host "Phone Lab URL: http://${lan}:8790   Token: dev-token   (ALLOW_MOCK_PREVIEW=true)" -ForegroundColor Cyan
$h = Invoke-RestMethod "http://127.0.0.1:8790/health" -Headers @{ Authorization = "Bearer dev-token" }
$mc = if ($h.mobileclip.available) { "yes" } else { "no ($($h.mobileclip.reason))" }
Write-Host "health: x02=$($h.x02.reachable) ffmpeg=$($h.ffmpeg_available) mc=$mc mock=$($h.allow_mock_preview)"
