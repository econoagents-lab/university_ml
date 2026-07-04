[CmdletBinding()]
Param(
    [switch]$RunTests,
    [switch]$OpenReport,
    [string]$PrivateDataDir = ""
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[INFO] MLU_PRIVATE_DATA_DIR=$PrivateDataDir"
}
python scripts/88_run_v16_real_mart_expansion.py
if ($RunTests) { pytest -q }
if ($OpenReport) { Invoke-Item "reports/real_marts/REAL_MART_EXPANSION.md" }
