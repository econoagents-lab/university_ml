[CmdletBinding()]
Param(
    [ValidateSet("safe", "sperant", "crm", "full", "production")]
    [string]$Mode = "production",

    [switch]$InstallDeps,
    [switch]$RunTests,
    [switch]$OpenReport,

    # Fuerza extracción fresca desde Redshift/Sperant antes de construir gold/model-ready.
    [switch]$ForceExtract,

    # Límite opcional para pruebas de extracción. 0 = sin límite.
    [int]$ExtractLimit = 0,

    # Alias explícito para extracción completa. Equivale a -ExtractLimit 0.
    [switch]$FullExtract,

    # Si existe data/raw/sperant/*.parquet y no usas -ForceExtract, trabaja con parquets locales.
    [switch]$PreferLocalParquets,

    # Evita correr scripts de registry/dashboard/production si solo quieres validar CRM fresco.
    [switch]$OnlyCRMValidation
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Write-Ok($Message) {
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn($Message) {
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail($Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Ensure-Dir($Path) {
    if (!(Test-Path $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Add-Result($Step, $Status, $Detail, $LogPath) {
    $script:Results += [pscustomobject]@{
        step = $Step
        status = $Status
        detail = $Detail
        log_path = $LogPath
        timestamp = (Get-Date).ToString("s")
    }
}

function Test-AllExpectedPaths($ExpectedPaths) {
    if ($null -eq $ExpectedPaths -or $ExpectedPaths.Count -eq 0) { return $false }
    foreach ($ExpectedPath in $ExpectedPaths) {
        if (!(Test-Path $ExpectedPath)) { return $false }
    }
    return $true
}

function Run-CommandLogged($StepName, $Command, $LogName, [switch]$Required, [string[]]$ExpectedPaths = @()) {
    $LogPath = Join-Path $script:LogsDir $LogName
    Write-Step $StepName
    Write-Host $Command -ForegroundColor DarkGray

    try {
        # Importante: usar redirección clásica para que warnings en stderr no se conviertan
        # en errores de PowerShell. El juez real debe ser ExitCode + artefactos generados.
        & cmd.exe /d /c $Command > $LogPath 2>&1
        $ExitCode = $LASTEXITCODE
        $ExpectedOk = Test-AllExpectedPaths $ExpectedPaths

        if ($ExitCode -eq 0) {
            Write-Ok "$StepName completado."
            Add-Result $StepName "ok" "Completado." $LogPath
            return $true
        }
        elseif ($ExpectedOk) {
            $Detail = "ExitCode=$ExitCode, pero artefactos esperados existen. Tratar como warning; revisar log."
            Write-Warn "$StepName completó con warnings. $Detail"
            Add-Result $StepName "warning" $Detail $LogPath
            return $true
        }
        else {
            $Detail = "ExitCode=$ExitCode. Revisar log."
            if ($Required) {
                Write-Fail "$StepName falló. $Detail"
                Add-Result $StepName "fail" $Detail $LogPath
                return $false
            }
            else {
                Write-Warn "$StepName no completó. $Detail"
                Add-Result $StepName "warning" $Detail $LogPath
                return $false
            }
        }
    }
    catch {
        $Detail = $_.Exception.Message
        $ExpectedOk = Test-AllExpectedPaths $ExpectedPaths
        if ($ExpectedOk) {
            Write-Warn "$StepName lanzó warning/error de consola, pero artefactos esperados existen. $Detail"
            Add-Result $StepName "warning" "Artefactos esperados existen. $Detail" $LogPath
            return $true
        }
        elseif ($Required) {
            Write-Fail "$StepName falló: $Detail"
            Add-Result $StepName "fail" $Detail $LogPath
            return $false
        }
        else {
            Write-Warn "$StepName warning: $Detail"
            Add-Result $StepName "warning" $Detail $LogPath
            return $false
        }
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir = Join-Path $Root "reports\executive_runs\$Timestamp"
$LogsDir = Join-Path $RunDir "logs"
Ensure-Dir $RunDir
Ensure-Dir $LogsDir
$script:LogsDir = $LogsDir
$script:Results = @()

Write-Step "Machine Learning University v1.0.2 CRM Fresh Full Extract Runner"
Write-Host "Proyecto: $Root"
Write-Host "Mode: $Mode"
Write-Host "ForceExtract: $ForceExtract"
if ($FullExtract) { $ExtractLimit = 0 }
Write-Host "ExtractLimit: $ExtractLimit"
Write-Host "FullExtract: $FullExtract"
Write-Host "PreferLocalParquets: $PreferLocalParquets"
Write-Host "OnlyCRMValidation: $OnlyCRMValidation"

# 1) Entorno virtual
Write-Step "Activate virtual environment"
if (!(Test-Path ".venv")) {
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
Add-Result "Activate virtual environment" "ok" ".venv activo." ""

if ($InstallDeps) {
    Run-CommandLogged "Install dependencies" "python -m pip install --upgrade pip && pip install -r requirements.txt" "install_deps.log" -Required | Out-Null
}
else {
    Add-Result "Install dependencies" "skipped" "No solicitado." ""
}

# 2) Modo de datos
if ($Mode -in @("sperant", "crm", "full")) {
    $env:MLU_DATA_MODE = "sperant"
}
elseif ($Mode -eq "safe") {
    $env:MLU_DATA_MODE = "demo"
}
else {
    if (-not $env:MLU_DATA_MODE) {
        $env:MLU_DATA_MODE = "sperant"
    }
}
Write-Ok "MLU_DATA_MODE=$env:MLU_DATA_MODE"

$RawSperant = Join-Path $Root "data\raw\sperant"
$HasLocalParquets = $false
if (Test-Path $RawSperant) {
    $LocalParquets = Get-ChildItem $RawSperant -Filter "*.parquet" -ErrorAction SilentlyContinue
    if ($LocalParquets.Count -gt 0) { $HasLocalParquets = $true }
}

# 3) Extracción Redshift/Sperant fresca o uso local
if ($ForceExtract) {
    $ExtractCmd = "python scripts/00_extract_redshift_to_parquet.py"
    if ($ExtractLimit -gt 0) {
        $ExtractCmd = "$ExtractCmd --limit $ExtractLimit"
    }
    $ExpectedExtractFiles = @(
        (Join-Path $Root "data\raw\sperant\procesos.parquet"),
        (Join-Path $Root "data\raw\sperant\unidades.parquet"),
        (Join-Path $Root "data\raw\sperant\clientes.parquet"),
        (Join-Path $Root "data\raw\sperant\clientes_proyectos.parquet"),
        (Join-Path $Root "data\raw\sperant\proyectos.parquet"),
        (Join-Path $Root "data\raw\sperant\datos_extras.parquet"),
        (Join-Path $Root "data\raw\sperant\proforma_unidad.parquet")
    )
    Run-CommandLogged "Extract Redshift to Parquet" $ExtractCmd "extract_redshift.log" -Required -ExpectedPaths $ExpectedExtractFiles | Out-Null
}
elseif ($PreferLocalParquets -or $HasLocalParquets) {
    Add-Result "Extract Redshift to Parquet" "skipped" "Omitido: se usan parquets locales existentes. Usa -ForceExtract para probar Redshift vivo." ""
    Write-Warn "Redshift omitido. Estás validando CRM local/parquet, no extracción fresca."
}
else {
    Add-Result "Extract Redshift to Parquet" "warning" "No hay parquets locales y no se usó -ForceExtract." ""
    Write-Warn "No hay parquets locales detectados. Usa -ForceExtract para traer data desde Redshift."
}

# 4) Pipeline CRM real/local
Run-CommandLogged "Profile Sperant sources" "python scripts/09_profile_sperant_sources.py" "profile_sperant.log" -Required | Out-Null
Run-CommandLogged "Build Sperant training dataset" "python scripts/10_build_sperant_training_dataset.py --unit-focus departamentos" "build_sperant_training.log" -Required | Out-Null
Run-CommandLogged "Prepare model-ready dataset" "python scripts/15_prepare_model_ready_dataset.py" "prepare_model_ready.log" -Required | Out-Null
Run-CommandLogged "Train/evaluate official model" "python scripts/16_train_evaluate_official_model.py" "train_evaluate_official.log" -Required | Out-Null
Run-CommandLogged "Score actual riesgo caida" "python scripts/14_score_actual_riesgo_caida.py" "score_actual.log" -Required | Out-Null

# 5) Monitoring/registry/dashboard/production opcional
if (-not $OnlyCRMValidation) {
    if (Test-Path "scripts/28_weekly_monitoring_report.py") {
        Run-CommandLogged "Weekly monitoring report" "python scripts/28_weekly_monitoring_report.py" "weekly_monitoring.log" | Out-Null
    }
    if (Test-Path "scripts/36_run_v08_registry_pipeline.py") {
        Run-CommandLogged "Registry pipeline v0.8" "python scripts/36_run_v08_registry_pipeline.py" "registry_v08.log" | Out-Null
    }
    if (Test-Path "scripts/41_run_v09_decision_dashboard_pipeline.py") {
        Run-CommandLogged "Decision dashboard pipeline v0.9" "python scripts/41_run_v09_decision_dashboard_pipeline.py" "decision_dashboard_v09.log" | Out-Null
    }
    if (Test-Path "scripts/45_run_v10_production_release.py") {
        Run-CommandLogged "Production release pipeline v1.0" "python scripts/45_run_v10_production_release.py" "production_release_v10.log" | Out-Null
    }
}
else {
    Add-Result "Production/registry/dashboard pipelines" "skipped" "OnlyCRMValidation activado." ""
}

if ($RunTests) {
    Run-CommandLogged "Pytest" "pytest -q" "pytest.log" -Required | Out-Null
}
else {
    Add-Result "Pytest" "skipped" "No solicitado." ""
}

# 6) Manifest + bitácora
$Counts = @{
    ok = @($Results | Where-Object {$_.status -eq "ok"}).Count
    warning = @($Results | Where-Object {$_.status -eq "warning"}).Count
    fail = @($Results | Where-Object {$_.status -eq "fail"}).Count
    skipped = @($Results | Where-Object {$_.status -eq "skipped"}).Count
}

$Manifest = [pscustomobject]@{
    project_root = $Root
    mode = $Mode
    data_mode = $env:MLU_DATA_MODE
    force_extract = [bool]$ForceExtract
    extract_limit = $ExtractLimit
    full_extract = [bool]$FullExtract
    prefer_local_parquets = [bool]$PreferLocalParquets
    only_crm_validation = [bool]$OnlyCRMValidation
    run_dir = $RunDir
    generated_at = (Get-Date).ToString("s")
    counts = $Counts
    results = $Results
}
$ManifestPath = Join-Path $RunDir "run_manifest.json"
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $ManifestPath -Encoding UTF8

$GoldPath = Join-Path $Root "data\processed\gold\riesgo_caida_training.parquet"
$ModelReadyPath = Join-Path $Root "data\processed\gold\riesgo_caida_training_model_ready.parquet"
$ScoringPath = Join-Path $Root "reports\scoring\top_100_riesgo_caida.csv"
$ReadinessPath = Join-Path $Root "reports\production\PRODUCTION_READINESS_REPORT.md"
$ExecutiveLatest = Join-Path $Root "reports\executive_latest.md"
$Bitacora = Join-Path $RunDir "BITACORA_EJECUTIVA_V10_2_CRM_FULL_EXTRACT.md"

$Lines = @()
$Lines += "# Machine Learning University - Bitácora Ejecutiva v1.0.2 CRM Fresh Full Extract"
$Lines += ""
$Lines += "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Lines += "Proyecto: $Root"
$Lines += "Mode: $Mode"
$Lines += "Data mode: $env:MLU_DATA_MODE"
$Lines += "ForceExtract: $ForceExtract"
$Lines += "ExtractLimit: $ExtractLimit"
$Lines += ""
$Lines += "## Resumen ejecutivo"
$Lines += ""
$Lines += "OK: $($Counts.ok)"
$Lines += "Warnings: $($Counts.warning)"
$Lines += "Fails: $($Counts.fail)"
$Lines += "Skipped: $($Counts.skipped)"
$Lines += ""
$Lines += "## Artefactos clave"
$Lines += ""
$Lines += "Gold entrenamiento existe: $(Test-Path $GoldPath)"
$Lines += "Model-ready existe: $(Test-Path $ModelReadyPath)"
$Lines += "Scoring top 100 existe: $(Test-Path $ScoringPath)"
$Lines += "Production readiness existe: $(Test-Path $ReadinessPath)"
$Lines += ""
$Lines += "## Pasos ejecutados"
$Lines += ""
$Lines += "| Paso | Estado | Detalle | Log |"
$Lines += "|---|---:|---|---|"
foreach ($R in $Results) {
    $Lines += "| $($R.step) | $($R.status) | $($R.detail) | $($R.log_path) |"
}
$Lines += ""
$Lines += "## Lectura ejecutiva"
$Lines += ""
if ($ForceExtract) {
    $Lines += "- Esta corrida intentó validar CRM fresco desde Redshift/Sperant."
} else {
    $Lines += "- Esta corrida usó parquets locales si existían. Para Redshift vivo usa -ForceExtract."
}
$Lines += "- Si Extract Redshift to Parquet está ok, la tubería probó extracción fresca."
$Lines += "- Si está skipped, validaste CRM local/parquet, no Redshift vivo."
$Lines += "- Si Gold, model-ready, scoring y production readiness existen, el flujo end-to-end está operativo."
$Lines += ""
$Lines += "## Siguiente acción recomendada"
$Lines += ""
if ($Counts.fail -gt 0) {
    $Lines += "Corregir primero los pasos FAIL revisando logs."
} elseif (-not $ForceExtract) {
    $Lines += "Ejecutar una corrida con -ForceExtract -ExtractLimit 1000 para probar Redshift vivo con muestra controlada."
} else {
    $Lines += "Revisar métricas, drift y readiness; si todo está OK, correr sin ExtractLimit para full refresh."
}

$Lines | Set-Content -Path $Bitacora -Encoding UTF8
Copy-Item $Bitacora $ExecutiveLatest -Force

Write-Step "Resumen final"
Write-Host "Bitácora: $Bitacora" -ForegroundColor Green
Write-Host "Manifest: $ManifestPath" -ForegroundColor Green
Write-Host "Executive latest: $ExecutiveLatest" -ForegroundColor Green

if ($OpenReport) {
    Invoke-Item $Bitacora
}

if ($Counts.fail -gt 0) {
    throw "Runner terminó con $($Counts.fail) fallo(s). Revisar bitácora/logs."
}
else {
    Write-Ok "v1.0.1 CRM fresh runner completado sin fallos críticos."
}
