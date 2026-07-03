[CmdletBinding()]
Param(
    [ValidateSet("safe", "sperant", "full")]
    [string]$Mode = "sperant",
    [switch]$RunTests,
    [switch]$OpenReport
)

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir = Join-Path $ProjectRoot "reports\executive_runs\$Timestamp"
$LogDir = Join-Path $RunDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Results = New-Object System.Collections.Generic.List[object]

function Add-Result($Step, $Status, $Detail, $LogPath="") {
    $Results.Add([PSCustomObject]@{ step=$Step; status=$Status; detail=$Detail; log_path=$LogPath; timestamp=(Get-Date).ToString("s") }) | Out-Null
    $Color = if ($Status -eq "ok") {"Green"} elseif ($Status -eq "warning") {"Yellow"} elseif ($Status -eq "skipped") {"Cyan"} else {"Red"}
    Write-Host "[$($Status.ToUpper())] $Step - $Detail" -ForegroundColor $Color
}

function Run-Step($Step, $Command, $LogName) {
    $LogPath = Join-Path $LogDir $LogName
    Write-Host "[INFO] Running step: $Step" -ForegroundColor Cyan
    try {
        cmd /c "$Command" *> $LogPath
        if ($LASTEXITCODE -eq 0) { Add-Result $Step "ok" "Completado." $LogPath }
        else { Add-Result $Step "fail" "Exit code $LASTEXITCODE. Revisar log." $LogPath }
    } catch {
        Add-Result $Step "fail" $_.Exception.Message $LogPath
    }
}

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . ".\.venv\Scripts\Activate.ps1"
    Add-Result "Activate virtual environment" "ok" ".venv activo."
} else {
    Add-Result "Activate virtual environment" "warning" "No existe .venv. Ejecuta python -m venv .venv."
}

Run-Step "Prepare model-ready dataset" "python scripts\15_prepare_model_ready_dataset.py" "prepare_model_ready.log"
Run-Step "Train/evaluate official model" "python scripts\16_train_evaluate_official_model.py" "train_evaluate_official.log"
Run-Step "Score current risk" "python scripts\14_score_actual_riesgo_caida.py" "score_actual.log"
Run-Step "Evaluate lift deciles" "python scripts\17_evaluate_lift_deciles.py" "lift_deciles.log"
Run-Step "Initialize feedback loop" "python scripts\18_initialize_feedback_loop.py" "feedback_init.log"
Run-Step "Merge feedback outcomes" "python scripts\19_merge_feedback_outcomes.py" "feedback_merge.log"
Run-Step "Generate CEO brief" "python scripts\20_generate_executive_lift_report.py" "ceo_brief.log"

if ($RunTests) {
    Run-Step "Pytest" "python -m pytest" "pytest.log"
}

$Ok = ($Results | Where-Object {$_.status -eq "ok"}).Count
$Warn = ($Results | Where-Object {$_.status -eq "warning"}).Count
$Fail = ($Results | Where-Object {$_.status -eq "fail"}).Count
$Skipped = ($Results | Where-Object {$_.status -eq "skipped"}).Count

$Manifest = [PSCustomObject]@{
    project_root=$ProjectRoot
    mode=$Mode
    generated_at=(Get-Date).ToString("s")
    counts=[PSCustomObject]@{ok=$Ok; warning=$Warn; fail=$Fail; skipped=$Skipped}
    results=$Results
}
$ManifestPath = Join-Path $RunDir "run_manifest.json"
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $ManifestPath -Encoding UTF8

$ReportPath = Join-Path $RunDir "BITACORA_EJECUTIVA.md"
$Lines = @()
$Lines += "# Machine Learning University - Bitacora Ejecutiva v0.6"
$Lines += ""
$Lines += "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Lines += "Proyecto: $ProjectRoot"
$Lines += "Modo: $Mode"
$Lines += ""
$Lines += "## Resumen ejecutivo"
$Lines += ""
$Lines += "OK: $Ok"
$Lines += "Warnings: $Warn"
$Lines += "Fails: $Fail"
$Lines += "Skipped: $Skipped"
$Lines += ""
$Lines += "## Artefactos v0.6"
$Lines += ""
$Lines += "- Lift deciles: $(Test-Path 'reports/modeling/lift_deciles.csv')"
$Lines += "- Feedback template: $(Test-Path 'data/feedback/feedback_log_template.csv')"
$Lines += "- CEO brief: $(Test-Path 'reports/executive/CEO_BRIEF_RIESGO_CAIDA_V0_6.md')"
$Lines += "- Ranking riesgo: $(Test-Path 'data/processed/scoring/ranking_operaciones_riesgo_caida.csv')"
$Lines += ""
$Lines += "## Pasos ejecutados"
$Lines += ""
$Lines += "| Paso | Estado | Detalle | Log |"
$Lines += "|---|---:|---|---|"
foreach ($R in $Results) { $Lines += "| $($R.step) | $($R.status) | $($R.detail) | $($R.log_path) |" }
$Lines += ""
$Lines += "## Siguiente accion recomendada"
$Lines += ""
$Lines += "Usar el top de riesgo diariamente, completar feedback_log.csv y medir resultados a 7/30 dias."
$Lines | Set-Content -Path $ReportPath -Encoding UTF8
Copy-Item $ReportPath (Join-Path $ProjectRoot "reports\executive_latest.md") -Force
Write-Host "[OK] Bitacora generada: $ReportPath" -ForegroundColor Green
if ($OpenReport) { Invoke-Item $ReportPath }
if ($Fail -gt 0) { exit 1 } else { exit 0 }
