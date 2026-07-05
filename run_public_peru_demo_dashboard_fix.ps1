[CmdletBinding()]
Param(
    [switch]$RunTests,
    [switch]$OpenLanding,
    [switch]$OpenCatalog
)
$ErrorActionPreference = "Stop"
python scripts/131_run_v26_public_demo_dashboard_fix.py
if ($RunTests) {
    pytest -q tests/test_public_peru_demo_and_dashboard_routes.py
}
if ($OpenLanding) {
    Start-Process "reports/client_ready_branding/LANDING_PAGE_CLIENT_DEMO.html"
}
if ($OpenCatalog) {
    Start-Process "reports/generated_dashboards/index.html"
}
