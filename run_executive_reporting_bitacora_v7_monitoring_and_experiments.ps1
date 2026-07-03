Param(
    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$OpenReport
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
Write-Host "=== MLU v0.7 Monitoring & Experiments ===" -ForegroundColor Cyan
if (!(Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\Activate.ps1"
if ($InstallDeps) { python -m pip install --upgrade pip; pip install -r requirements.txt }
$steps = @(
    "scripts/15_prepare_model_ready_dataset.py",
    "scripts/16_train_evaluate_official_model.py",
    "scripts/14_score_actual_riesgo_caida.py",
    "scripts/28_weekly_monitoring_report.py"
)
foreach ($s in $steps) {
    Write-Host "Running $s" -ForegroundColor Yellow
    python $s
}
if ($RunTests) { python -m pytest -q }
$report = Join-Path $ProjectRoot "reports\executive\WEEKLY_MONITORING_REPORT.md"
Write-Host "Reporte: $report" -ForegroundColor Green
if ($OpenReport -and (Test-Path $report)) { Invoke-Item $report }
