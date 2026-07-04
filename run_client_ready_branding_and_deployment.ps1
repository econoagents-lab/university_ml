[CmdletBinding()]
param(
    [switch]$RunTests,
    [switch]$OpenLanding,
    [string]$PrivateDataDir = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if ($PrivateDataDir -ne "") {
    $env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir
    Write-Host "[INFO] MLU_PRIVATE_DATA_DIR=$PrivateDataDir"
}

python scripts/112_run_v21_client_ready_branding_and_deployment.py

if ($RunTests) {
    pytest -q tests/test_client_ready_branding_and_deployment.py
}

if ($OpenLanding) {
    Start-Process (Join-Path $ProjectRoot "reports/client_ready_branding/LANDING_PAGE_CLIENT_DEMO.html")
}
