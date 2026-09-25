Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path
uvicorn bff.main:app --host 0.0.0.0 --port 8790 --reload
