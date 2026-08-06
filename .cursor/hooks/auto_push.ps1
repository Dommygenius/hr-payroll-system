# Cursor stop hook — commit pending changes and push when an agent session ends.
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot
& (Join-Path $repoRoot "scripts\auto_push.ps1") -Message "Auto-sync: agent session update"
exit 0
