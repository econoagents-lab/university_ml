[CmdletBinding()]
param(
    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$OpenReport,
    [switch]$ExportStaticSite
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "[INFO] Machine Learning University v1.2 - GitHub Actions Alerts" -ForegroundColor Cyan

if ($InstallDeps) {
    Write-Host "[INFO] Installing dependencies" -ForegroundColor Cyan
    python -m pip install --upgrade pip
    pip install pandas pyyaml pytest
}

python scripts/66_build_all_alerts.py

if ($ExportStaticSite) {
    python scripts/68_export_alerts_static_site.py
}

if ($RunTests) {
    pytest -q
}

$Report = Join-Path $ProjectRoot "reports\alerts\ALERTS_MANIFEST.md"
Write-Host "[OK] Alerts manifest: $Report" -ForegroundColor Green

if ($OpenReport -and (Test-Path $Report)) {
    Start-Process $Report
}
