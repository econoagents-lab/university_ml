[CmdletBinding()]
param(
    [string]$PrivateDataDir = "",
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"

if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[OK] MLU_PRIVATE_DATA_DIR=$PrivateDataDir" -ForegroundColor Green
}

python scripts/108_run_v20_productized_commercial_intelligence_os.py

if ($RunTests) {
    pytest -q
}

if ($OpenReport) {
    $report = "reports/productized_os/productized_os_index.html"
    if (Test-Path $report) { Start-Process $report }
}
