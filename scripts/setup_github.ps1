# One-time GitHub remote setup. Requires: gh auth login -h github.com
param(
    [string]$RepoName = "hr-payroll-system",
    [ValidateSet("public", "private")]
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
}

gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "GitHub CLI is not authenticated."
    Write-Host "Run: gh auth login -h github.com"
    exit 1
}

$existing = $null
git remote get-url origin 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    $existing = git remote get-url origin
}
if ($existing) {
    Write-Host "Origin already set: $existing"
} else {
    gh repo create $RepoName --$Visibility --source=. --remote=origin --push
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Created and linked: $RepoName"
    exit 0
}

git push -u origin HEAD
exit $LASTEXITCODE
