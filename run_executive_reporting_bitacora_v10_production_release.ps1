[CmdletBinding()]
Param(
    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$OpenReport
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (!(Test-Path ".venv")) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
if ($InstallDeps) { pip install -r requirements.txt }
python scripts/45_run_v10_production_release.py
if ($RunTests) { pytest -q }
$Report = Join-Path $Root "reports\production\PRODUCTION_READINESS_REPORT.md"
if ($OpenReport -and (Test-Path $Report)) { Invoke-Item $Report }
Write-Host "[OK] v1.0 production release runner completed" -ForegroundColor Green
