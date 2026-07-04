[CmdletBinding()]
Param(
  [switch]$RunTests,
  [switch]$OpenIndex
)

$ErrorActionPreference = "Stop"
Write-Host "[v2.4] Contract to Signature and Invoice Ops" -ForegroundColor Cyan
python scripts/124_run_v24_contract_to_signature_and_invoice_ops.py

if ($RunTests) {
  pytest -q tests/test_contract_to_signature_and_invoice_ops.py
}

if ($OpenIndex) {
  $index = Join-Path (Get-Location) "reports\contract_ops\contract_ops_index.html"
  if (Test-Path $index) { Start-Process $index }
}
