[CmdletBinding()]
Param(
    [ValidateSet("crm","demo")][string]$DataMode = "crm",
    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$RunStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir = Join-Path $ProjectRoot "reports\executive_runs\$RunStamp"
$LogDir = Join-Path $RunDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Add-Result($Step, $Status, $Detail) {
    $script:Results += [PSCustomObject]@{ step=$Step; status=$Status; detail=$Detail; timestamp=(Get-Date).ToString("s") }
}
function Run-Step($Name, $Command) {
    $log = Join-Path $LogDir (($Name -replace '[^a-zA-Z0-9]+','_') + ".log")
    try {
        cmd /c "$Command" > $log 2>&1
        if ($LASTEXITCODE -eq 0) { Add-Result $Name "ok" $log }
        else { Add-Result $Name "fail" $log }
    } catch {
        Add-Result $Name "fail" $_.Exception.Message
    }
}

$script:Results = @()
if (Test-Path ".\.venv\Scripts\Activate.ps1") { . ".\.venv\Scripts\Activate.ps1"; Add-Result "Activate virtual environment" "ok" ".venv activo" } else { Add-Result "Activate virtual environment" "warning" "No existe .venv" }
if ($InstallDeps) { Run-Step "Install dependencies" "python -m pip install -r requirements.txt" }
$env:MLU_DATA_MODE = $DataMode

Run-Step "Prepare model-ready dataset" "python scripts/15_prepare_model_ready_dataset.py"
Run-Step "Register dataset version" "python scripts/29_register_dataset_version.py"
Run-Step "Train challenger models" "python scripts/30_train_challenger_models.py"
Run-Step "Compare champion vs challengers" "python scripts/31_compare_champion_vs_challengers.py"
Run-Step "Promote champion model" "python scripts/32_promote_champion_model.py"
Run-Step "Retraining policy check" "python scripts/33_retraining_policy_check.py"
Run-Step "Generate congress figures" "python scripts/34_generate_congress_figures.py"
Run-Step "Build registry metadata" "python scripts/35_build_registry_metadata.py"
if ($RunTests) { Run-Step "Pytest" "python -m pytest -q" }

$ok = ($Results | Where-Object {$_.status -eq "ok"}).Count
$fail = ($Results | Where-Object {$_.status -eq "fail"}).Count
$warn = ($Results | Where-Object {$_.status -eq "warning"}).Count
$report = Join-Path $RunDir "BITACORA_V8_RETRAINING_REGISTRY.md"
$md = "# Bitacora Ejecutiva v0.8 - Retraining Registry`n`n"
$md += "Fecha: $(Get-Date -Format s)`n"
$md += "Data mode: $DataMode`n`n"
$md += "## Resumen`n`nOK: $ok`nWarnings: $warn`nFails: $fail`n`n"
$md += "## Pasos`n`n| Paso | Estado | Detalle |`n|---|---:|---|`n"
foreach ($r in $Results) { $md += "| $($r.step) | $($r.status) | $($r.detail) |`n" }
$md += "`n## Artefactos clave`n`n"
$md += "- reports/registry/model_registry_metadata.md`n"
$md += "- reports/registry/champion_vs_challenger_report.md`n"
$md += "- reports/registry/retraining_decision_report.md`n"
$md += "- reports/congress/CONGRESS_FIGURE_PACK.md`n"
$md += "- reports/figures/congress/*.png y *.svg`n"
Set-Content -Path $report -Value $md -Encoding UTF8
Copy-Item $report "reports\executive_latest_v8.md" -Force
$Results | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $RunDir "run_manifest_v8.json") -Encoding UTF8
if ($OpenReport) { Invoke-Item $report }
Write-Host "Bitacora generada: $report"
