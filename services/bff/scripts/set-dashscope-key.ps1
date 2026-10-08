<#
Save DashScope API Key to Windows User environment (not Git).

  .\scripts\set-dashscope-key.ps1 -Key 'sk-xxxxxxxx'

Accepted:
  - sk-...     old pay-as-you-go keys
  - sk-ws-...  new pay-as-you-go keys (Aliyun security upgrade) OR Coding Plan keys
Rejected:
  - sk-sp-...  Token Plan (different base URL; not used by this stack)
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$Key
)

$ErrorActionPreference = "Stop"
$trimmed = $Key.Trim()

if ($trimmed.StartsWith("sk-sp-")) {
  Write-Host "Token Plan keys (sk-sp-) are not supported. Create a 按量付费 API-KEY." -ForegroundColor Red
  Write-Error "Rejected sk-sp- key."
}

if (-not $trimmed.StartsWith("sk-")) {
  Write-Error "Key must start with sk-"
}

[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", $trimmed, "User")
$env:DASHSCOPE_API_KEY = $trimmed
$prefixLen = [Math]::Min(10, $trimmed.Length)
Write-Host "Saved DASHSCOPE_API_KEY to User environment." -ForegroundColor Green
Write-Host ("Prefix: {0}..." -f $trimmed.Substring(0, $prefixLen))
if ($trimmed.StartsWith("sk-ws-")) {
  Write-Host "Note: new Aliyun keys start with sk-ws-. This stack uses compatible-mode HTTP." -ForegroundColor Yellow
}
Write-Host "Next:"
Write-Host "  .\scripts\stop-dev-lite.ps1"
Write-Host "  .\scripts\start-dev-lite.ps1 -Adapter qwen"
