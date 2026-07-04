Param(
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "=== Machine Learning University v1.5 Dashboard Metrics Engine ===" -ForegroundColor Cyan
python scripts/84_run_v15_dashboard_metrics_engine.py

if ($RunTests) {
    python -m pytest -q
}

if ($OpenReport) {
    $Report = Join-Path $Root "reports\dashboard_metrics\DASHBOARD_METRICS_ENGINE.md"
    if (Test-Path $Report) { Invoke-Item $Report }
}
