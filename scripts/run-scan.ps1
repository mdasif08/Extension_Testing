param(
    [string]$MigrationPath = "db/migrations",
    [string]$EvidenceFile = "artifacts/migration-safety-evidence.json"
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    throw "Python was not found. Install Python 3 or add it to PATH."
}

& $pythonCmd.Source "tools/migration_safety_scan.py" $MigrationPath --evidence-file $EvidenceFile
exit $LASTEXITCODE
