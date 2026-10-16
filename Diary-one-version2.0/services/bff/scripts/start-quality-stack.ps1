<#
Quality stack for grounded chapters (NO mock).

  - X02 adapter = qwen (requires DASHSCOPE_API_KEY)
  - Dev Lite ALLOW_MOCK_PREVIEW = false
  - Fails fast if Key missing (does NOT silently fall back to fixture)

Usage:
  .\scripts\set-dashscope-key.ps1 -Key 'sk-...'
  .\scripts\start-quality-stack.ps1

Then:
  .\scripts\smoke-cloud-pack.ps1 -MediaDir D:\packs\day1 -RequireGrounded -ReportDir $env:TEMP\diary-reports
#>
$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

if (-not $env:DASHSCOPE_API_KEY) {
  $userKey = [Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
  if ($userKey) { $env:DASHSCOPE_API_KEY = $userKey }
}
if (-not $env:DASHSCOPE_API_KEY) {
  throw @"
DASHSCOPE_API_KEY missing.

  .\scripts\set-dashscope-key.ps1 -Key 'sk-...'
  .\scripts\start-quality-stack.ps1
"@
}

Write-Host "=== Diary One QUALITY stack (qwen + mock OFF) ===" -ForegroundColor Cyan
& (Join-Path $ScriptRoot "stop-dev-lite.ps1") -ErrorAction SilentlyContinue
& (Join-Path $ScriptRoot "start-dev-lite.ps1") -Adapter qwen -AllowMockPreview:$false
