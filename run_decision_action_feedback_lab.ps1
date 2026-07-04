[CmdletBinding()]
Param(
    [string]$PrivateDataDir = "",
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[OK] MLU_PRIVATE_DATA_DIR=$env:MLU_PRIVATE_DATA_DIR" -ForegroundColor Green
}

python scripts/94_run_v17_decision_action_feedback_lab.py

if ($RunTests) {
    pytest -q
}

if ($OpenReport) {
    $Report = Join-Path $Root "reports\action_feedback\DECISION_ACTION_FEEDBACK_LAB.md"
    if (Test-Path $Report) { Invoke-Item $Report }
}
