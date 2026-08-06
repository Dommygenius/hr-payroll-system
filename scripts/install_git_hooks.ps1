# Install git hooks for automatic push after commits.
$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$hooksDir = Join-Path $repoRoot ".git\hooks"
$source = Join-Path $repoRoot "scripts\hooks\post-commit.ps1"
$target = Join-Path $hooksDir "post-commit"

if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Error "Run git init first."
}

@(
    "@echo off",
    "powershell -NoProfile -ExecutionPolicy Bypass -File `"$source`""
) | Set-Content -Path $target -Encoding ASCII

Write-Host "Installed post-commit hook -> $target"
Write-Host "Every git commit will auto-push to origin."
