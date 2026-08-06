# Install git hooks for automatic push after commits.
$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$hooksDir = Join-Path $repoRoot ".git\hooks"
$autoPush = Join-Path $repoRoot "scripts\auto_push.ps1"
$target = Join-Path $hooksDir "post-commit"

if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Error "Run git init first."
}

# Git for Windows runs hooks via sh — use a shell script that invokes PowerShell.
$hookPath = $autoPush -replace '\\', '/'
$hookContent = @"
#!/bin/sh
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$hookPath" -PushOnly
"@

Set-Content -Path $target -Value $hookContent -Encoding UTF8

Write-Host "Installed post-commit hook -> $target"
Write-Host "Every git commit will auto-push to origin."
