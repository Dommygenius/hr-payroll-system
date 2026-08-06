# Auto-commit (if needed) and push to GitHub origin.
# Used by git post-commit hook and Cursor agent stop hook.
param(
    [switch]$PushOnly,
    [string]$Message = "Auto-sync: workspace update"
)

$ErrorActionPreference = "Continue"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Test-Path ".git")) {
    Write-Host "[auto_push] Not a git repository — skipping."
    exit 0
}

$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "[auto_push] No origin remote configured."
    Write-Host "  Run: powershell -File scripts/setup_github.ps1"
    exit 1
}

if (-not $PushOnly) {
    git add -A
    $status = git status --porcelain
    if ($status) {
        git commit -m $Message
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[auto_push] Commit failed — skipping push."
            exit $LASTEXITCODE
        }
        Write-Host "[auto_push] Committed pending changes."
    }
}

$branch = git rev-parse --abbrev-ref HEAD
git push -u origin $branch 2>&1 | ForEach-Object { Write-Host $_ }

if ($LASTEXITCODE -eq 0) {
    Write-Host "[auto_push] Pushed to origin/$branch"
} else {
    Write-Host "[auto_push] Push failed. Re-authenticate with: gh auth login -h github.com"
    exit $LASTEXITCODE
}

exit 0
