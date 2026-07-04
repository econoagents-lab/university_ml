[CmdletBinding()]
param(
    [switch]$RunTests,
    [switch]$OpenIndex
)
$ErrorActionPreference = "Stop"
python scripts/120_run_v23_client_proposal_and_contract_automation.py
if ($RunTests) { pytest -q tests/test_client_proposal_and_contract_automation.py }
if ($OpenIndex) { Invoke-Item "reports/client_proposals/proposal_index.html" }
