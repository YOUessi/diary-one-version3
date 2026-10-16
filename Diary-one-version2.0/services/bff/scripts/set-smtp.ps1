<#
Save SMTP for real OTP email (Windows User env, not Git).

  .\scripts\set-smtp.ps1 -SmtpHost smtp.163.com -Port 465 -User 'you@163.com' -Password '授权码' -From 'you@163.com'

QQ: smtp.qq.com port 465 ssl, password = 邮箱授权码 (not login password).
163: smtp.163.com port 465 ssl.
Gmail: smtp.gmail.com port 587 -Security starttls, App Password.
#>
param(
  [Parameter(Mandatory = $true)][string]$SmtpHost,
  [int]$Port = 465,
  [Parameter(Mandatory = $true)][string]$User,
  [Parameter(Mandatory = $true)][string]$Password,
  [Parameter(Mandatory = $true)][string]$From,
  [ValidateSet("ssl", "starttls", "none")]
  [string]$Security = "ssl"
)

$ErrorActionPreference = "Stop"
[Environment]::SetEnvironmentVariable("SMTP_HOST", $SmtpHost.Trim(), "User")
[Environment]::SetEnvironmentVariable("SMTP_PORT", "$Port", "User")
[Environment]::SetEnvironmentVariable("SMTP_USER", $User.Trim(), "User")
[Environment]::SetEnvironmentVariable("SMTP_PASSWORD", $Password, "User")
[Environment]::SetEnvironmentVariable("SMTP_FROM", $From.Trim(), "User")
[Environment]::SetEnvironmentVariable("SMTP_SECURITY", $Security, "User")
[Environment]::SetEnvironmentVariable("EXPOSE_OTP_IN_RESPONSE", "false", "User")

$env:SMTP_HOST = $SmtpHost.Trim()
$env:SMTP_PORT = "$Port"
$env:SMTP_USER = $User.Trim()
$env:SMTP_PASSWORD = $Password
$env:SMTP_FROM = $From.Trim()
$env:SMTP_SECURITY = $Security
$env:EXPOSE_OTP_IN_RESPONSE = "false"

Write-Host "SMTP saved. App will NOT show dev_code after you restart BFF." -ForegroundColor Green
Write-Host "Restart: stop-dev-lite.ps1 then start-dev-lite.ps1 -Adapter qwen"
Write-Host "Or Docker: .\scripts\up-docker-stack.ps1"
