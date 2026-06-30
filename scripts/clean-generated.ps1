$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Remove-Item -Recurse -Force "artifacts" -ErrorAction SilentlyContinue
Remove-Item -Force "migration-safety-evidence.json" -ErrorAction SilentlyContinue
Remove-Item -Force "*.evidence.json" -ErrorAction SilentlyContinue
