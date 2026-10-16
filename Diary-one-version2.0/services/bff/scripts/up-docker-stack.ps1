# Bring up production-ish Docker stack (Postgres/Redis/MinIO/BFF/Worker)
# Prerequisites: Docker Desktop running + WSL2 enabled
$ErrorActionPreference = "Stop"

$dockerDesktop = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\Docker Desktop.exe"
$dockerBin = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin"
if (Test-Path (Join-Path $dockerBin "docker.exe")) {
  $env:Path = "$dockerBin;" + $env:Path
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw "docker CLI not found. Install/start Docker Desktop first."
}

function Test-DockerEngine {
  $prev = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  $out = & docker info 2>&1
  $code = $LASTEXITCODE
  $ErrorActionPreference = $prev
  if ($code -ne 0) { return $false }
  $text = ($out | Out-String)
  # Do not match "npipe:" — a healthy Windows docker info lists the named pipe host.
  if ($text -match 'Cannot connect to the Docker daemon|failed to connect to the docker API|The system cannot find the file specified') {
    return $false
  }
  return $true
}

if (-not (Test-DockerEngine)) {
  if (Test-Path $dockerDesktop) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan
    Start-Process $dockerDesktop
  }
  $ready = $false
  for ($i = 1; $i -le 36; $i++) {
    Start-Sleep -Seconds 5
    if (Test-DockerEngine) {
      Write-Host "Docker engine ready after $($i * 5)s" -ForegroundColor Green
      $ready = $true
      break
    }
    Write-Host "Waiting for Docker engine ($i/36)..."
  }
  if (-not $ready) {
    throw @"
Docker engine not responding.

1) Open Docker Desktop and wait until it says Running
2) If first launch: enable WSL2 (wsl --install) then reboot
3) Re-run this script — do not kill processes named docker / com.docker
"@
  }
} else {
  Write-Host "Docker engine OK" -ForegroundColor Green
}

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example"
}

# Free :8790 only if a non-Docker process (e.g. Dev Lite uvicorn) is bound
$protect = '(?i)docker|com\.docker|vpnkit|wsl|vmmem'
Get-NetTCPConnection -LocalPort 8790 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object {
    $ownerPid = $_
    if (-not $ownerPid) { return }
    $proc = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
    if (-not $proc) { return }
    if ($proc.ProcessName -match $protect) {
      Write-Host "Leaving Docker listener on :8790 (PID $ownerPid $($proc.ProcessName))"
      return
    }
    Write-Host "Stopping Dev Lite on :8790 (PID $ownerPid $($proc.ProcessName))"
    Stop-Process -Id $ownerPid -Force -ErrorAction SilentlyContinue
  }

# Load User-level SMTP/DashScope into this process so compose interpolates them
foreach ($name in @(
    "SMTP_HOST","SMTP_PORT","SMTP_USER","SMTP_PASSWORD","SMTP_FROM","SMTP_SECURITY",
    "EXPOSE_OTP_IN_RESPONSE","DASHSCOPE_API_KEY"
  )) {
  if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
    $v = [Environment]::GetEnvironmentVariable($name, "User")
    if ($v) { Set-Item -Path "Env:$name" -Value $v }
  }
}
Write-Host "docker compose up -d --build ..." -ForegroundColor Cyan
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "compose up failed" }

Write-Host "db_init ..." -ForegroundColor Cyan
docker compose run --rm bff python -m shared.db_init
if ($LASTEXITCODE -ne 0) { throw "db_init failed" }

Write-Host "smoke-docker.ps1 ..." -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "smoke-docker.ps1")

Write-Host ""
Write-Host "Stack up. BFF http://127.0.0.1:8790  (X02 still on host :8787 if worker needs it)" -ForegroundColor Green
Write-Host "Stop:  docker compose down"
Write-Host "Logs:  docker compose logs -f bff worker"
