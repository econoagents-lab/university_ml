[CmdletBinding()]
param(
    [switch]$RunTests,
    [switch]$OpenIndex
)
$ErrorActionPreference = "Stop"
Write-Host "[v2.2] Generando paquetes cliente multi-tenant..." -ForegroundColor Cyan
python scripts/116_run_v22_multi_tenant_client_packaging.py
if ($RunTests) {
    pytest -q tests/test_multi_tenant_client_packaging.py
}
if ($OpenIndex) {
    $p = Join-Path (Get-Location) "reports/client_tenants/tenant_index.html"
    if (Test-Path $p) { Start-Process $p }
}
