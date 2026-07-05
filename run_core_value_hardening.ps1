[CmdletBinding()]
Param(
    [switch]$RunTests,
    [switch]$OpenBrief
)
$ErrorActionPreference = "Stop"
Write-Host "[v2.7] Core Value Hardening" -ForegroundColor Cyan
python scripts/136_run_v27_core_value_hardening.py
if ($RunTests) {
    pytest -q tests/test_core_value_hardening.py
}
if ($OpenBrief) {
    Start-Process "reports\core_value_hardening\EXECUTIVE_VALUE_BRIEF.html"
}
