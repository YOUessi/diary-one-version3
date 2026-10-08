# Download official MobileCLIP-S0 checkpoint (Apple ML Research).
# Source: https://github.com/apple/ml-mobileclip/blob/main/get_pretrained_models.sh
$ErrorActionPreference = "Stop"
$Url = "https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s0.pt"
$ExpectedSha = "809b408eff74f8058843e86a1f92967097d42ba782450e85b8f4867b7f0ca0b7"

$RootCandidates = @(
  (Join-Path $PSScriptRoot "..\..\..\..\diary_one_app_evidence_v0_2_dev8_mobileclip_router"),
  "E:\AI耳机\diary_one_app_evidence_v0_2_dev8_mobileclip_router"
)
$EvidenceRoot = $null
foreach ($c in $RootCandidates) {
  try {
    $r = Resolve-Path $c -ErrorAction Stop
    if (Test-Path (Join-Path $r "src\diary_one_app\engine\semantic.py")) {
      $EvidenceRoot = $r.Path
      break
    }
  } catch {
    continue
  }
}
if (-not $EvidenceRoot) {
  throw "Evidence router package not found"
}

$DestDir = Join-Path $EvidenceRoot "checkpoints"
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
$Dest = Join-Path $DestDir "mobileclip_s0.pt"

$needDownload = $true
if (Test-Path -LiteralPath $Dest) {
  $hash = (Get-FileHash -LiteralPath $Dest -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($hash -eq $ExpectedSha) {
    Write-Host "Already present and SHA256 OK: $Dest"
    $needDownload = $false
  } else {
    Write-Host "Existing file hash mismatch ($hash) - re-downloading..."
    Remove-Item -LiteralPath $Dest -Force
  }
}

if ($needDownload) {
  Write-Host "Downloading MobileCLIP-S0 (~216 MB)..."
  Write-Host $Url
  Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
}

$hash = (Get-FileHash -LiteralPath $Dest -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $ExpectedSha) {
  throw "SHA256 mismatch for $Dest expected $ExpectedSha got $hash"
}

[Environment]::SetEnvironmentVariable("DIARY_ONE_MOBILECLIP_CHECKPOINT", $Dest, "User")
$env:DIARY_ONE_MOBILECLIP_CHECKPOINT = $Dest
$sizeMb = [math]::Round((Get-Item $Dest).Length / 1MB, 1)
Write-Host "OK: $Dest"
Write-Host "User env DIARY_ONE_MOBILECLIP_CHECKPOINT set."
Write-Host "Size: $sizeMb MB  SHA256: $hash"
Write-Host "Restart Dev Lite then Lab Ping should show mc=yes."
