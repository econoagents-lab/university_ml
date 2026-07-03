<#
Machine Learning University - Executive Bitacora v4 RESCUE
Objetivo: ejecutar lo posible, priorizar parquets locales, rescatar entrenamiento si el builder oficial falla,
y generar una bitacora ejecutiva sin romperse por warnings de stderr.

Uso recomendado:
  .\run_executive_reporting_bitacora_v4_rescue.ps1 -Mode safe -InstallDeps -OpenReport
  .\run_executive_reporting_bitacora_v4_rescue.ps1 -Mode sperant -PreferLocalParquets -OpenReport
  .\run_executive_reporting_bitacora_v4_rescue.ps1 -Mode sperant -ForceExtract -ExtractLimit 1000 -OpenReport
#>

[CmdletBinding()]
Param(
    [ValidateSet("safe", "sperant", "full")]
    [string]$Mode = "safe",

    [switch]$InstallDeps,
    [switch]$OpenReport,
    [switch]$PreferLocalParquets,
    [switch]$ForceExtract,
    [int]$ExtractLimit = 0,
    [switch]$RunTests,
    [switch]$NoRescue
)

$ErrorActionPreference = "Continue"

function Write-Info { Param([string]$Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Ok   { Param([string]$Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Warn { Param([string]$Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Fail { Param([string]$Message) Write-Host "[FAIL] $Message" -ForegroundColor Red }

function New-DirectoryIfMissing {
    Param([string]$Path)
    if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}

function Add-Result {
    Param(
        [string]$Step,
        [string]$Status,
        [string]$Detail,
        [string]$LogPath = ""
    )
    $script:Results += [PSCustomObject]@{
        step = $Step
        status = $Status
        detail = $Detail
        log_path = $LogPath
        timestamp = (Get-Date).ToString("s")
    }
}

function Invoke-LoggedCommand {
    Param(
        [string]$Step,
        [string]$Command,
        [string]$LogFile,
        [switch]$AllowWarnings
    )

    Write-Info "Running step: $Step"
    $start = Get-Date
    $output = @()
    $exitCode = 0

    try {
        $output = Invoke-Expression "$Command 2>&1"
        $exitCode = if ($LASTEXITCODE -ne $null) { [int]$LASTEXITCODE } else { 0 }
    }
    catch {
        $output += $_.Exception.ToString()
        $exitCode = 1
    }

    $duration = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
    $text = @()
    $text += "STEP: $Step"
    $text += "COMMAND: $Command"
    $text += "EXIT_CODE: $exitCode"
    $text += "DURATION_SECONDS: $duration"
    $text += "--- OUTPUT ---"
    $text += ($output | ForEach-Object { $_.ToString() })
    $text | Set-Content -Path $LogFile -Encoding UTF8

    $joined = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    if ($exitCode -eq 0) {
        if ($joined -match "UserWarning|FutureWarning|DeprecationWarning") {
            Write-Warn "$Step completed with warnings."
            Add-Result $Step "warning" "Completado con warnings. Revisar log." $LogFile
        }
        else {
            Write-Ok $Step
            Add-Result $Step "ok" "Completado." $LogFile
        }
        return $true
    }
    else {
        Write-Fail "$Step failed. Exit code: $exitCode"
        $brief = ($joined -split "`n" | Select-Object -Last 8) -join " | "
        Add-Result $Step "fail" $brief $LogFile
        return $false
    }
}

function Test-AnyParquetInSperantRaw {
    $rawDir = Join-Path $ProjectRoot "data\raw\sperant"
    if (-not (Test-Path $rawDir)) { return $false }
    $files = Get-ChildItem -Path $rawDir -Filter "*.parquet" -ErrorAction SilentlyContinue
    return ($files.Count -gt 0)
}

function Get-ProcessesParquetPath {
    $candidates = @(
        (Join-Path $ProjectRoot "data\raw\sperant\procesos.parquet"),
        (Join-Path $ProjectRoot "data\raw\procesos.parquet"),
        (Join-Path $ProjectRoot "procesos.parquet"),
        (Join-Path $ProjectRoot "data\sample\procesos.parquet")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return ""
}

function Normalize-LocalParquets {
    $rawSperant = Join-Path $ProjectRoot "data\raw\sperant"
    New-DirectoryIfMissing $rawSperant

    $knownTables = @(
        "procesos", "unidades", "clientes", "proyectos", "datos_extras", "clientes_proyectos",
        "fact_leads", "fact_leads_enriched", "fact_conversion_leads", "fact_separaciones",
        "fact_firmas_minutas", "fact_caidas", "fact_separacion_cuota_inicial"
    )

    $copied = @()
    foreach ($table in $knownTables) {
        $target = Join-Path $rawSperant "$table.parquet"
        if (Test-Path $target) { continue }

        $sources = @(
            (Join-Path $ProjectRoot "$table.parquet"),
            (Join-Path $ProjectRoot "data\raw\$table.parquet"),
            (Join-Path $ProjectRoot "data\sample\$table.parquet")
        )

        foreach ($source in $sources) {
            if (Test-Path $source) {
                Copy-Item $source $target -Force
                $copied += "$table.parquet"
                break
            }
        }
    }

    if ($copied.Count -gt 0) {
        Write-Ok "Parquets locales normalizados: $($copied -join ', ')"
        Add-Result "Normalize local parquets" "ok" "Copiados a data/raw/sperant: $($copied -join ', ')" ""
    }
    else {
        Write-Warn "No se copiaron parquets locales nuevos."
        Add-Result "Normalize local parquets" "warning" "No se encontraron parquets locales nuevos para copiar." ""
    }
}

function Copy-InferredGoldToOfficialIfNeeded {
    $official = Join-Path $ProjectRoot "data\processed\gold\riesgo_caida_training.parquet"
    $inferred = Join-Path $ProjectRoot "data\processed\gold\riesgo_caida_training_inferred.parquet"
    if ((-not (Test-Path $official)) -and (Test-Path $inferred) -and (-not $NoRescue)) {
        Copy-Item $inferred $official -Force
        Write-Warn "Rescue activo: se copió riesgo_caida_training_inferred.parquet como riesgo_caida_training.parquet. Marcar como DRAFT."
        Add-Result "Rescue inferred gold" "warning" "Se usó gold inferred para desbloquear entrenamiento. Debe revisarse antes de uso ejecutivo." ""
        return $true
    }
    return $false
}

function Write-ExecutiveReport {
    $reportPath = Join-Path $RunDir "BITACORA_EJECUTIVA.md"
    $latestPath = Join-Path $ProjectRoot "reports\executive_latest.md"
    $manifestPath = Join-Path $RunDir "run_manifest.json"

    $okCount = ($Results | Where-Object { $_.status -eq "ok" }).Count
    $warnCount = ($Results | Where-Object { $_.status -eq "warning" }).Count
    $failCount = ($Results | Where-Object { $_.status -eq "fail" }).Count
    $skipCount = ($Results | Where-Object { $_.status -eq "skipped" }).Count

    $md = @()
    $md += "# Machine Learning University - Bitacora Ejecutiva"
    $md += ""
    $md += "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $md += "Proyecto: $ProjectRoot"
    $md += "Modo: $Mode"
    $md += ""
    $md += "## Resumen ejecutivo"
    $md += ""
    $md += "OK: $okCount"
    $md += "Warnings: $warnCount"
    $md += "Fails: $failCount"
    $md += "Skipped: $skipCount"
    $md += ""
    $md += "## Diagnostico"
    $md += ""

    if ($failCount -eq 0) {
        $md += "Estado general: operativo con o sin advertencias."
    }
    else {
        $md += "Estado general: hay bloqueadores. Revisar los logs asociados a los pasos fallidos."
    }

    $officialGold = Join-Path $ProjectRoot "data\processed\gold\riesgo_caida_training.parquet"
    $inferredGold = Join-Path $ProjectRoot "data\processed\gold\riesgo_caida_training_inferred.parquet"
    $modelPath = Join-Path $ProjectRoot "models\riesgo_caida_model.joblib"

    $md += ""
    $md += "## Artefactos clave"
    $md += ""
    $md += "Gold oficial entrenamiento: $(if (Test-Path $officialGold) { 'existe' } else { 'no existe' })"
    $md += "Gold inferred entrenamiento: $(if (Test-Path $inferredGold) { 'existe' } else { 'no existe' })"
    $md += "Modelo riesgo caida: $(if (Test-Path $modelPath) { 'existe' } else { 'no existe' })"
    $md += ""
    $md += "## Pasos ejecutados"
    $md += ""
    $md += "| Paso | Estado | Detalle | Log |"
    $md += "|---|---:|---|---|"
    foreach ($r in $Results) {
        $safeDetail = ($r.detail -replace "\|", "/")
        $logCell = if ($r.log_path) { $r.log_path } else { "" }
        $md += "| $($r.step) | $($r.status) | $safeDetail | $logCell |"
    }

    $md += ""
    $md += "## Lectura ejecutiva"
    $md += ""
    $md += "1. Si existe gold oficial, el sistema puede entrenar con dataset estandar."
    $md += "2. Si solo existe gold inferred, el sistema puede entrenar como borrador, pero requiere congelar reglas oficiales."
    $md += "3. Si Redshift falla pero hay parquets locales, se recomienda seguir con modo local y corregir extractor despues."
    $md += "4. Si hay warnings de pandas/redshift_connector, no necesariamente bloquean; revisar exit code y archivos generados."
    $md += ""
    $md += "## Siguiente accion recomendada"
    $md += ""
    if (-not (Test-Path $officialGold) -and -not (Test-Path $inferredGold)) {
        $md += "Copiar procesos.parquet y unidades.parquet a data/raw/sperant o ejecutar extractor Redshift con ForceExtract."
    }
    elseif (Test-Path $inferredGold) {
        $md += "Revisar reglas inferidas, congelarlas como oficiales y reentrenar."
    }
    else {
        $md += "Entrenar modelo, revisar metricas y publicar API local."
    }

    $md | Set-Content -Path $reportPath -Encoding UTF8
    Copy-Item $reportPath $latestPath -Force

    $manifest = [PSCustomObject]@{
        project_root = $ProjectRoot
        mode = $Mode
        run_dir = $RunDir
        generated_at = (Get-Date).ToString("s")
        counts = [PSCustomObject]@{ ok = $okCount; warning = $warnCount; fail = $failCount; skipped = $skipCount }
        results = $Results
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8

    Write-Ok "Bitacora generada: $reportPath"
    Write-Ok "Latest report: $latestPath"
    Write-Ok "Manifest: $manifestPath"

    if ($OpenReport) { Start-Process $reportPath }
}

# Main
$script:ProjectRoot = (Get-Location).Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$script:RunDir = Join-Path $ProjectRoot "reports\executive_runs\$timestamp"
$logDir = Join-Path $RunDir "logs"
New-DirectoryIfMissing $RunDir
New-DirectoryIfMissing $logDir
New-DirectoryIfMissing (Join-Path $ProjectRoot "reports")
$script:Results = @()

Write-Info "Machine Learning University - Executive Bitacora v4 RESCUE"
Write-Info "Project root: $ProjectRoot"
Write-Info "Mode: $Mode"

# Virtual environment
$venvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    try {
        . $venvActivate
        Write-Ok "Virtual environment activated."
        Add-Result "Activate virtual environment" "ok" ".venv activo." ""
    }
    catch {
        Write-Fail "No se pudo activar .venv: $($_.Exception.Message)"
        Add-Result "Activate virtual environment" "fail" $_.Exception.Message ""
    }
}
else {
    Write-Warn "No existe .venv. Se usara python del sistema."
    Add-Result "Activate virtual environment" "warning" "No existe .venv." ""
}

if ($InstallDeps -and (Test-Path (Join-Path $ProjectRoot "requirements.txt"))) {
    Invoke-LoggedCommand "Install dependencies" "python -m pip install -r requirements.txt" (Join-Path $logDir "install_dependencies.log") | Out-Null
}

# Normalize local parquets early
if ($Mode -in @("sperant", "full") -or $PreferLocalParquets) {
    Normalize-LocalParquets
}

# Redshift extraction: only if forced or no parquets available.
$extractScript = Join-Path $ProjectRoot "scripts\00_extract_redshift_to_parquet.py"
$hasRawParquets = Test-AnyParquetInSperantRaw
if (($Mode -in @("sperant", "full")) -and (Test-Path $extractScript)) {
    if ($ForceExtract -or (-not $hasRawParquets)) {
        $extractCmd = "python scripts/00_extract_redshift_to_parquet.py"
        if ($ExtractLimit -gt 0) { $extractCmd = "$extractCmd --limit $ExtractLimit" }
        Invoke-LoggedCommand "Extract Redshift to Parquet" $extractCmd (Join-Path $logDir "extract_redshift.log") -AllowWarnings | Out-Null
    }
    else {
        Write-Warn "Extractor omitido: ya existen parquets locales en data/raw/sperant. Usa -ForceExtract para refrescar desde Redshift."
        Add-Result "Extract Redshift to Parquet" "skipped" "Omitido por parquets locales existentes." ""
    }
}

# Profile Sperant sources
$profileScript = Join-Path $ProjectRoot "scripts\09_profile_sperant_sources.py"
if (($Mode -in @("sperant", "full")) -and (Test-Path $profileScript)) {
    Invoke-LoggedCommand "Profile Sperant sources" "python scripts/09_profile_sperant_sources.py" (Join-Path $logDir "profile_sperant.log") | Out-Null
}

# Build official Sperant training dataset first, but do not block inferred build.
$buildOfficialScript = Join-Path $ProjectRoot "scripts\10_build_sperant_training_dataset.py"
if (($Mode -in @("sperant", "full")) -and (Test-Path $buildOfficialScript)) {
    if (Get-ProcessesParquetPath) {
        Invoke-LoggedCommand "Build Sperant training dataset" "python scripts/10_build_sperant_training_dataset.py --unit-focus departamentos" (Join-Path $logDir "build_sperant_training.log") | Out-Null
    }
    else {
        Write-Warn "Build oficial omitido: falta procesos.parquet."
        Add-Result "Build Sperant training dataset" "skipped" "Falta procesos.parquet." ""
    }
}

# Build inferred rules gold table as fallback/rescue.
$buildInferredScript = Join-Path $ProjectRoot "scripts\13_build_from_inferred_rules.py"
if (($Mode -in @("sperant", "full")) -and (Test-Path $buildInferredScript)) {
    if (Get-ProcessesParquetPath) {
        Invoke-LoggedCommand "Build inferred rules gold table" "python scripts/13_build_from_inferred_rules.py" (Join-Path $logDir "build_inferred_rules.log") | Out-Null
    }
    else {
        Write-Warn "Build inferred omitido: falta procesos.parquet."
        Add-Result "Build inferred rules gold table" "skipped" "Falta procesos.parquet." ""
    }
}

Copy-InferredGoldToOfficialIfNeeded | Out-Null

# Validate foundations
$validateScript = Join-Path $ProjectRoot "scripts\12_validate_foundations.py"
if (Test-Path $validateScript) {
    Invoke-LoggedCommand "Validate foundations" "python scripts/12_validate_foundations.py" (Join-Path $logDir "validate_foundations.log") | Out-Null
}

# Train model
$trainScript = Join-Path $ProjectRoot "scripts\11_train_from_sperant.py"
$officialGoldPath = Join-Path $ProjectRoot "data\processed\gold\riesgo_caida_training.parquet"
if (($Mode -in @("sperant", "full")) -and (Test-Path $trainScript)) {
    if (Test-Path $officialGoldPath) {
        Invoke-LoggedCommand "Train from Sperant" "`$env:MLU_DATA_MODE='sperant'; python scripts/11_train_from_sperant.py" (Join-Path $logDir "train_from_sperant.log") | Out-Null
    }
    else {
        Write-Warn "Train omitido: no existe data/processed/gold/riesgo_caida_training.parquet."
        Add-Result "Train from Sperant" "skipped" "Falta gold oficial de entrenamiento." ""
    }
}

# Tests
if ($RunTests -or $Mode -eq "full") {
    Invoke-LoggedCommand "Pytest" "pytest" (Join-Path $logDir "pytest.log") | Out-Null
}

Write-ExecutiveReport
