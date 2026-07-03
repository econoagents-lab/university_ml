Param(
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "=== Machine Learning University v0.9 Decision Dashboard API ===" -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . ".\.venv\Scripts\Activate.ps1"
}

python scripts/41_run_v09_decision_dashboard_pipeline.py

if ($RunTests) {
    python -m pytest -q
}

$Report = Join-Path $ProjectRoot "reports\dashboard\EXECUTIVE_DECISION_BRIEF_RIESGO_CAIDA.md"
if ($OpenReport -and (Test-Path $Report)) {
    Invoke-Item $Report
}

Write-Host "OK v0.9 bitácora/dashboard pipeline completado." -ForegroundColor Green
