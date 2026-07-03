[CmdletBinding()]
param(
    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "[INFO] Yo ejecuto el pack final UNI RAG económico." -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . ".\.venv\Scripts\Activate.ps1"
    Write-Host "[OK] Yo activé el entorno virtual." -ForegroundColor Green
}

if ($InstallDeps) {
    python -m pip install -r requirements.txt
}

python scripts/51_run_v11_uni_final_rag_pack.py

if ($RunTests) {
    pytest -q
}

if ($OpenReport) {
    Start-Process "reports\uni_final\RAGAS_LIKE_SUMMARY.md"
}

Write-Host "[OK] Yo terminé el pipeline UNI final." -ForegroundColor Green
