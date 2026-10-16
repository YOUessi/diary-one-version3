# Validates an on-device bundle.json against handoff bundle.py (V03/V04 gate).
# Usage: .\scripts\validate-bundle-gate.ps1 -BundleJson "C:\path\to\bundle.json"
param(
  [Parameter(Mandatory = $true)]
  [string]$BundleJson
)

$HandoffRoot = Join-Path $PSScriptRoot "..\..\codex_diary_one_algorithm_v1_75_engineering_handoff_20260916"
if (-not (Test-Path $HandoffRoot)) {
  Write-Error "Handoff folder not found: $HandoffRoot"
  exit 1
}

$env:PYTHONPATH = Join-Path $HandoffRoot "src"
python -c @"
from pathlib import Path
from diary_one_ci.bundle import load_any_bundle
p = Path(r'$BundleJson')
bundle = load_any_bundle(p)
print('OK', bundle.validation['validation_version'], 'assets=', bundle.validation['asset_count'])
"@
