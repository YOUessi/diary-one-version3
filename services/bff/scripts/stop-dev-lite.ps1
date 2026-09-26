# Stop Dev Lite / X02 processes on 8787 + 8790
$ErrorActionPreference = "Continue"
$ports = @(8787, 8790)
foreach ($port in $ports) {
  $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
  foreach ($c in $conns) {
    $procId = $c.OwningProcess
    if (-not $procId) { continue }
    try {
      $p = Get-Process -Id $procId -ErrorAction Stop
      Write-Host "Stopping PID $procId ($($p.ProcessName)) on :$port"
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    } catch {
      Write-Host "Port $port owner $procId already gone"
    }
  }
}
Start-Sleep -Seconds 1
$left = @()
foreach ($port in $ports) {
  if (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue) {
    $left += $port
  }
}
if ($left.Count -eq 0) {
  Write-Host "Dev Lite ports 8787/8790 are free." -ForegroundColor Green
} else {
  Write-Host "Still listening: $($left -join ', ') — close remaining python windows manually." -ForegroundColor Yellow
}
