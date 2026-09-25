# Diary One - Windows Android env setup. Run from project root:
#   powershell -ExecutionPolicy Bypass -File .\scripts\setup-android-windows.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "=== Diary One Android setup ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"

$candidates = @(
  $env:ANDROID_HOME,
  $env:ANDROID_SDK_ROOT,
  (Join-Path $env:LOCALAPPDATA "Android\Sdk"),
  (Join-Path $env:USERPROFILE "Android\Sdk")
) | Where-Object { $_ -and (Test-Path $_) }

$sdk = $candidates | Select-Object -First 1
if (-not $sdk) {
  $sdkDefault = Join-Path $env:LOCALAPPDATA "Android\Sdk"
  Write-Host ""
  Write-Host "[!] Android SDK not found." -ForegroundColor Yellow
  Write-Host "In Android Studio: More Actions -> SDK Manager" -ForegroundColor Yellow
  Write-Host "Install: Platform API 34, Build-Tools, Platform-Tools, Emulator, Command-line Tools" -ForegroundColor Yellow
  Write-Host "Default SDK path: $sdkDefault" -ForegroundColor Yellow
  Write-Host "Then create a Pixel 6 API 34 AVD in Device Manager and re-run this script." -ForegroundColor Yellow
  exit 1
}

Write-Host "SDK: $sdk" -ForegroundColor Green

$platformTools = Join-Path $sdk "platform-tools"
$emulator = Join-Path $sdk "emulator\emulator.exe"
$adb = Join-Path $platformTools "adb.exe"

[Environment]::SetEnvironmentVariable("ANDROID_HOME", $sdk, "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $sdk, "User")

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$toAdd = @(
  $platformTools,
  (Join-Path $sdk "emulator"),
  (Join-Path $sdk "cmdline-tools\latest\bin")
)
foreach ($segment in $toAdd) {
  if ((Test-Path $segment) -and ($userPath -notlike "*$segment*")) {
    $userPath = $segment + ";" + $userPath
  }
}
[Environment]::SetEnvironmentVariable("Path", $userPath, "User")

$env:ANDROID_HOME = $sdk
$env:ANDROID_SDK_ROOT = $sdk
$env:Path = $platformTools + ";" + $env:Path

$androidDir = Join-Path $ProjectRoot "android"
if (Test-Path $androidDir) {
  $localProps = Join-Path $androidDir "local.properties"
  $sdkEscaped = $sdk -replace '\\', '/'
  Set-Content -Path $localProps -Value ("sdk.dir=" + $sdkEscaped) -Encoding UTF8
  Write-Host "Wrote android\local.properties" -ForegroundColor Green
}

if (Test-Path $adb) {
  & $adb version
} else {
  Write-Host "[!] Missing platform-tools. Install via SDK Manager." -ForegroundColor Yellow
}

if (Test-Path $emulator) {
  Write-Host "AVDs:" -ForegroundColor Cyan
  & $emulator -list-avds
} else {
  Write-Host "[!] Emulator not installed. Enable Android Emulator in SDK Manager." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Next steps ===" -ForegroundColor Cyan
Write-Host "1. Close and reopen your terminal"
Write-Host "2. cd $ProjectRoot"
Write-Host "3. Start emulator from Android Studio Device Manager"
Write-Host "4. npx expo run:android"
Write-Host "5. Later: npx expo start --dev-client  (press a)"
