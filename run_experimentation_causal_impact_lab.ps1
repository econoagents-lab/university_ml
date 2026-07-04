[CmdletBinding()]
Param(
    [string]$PrivateDataDir = "",
    [switch]$RunTests,
    [switch]$OpenReport
)
$ErrorActionPreference = "Stop"
if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[INFO] MLU_PRIVATE_DATA_DIR=$PrivateDataDir"
}
python scripts/99_run_v18_experimentation_causal_impact_lab.py
if ($RunTests) {
    pytest -q tests/test_experimentation_causal_impact_lab.py
}
if ($OpenReport) {
    $report = "reports/experiments/EXPERIMENTATION_CAUSAL_IMPACT_LAB.md"
    if (Test-Path $report) { Invoke-Item $report }
}
