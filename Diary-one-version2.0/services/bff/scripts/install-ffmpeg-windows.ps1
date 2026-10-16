# Install ffmpeg for Daily Recap render (winget)
$ErrorActionPreference = "Stop"
Write-Host "Installing ffmpeg via winget (Gyan.FFmpeg)..." -ForegroundColor Cyan
winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
Write-Host ""
Write-Host "Restart terminal, then: ffmpeg -version" -ForegroundColor Green
Write-Host "Re-run Dev Lite and check /health -> ffmpeg_available: true"
