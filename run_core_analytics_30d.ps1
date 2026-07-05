Param(
    [string]$PrivateDataDir = "C:\Repos\freelance\ml_university_ready\data\raw\sperant",
    [switch]$OpenPlan
)

$ErrorActionPreference = "Stop"
$env:MLU_PRIVATE_DATA_DIR = $PrivateDataDir

Write-Host "== CORE_ANALYTICS_30D_PLAN_v1 ==" -ForegroundColor Cyan
Write-Host "PrivateDataDir: $PrivateDataDir"

python scripts/run_core_analytics_30d.py --private-data-dir "$PrivateDataDir"

if ($OpenPlan) {
    Start-Process "CORE_ANALYTICS_30D_PLAN_v1.md"
}
