[CmdletBinding()]
param(
    [switch]$RunTests,
    [switch]$OpenIndex
)
$ErrorActionPreference = "Stop"
Write-Host "[INFO] v1.4 Dashboard Generator From Catalog" -ForegroundColor Cyan
python scripts/80_run_v14_dashboard_generator.py
if ($RunTests) {
    pytest -q
}
if ($OpenIndex) {
    $index = Join-Path (Get-Location) "reports/generated_dashboards/index.html"
    if (Test-Path $index) { Start-Process $index }
}
