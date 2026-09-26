# Start X02 + BFF without Conda pop-up windows (hidden processes)
$ErrorActionPreference = "Stop"
$ServerRoot = Split-Path -Parent $PSScriptRoot

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

$env:PYTHONPATH = "$AlgoRoot\src"
Start-Process -WindowStyle Hidden -FilePath $Py -ArgumentList "-m","diary_one_ci.x01_server","--adapter","fixture","--host","127.0.0.1","--port","8787" -WorkingDirectory $AlgoRoot

Start-Sleep -Seconds 2
$env:PYTHONPATH = $ServerRoot
$env:API_TOKEN = "dev-token"
$env:X02_BASE_URL = "http://127.0.0.1:8787"
$env:EXPOSE_OTP_IN_RESPONSE = "true"
$env:ALLOW_MOCK_PREVIEW = "false"
Start-Process -WindowStyle Hidden -FilePath $Py -ArgumentList "-m","uvicorn","dev_lite.app:app","--host","0.0.0.0","--port","8790" -WorkingDirectory $ServerRoot

Start-Sleep -Seconds 5
$lan = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' } | Select-Object -First 1).IPAddress
Write-Host "Dev Lite background: http://${lan}:8790  X02:127.0.0.1:8787  Python: $Py" -ForegroundColor Green
$h = Invoke-RestMethod "http://127.0.0.1:8790/health" -Headers @{ Authorization = "Bearer dev-token" }
Write-Host "health: x02=$($h.x02.reachable) ffmpeg=$($h.ffmpeg_available)"
