[CmdletBinding()]
Param(
    [ValidateSet("safe","sperant","full")]
    [string]$Mode = "sperant",
    [switch]$InstallDeps,
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
$Results = @()
function Add-Result($Step,$Status,$Detail,$LogPath="") {
  $script:Results += [pscustomobject]@{step=$Step;status=$Status;detail=$Detail;log_path=$LogPath;timestamp=(Get-Date).ToString("s")}
  $color = @{ok="Green";warning="Yellow";fail="Red";skipped="Gray"}[$Status]
  Write-Host "[$($Status.ToUpper())] $Step - $Detail" -ForegroundColor $color
}
function Run-Step($Step,$Command,$LogName) {
  $LogPath = Join-Path $LogDir $LogName
  Write-Host "[INFO] Running: $Step" -ForegroundColor Cyan
  cmd /c "$Command" *> $LogPath
  if ($LASTEXITCODE -eq 0) { Add-Result $Step "ok" "Completado." $LogPath } else { Add-Result $Step "fail" "Falló. Revisar log." $LogPath }
}
if (Test-Path ".\.venv\Scripts\Activate.ps1") { . .\.venv\Scripts\Activate.ps1; Add-Result "Activate virtual environment" "ok" ".venv activo." } else { Add-Result "Activate virtual environment" "warning" "No existe .venv." }
if ($InstallDeps) { Run-Step "Install dependencies" "python -m pip install -r requirements.txt" "install_deps.log" }
Run-Step "Prepare model-ready dataset" "python scripts/15_prepare_model_ready_dataset.py" "prepare_model_ready.log"
Run-Step "Train and evaluate official model" "python scripts/16_train_evaluate_official_model.py" "train_evaluate_official.log"
Run-Step "Score current riesgo caida" "python scripts/14_score_actual_riesgo_caida.py" "score_actual.log"
Run-Step "Validate foundations" "python scripts/12_validate_foundations.py" "validate_foundations.log"
if ($RunTests) { Run-Step "Pytest" "python -m pytest" "pytest.log" }
$ManifestPath = Join-Path $ProjectRoot "models\model_manifest.json"
$MetricText = "Sin metricas disponibles."
if (Test-Path $ManifestPath) {
  $m = Get-Content $ManifestPath -Raw | ConvertFrom-Json
  $MetricText = "ROC AUC: $([math]::Round($m.roc_auc,3))`nRecall: $([math]::Round($m.recall,3))`nPrecision: $([math]::Round($m.precision,3))`nF1: $([math]::Round($m.f1,3))`nThreshold: $($m.recommended_threshold)"
}
$Ok = ($Results | Where-Object {$_.status -eq "ok"}).Count
$Fail = ($Results | Where-Object {$_.status -eq "fail"}).Count
$Warn = ($Results | Where-Object {$_.status -eq "warning"}).Count
$Md = @()
$Md += "# Machine Learning University - Bitacora Ejecutiva v0.5 Official Rules"
$Md += ""
$Md += "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Md += "Proyecto: $ProjectRoot"
$Md += "Modo: $Mode"
$Md += ""
$Md += "## Resumen ejecutivo"
$Md += "OK: $Ok"
$Md += "Warnings: $Warn"
$Md += "Fails: $Fail"
$Md += ""
$Md += "## Metricas del modelo"
$Md += $MetricText
$Md += ""
$Md += "## Artefactos clave"
$Md += "- Model-ready: data/processed/gold/riesgo_caida_training_model_ready.parquet"
$Md += "- Evaluation report: reports/modeling/evaluation_report.md"
$Md += "- Model card: models/model_card.md"
$Md += "- Ranking scoring: data/processed/scoring/ranking_operaciones_riesgo_caida.csv"
$Md += ""
$Md += "## Pasos ejecutados"
$Md += "| Paso | Estado | Detalle | Log |"
$Md += "|---|---:|---|---|"
foreach ($r in $Results) { $Md += "| $($r.step) | $($r.status) | $($r.detail) | $($r.log_path) |" }
$ReportPath = Join-Path $RunDir "BITACORA_EJECUTIVA_V0_5.md"
$LatestPath = Join-Path $ProjectRoot "reports\executive_latest.md"
$Md -join "`n" | Set-Content -Path $ReportPath -Encoding UTF8
$Md -join "`n" | Set-Content -Path $LatestPath -Encoding UTF8
$RunManifest = [pscustomobject]@{project_root=$ProjectRoot;mode=$Mode;generated_at=(Get-Date).ToString("s");counts=@{ok=$Ok;warning=$Warn;fail=$Fail};results=$Results}
$RunManifest | ConvertTo-Json -Depth 8 | Set-Content -Path (Join-Path $RunDir "run_manifest_v0_5.json") -Encoding UTF8
Write-Host "[OK] Bitacora generada: $ReportPath" -ForegroundColor Green
if ($OpenReport) { Invoke-Item $ReportPath }
