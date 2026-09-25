"""
Save SMTP settings for real OTP email (User env, not Git).

  .\scripts\set-smtp.ps1 -SmtpHost smtp.163.com -Port 465 -User you@163.com -Password '授权码' -From you@163.com

Free options: 163/QQ 邮箱授权码, or Resend/Brevo SMTP.
"""
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

Write-Host "SMTP saved to User environment. OTP will be emailed; App will NOT show dev_code." -ForegroundColor Green
Write-Host "Restart Dev Lite after this."
