[CmdletBinding()]
Param(
    [string]$PrivateDataDir = "",
    [switch]$RunTests,
    [switch]$OpenReport
)
$ErrorActionPreference = "Stop"
if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[OK] MLU_PRIVATE_DATA_DIR=$PrivateDataDir" -ForegroundColor Green
}
$env:PYTHONPATH = (Get-Location).Path
python scripts/104_run_v19_experiment_power_policy_engine.py
if ($RunTests) {
    pytest -q tests/test_experiment_power_policy_engine.py
}
if ($OpenReport) {
    Start-Process "reports/policy_engine/EXPERIMENT_POWER_AND_POLICY_ENGINE.md"
}
