# Git post-commit hook — push after every local commit.
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
& (Join-Path $repoRoot "scripts\auto_push.ps1") -PushOnly
