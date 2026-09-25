Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path
python -m worker.main
