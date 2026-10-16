<#
End-to-end quality gate for a real media day pack.

Prereq: quality stack running (qwen + mock off).

  .\scripts\start-quality-stack.ps1
  .\scripts\run-quality-gate.ps1 -MediaDir D:\packs\day1
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$MediaDir,
  [int]$MaxAssets = 40,
  [string]$ReportDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
if (-not $ReportDir) {
  $ReportDir = Join-Path $env:TEMP ("diary-quality-" + (Get-Date -Format "yyyyMMddHHmmss"))
}

Write-Host "=== Quality gate ===" -ForegroundColor Cyan
Write-Host "MediaDir=$MediaDir"
Write-Host "ReportDir=$ReportDir"

& (Join-Path $ScriptRoot "smoke-cloud-pack.ps1") `
  -MediaDir $MediaDir `
  -MaxAssets $MaxAssets `
  -RequireGrounded `
  -ReportDir $ReportDir `
  -TimeoutSec 1200

Write-Host ""
Write-Host "QUALITY GATE PASSED" -ForegroundColor Green
Write-Host "Open reports under: $ReportDir"
