Param(
    [string]$PrivateDataDir = "",
    [switch]$RunTests,
    [switch]$OpenIndex
)
$ErrorActionPreference = "Stop"
if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[INFO] MLU_PRIVATE_DATA_DIR=$PrivateDataDir"
}
python scripts/128_run_v25_client_success_and_renewal_intelligence.py
if ($RunTests) {
    pytest -q tests/test_client_success_and_renewal_intelligence.py
}
if ($OpenIndex) {
    Start-Process "reports/client_success/client_success_index.html"
}
