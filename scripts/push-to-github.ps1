# Push Diary_one to Nexleap-Tech
# Run AFTER: gh auth login (browser) succeeds
$ErrorActionPreference = "Stop"
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Set-Location "E:\AI耳机\diary-one"

gh auth status
if ($LASTEXITCODE -ne 0) {
  Write-Host "Not logged in. Run: gh auth login -h github.com -p https -w -s repo,read:org,workflow"
  exit 1
}

$repoName = "Diary_one"
$owner = "Nexleap-Tech"
$full = "$owner/$repoName"

$exists = gh repo view $full 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Creating private repo $full ..."
  gh repo create $full --private --description "Diary One — iOS app + BFF + algorithm + test/progress (commercial internal)" --source "." --remote origin --push
} else {
  Write-Host "Repo exists. Setting remote and pushing..."
  $url = "https://github.com/$full.git"
  $remotes = git remote
  if ($remotes -notcontains "origin") {
    git remote add origin $url
  } else {
    git remote set-url origin $url
  }
  git push -u origin main
}

Write-Host "Done: https://github.com/$full"
