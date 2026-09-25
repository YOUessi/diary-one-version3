"""
Save 阿里云百炼 DashScope API Key to Windows User environment (not Git).

  .\scripts\set-dashscope-key.ps1 -Key 'sk-xxxxxxxx'
"""
param(
  [Parameter(Mandatory = $true)]
  [string]$Key
)

$ErrorActionPreference = "Stop"
$trimmed = $Key.Trim()
if (-not $trimmed.StartsWith("sk-")) {
  Write-Error "Key should look like sk-... (百炼通用 API Key，不要用 sk-sp-/sk-ws- 专属套餐 Key)"
}

[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", $trimmed, "User")
$env:DASHSCOPE_API_KEY = $trimmed
Write-Host "Saved DASHSCOPE_API_KEY to User environment." -ForegroundColor Green
Write-Host "Prefix: $($trimmed.Substring(0, [Math]::Min(8, $trimmed.Length)))…"
Write-Host "Next: .\scripts\start-dev-lite.ps1   (default adapter=qwen)"
Write-Host "Get key: https://bailian.console.aliyun.com/?tab=model#/api-key  (地域选华北2北京)"
