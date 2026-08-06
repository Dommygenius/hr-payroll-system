# Install git hooks for automatic push after commits.
$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$hooksDir = Join-Path $repoRoot ".git\hooks"
$autoPush = Join-Path $repoRoot "scripts\auto_push.ps1"
$target = Join-Path $hooksDir "post-commit"

if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Error "Run git init first."
}

$hookPath = $autoPush -replace '\\', '/'
$hookContent = "#!/bin/sh`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$hookPath`" -PushOnly`n"

# LF line endings required — CRLF breaks the shebang on Windows Git.
[System.IO.File]::WriteAllText($target, $hookContent)

Write-Host "Installed post-commit hook -> $target"
Write-Host "Every git commit will auto-push to origin."
