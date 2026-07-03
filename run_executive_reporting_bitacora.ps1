<#
Machine Learning University - Executive Reporting / Bitacora v3 SAFE
Compatible with Windows PowerShell 5.1+

Purpose:
- Run what is available in the project without breaking the whole execution.
- Generate an executive Markdown report and JSON manifest.
- Avoid Markdown bold syntax in script strings to prevent parser issues seen with ** tokens.

Usage:
  .\run_executive_reporting_bitacora_v3_safe.ps1 -Mode safe -InstallDeps -OpenReport
  .\run_executive_reporting_bitacora_v3_safe.ps1 -Mode sperant -ExtractLimit 1000 -OpenReport
  .\run_executive_reporting_bitacora_v3_safe.ps1 -Mode full -ExtractLimit 1000 -RunTests -OpenReport
#>

[CmdletBinding()]
Param(
    [ValidateSet('safe','sperant','full')]
    [string]$Mode = 'safe',

    [switch]$InstallDeps,

    [int]$ExtractLimit = 0,

    [switch]$RunTests,

    [switch]$OpenReport
)

$ErrorActionPreference = 'Stop'

function Write-Info {
    Param([string]$Message)
    Write-Host ('[INFO] ' + $Message) -ForegroundColor Cyan
}

function Write-Ok {
    Param([string]$Message)
    Write-Host ('[OK] ' + $Message) -ForegroundColor Green
}

function Write-Warn2 {
    Param([string]$Message)
    Write-Host ('[WARN] ' + $Message) -ForegroundColor Yellow
}

function Write-Fail {
    Param([string]$Message)
    Write-Host ('[FAIL] ' + $Message) -ForegroundColor Red
}

function Ensure-Dir {
    Param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function ConvertTo-JsonSafe {
    Param($Object)
    try {
        return ($Object | ConvertTo-Json -Depth 12)
    }
    catch {
        return '{"json_error":"ConvertTo-Json failed"}'
    }
}

function Get-FileCountSafe {
    Param([string]$Path, [string]$Filter)
    if (-not (Test-Path $Path)) { return 0 }
    try {
        return @(Get-ChildItem -Path $Path -Filter $Filter -Recurse -File -ErrorAction SilentlyContinue).Count
    }
    catch {
        return 0
    }
}

function Get-DirSizeMbSafe {
    Param([string]$Path)
    if (-not (Test-Path $Path)) { return 0 }
    try {
        $sum = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $sum) { return 0 }
        return [math]::Round(($sum / 1MB), 2)
    }
    catch {
        return 0
    }
}

function Invoke-Step {
    Param(
        [string]$Name,
        [string]$Command,
        [string]$LogFile,
        [switch]$Critical
    )

    $started = Get-Date
    Write-Info ('Running step: ' + $Name)

    $result = [ordered]@{
        name = $Name
        command = $Command
        status = 'pending'
        exit_code = $null
        started_at = $started.ToString('s')
        finished_at = $null
        duration_seconds = $null
        log_file = $LogFile
        critical = [bool]$Critical
        error = $null
    }

    try {
        if ($Command.Trim().Length -eq 0) {
            throw 'Empty command.'
        }

        $cmdToRun = $Command + ' *> "' + $LogFile + '"'
        Invoke-Expression $cmdToRun
        $exit = $LASTEXITCODE
        if ($null -eq $exit) { $exit = 0 }

        $result.exit_code = $exit
        if ($exit -eq 0) {
            $result.status = 'success'
            Write-Ok $Name
        }
        else {
            $result.status = 'failed'
            $result.error = 'Non-zero exit code.'
            Write-Fail ($Name + ' exit code: ' + $exit)
            if ($Critical) { throw ($Name + ' failed.') }
        }
    }
    catch {
        $result.status = 'failed'
        $result.error = $_.Exception.Message
        Write-Fail ($Name + ': ' + $_.Exception.Message)
        if ($Critical) { throw }
    }
    finally {
        $finished = Get-Date
        $result.finished_at = $finished.ToString('s')
        $result.duration_seconds = [math]::Round(($finished - $started).TotalSeconds, 2)
    }

    return $result
}

function Test-CommandExists {
    Param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    return ($null -ne $cmd)
}

# Root paths
$ProjectRoot = (Get-Location).Path
$Timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ReportsRoot = Join-Path $ProjectRoot 'reports'
$ExecutiveRoot = Join-Path $ReportsRoot 'executive_runs'
$RunRoot = Join-Path $ExecutiveRoot $Timestamp
$LogsRoot = Join-Path $RunRoot 'logs'
$ArtifactsRoot = Join-Path $RunRoot 'artifacts'

Ensure-Dir $ReportsRoot
Ensure-Dir $ExecutiveRoot
Ensure-Dir $RunRoot
Ensure-Dir $LogsRoot
Ensure-Dir $ArtifactsRoot

$Steps = New-Object System.Collections.ArrayList
$Warnings = New-Object System.Collections.ArrayList
$Recommendations = New-Object System.Collections.ArrayList

Write-Info 'Machine Learning University - Executive Bitacora v3'
Write-Info ('Project root: ' + $ProjectRoot)
Write-Info ('Mode: ' + $Mode)

# Preflight
$pythonExists = Test-CommandExists 'python'
$pipExists = Test-CommandExists 'pip'
$pytestExists = Test-CommandExists 'pytest'

if (-not $pythonExists) { [void]$Warnings.Add('Python was not found in PATH.') }
if (-not $pipExists) { [void]$Warnings.Add('pip was not found in PATH.') }

# Virtual environment
$VenvActivate = Join-Path $ProjectRoot '.venv\Scripts\Activate.ps1'
if (-not (Test-Path $VenvActivate)) {
    if ($pythonExists) {
        [void]$Steps.Add((Invoke-Step -Name 'Create virtual environment' -Command 'python -m venv .venv' -LogFile (Join-Path $LogsRoot '01_create_venv.log')))
    }
    else {
        [void]$Warnings.Add('Cannot create .venv because Python is missing.')
    }
}

if (Test-Path $VenvActivate) {
    try {
        . $VenvActivate
        Write-Ok 'Virtual environment activated.'
    }
    catch {
        [void]$Warnings.Add('Virtual environment exists but could not be activated: ' + $_.Exception.Message)
    }
}
else {
    [void]$Warnings.Add('Virtual environment is not available.')
}

# Install dependencies
if ($InstallDeps) {
    if (Test-Path (Join-Path $ProjectRoot 'requirements.txt')) {
        [void]$Steps.Add((Invoke-Step -Name 'Install requirements' -Command 'python -m pip install -r requirements.txt' -LogFile (Join-Path $LogsRoot '02_install_requirements.log')))
    }
    else {
        [void]$Warnings.Add('requirements.txt not found; dependencies were not installed.')
    }
}

# Step execution map
function Run-PythonScriptIfExists {
    Param(
        [string]$StepName,
        [string]$ScriptRelativePath,
        [string]$Args,
        [string]$LogName
    )
    $scriptPath = Join-Path $ProjectRoot $ScriptRelativePath
    if (Test-Path $scriptPath) {
        $cmd = 'python "' + $scriptPath + '"'
        if ($Args.Trim().Length -gt 0) { $cmd = $cmd + ' ' + $Args }
        [void]$Steps.Add((Invoke-Step -Name $StepName -Command $cmd -LogFile (Join-Path $LogsRoot $LogName)))
    }
    else {
        [void]$Warnings.Add('Missing script: ' + $ScriptRelativePath)
    }
}

# Safe mode scripts
Run-PythonScriptIfExists -StepName 'Validate foundations' -ScriptRelativePath 'scripts\12_validate_foundations.py' -Args '' -LogName '10_validate_foundations.log'
Run-PythonScriptIfExists -StepName 'Build inferred rules gold table' -ScriptRelativePath 'scripts\13_build_from_inferred_rules.py' -Args '' -LogName '11_build_inferred_rules.log'

# Sperant extraction/profile/build/train
if ($Mode -eq 'sperant' -or $Mode -eq 'full') {
    $envPath = Join-Path $ProjectRoot '.env'
    if (-not (Test-Path $envPath)) {
        [void]$Warnings.Add('Mode requires Sperant/Redshift but .env was not found. Extraction skipped if script needs credentials.')
    }

    $extractArgs = ''
    if ($ExtractLimit -gt 0) { $extractArgs = '--limit ' + $ExtractLimit }
    Run-PythonScriptIfExists -StepName 'Extract Redshift to Parquet' -ScriptRelativePath 'scripts\00_extract_redshift_to_parquet.py' -Args $extractArgs -LogName '20_extract_redshift.log'
    Run-PythonScriptIfExists -StepName 'Profile Sperant sources' -ScriptRelativePath 'scripts\09_profile_sperant_sources.py' -Args '' -LogName '21_profile_sperant_sources.log'
    Run-PythonScriptIfExists -StepName 'Build Sperant training dataset' -ScriptRelativePath 'scripts\10_build_sperant_training_dataset.py' -Args '--unit-focus departamentos' -LogName '22_build_sperant_training.log'
    Run-PythonScriptIfExists -StepName 'Train from Sperant' -ScriptRelativePath 'scripts\11_train_from_sperant.py' -Args '' -LogName '23_train_sperant.log'
}

# Full mode extra possible scripts
if ($Mode -eq 'full') {
    Run-PythonScriptIfExists -StepName 'Generate sample data' -ScriptRelativePath 'scripts\01_generate_sample_data.py' -Args '' -LogName '30_generate_sample_data.log'
    Run-PythonScriptIfExists -StepName 'Train model' -ScriptRelativePath 'scripts\02_train_model.py' -Args '' -LogName '31_train_model.log'
}

# Tests
if ($RunTests) {
    if (Test-Path (Join-Path $ProjectRoot 'tests')) {
        [void]$Steps.Add((Invoke-Step -Name 'Run pytest' -Command 'python -m pytest' -LogFile (Join-Path $LogsRoot '90_pytest.log')))
    }
    else {
        [void]$Warnings.Add('tests folder not found; pytest skipped.')
    }
}

# Inventory
$dataRaw = Join-Path $ProjectRoot 'data\raw'
$dataProcessed = Join-Path $ProjectRoot 'data\processed'
$modelsDir = Join-Path $ProjectRoot 'models'
$contractsDir = Join-Path $ProjectRoot 'contracts'
$notebooksDir = Join-Path $ProjectRoot 'notebooks'
$scriptsDir = Join-Path $ProjectRoot 'scripts'
$apiDir = Join-Path $ProjectRoot 'api'
$docsDir = Join-Path $ProjectRoot 'docs'

$Inventory = [ordered]@{
    parquet_raw_count = Get-FileCountSafe -Path $dataRaw -Filter '*.parquet'
    parquet_processed_count = Get-FileCountSafe -Path $dataProcessed -Filter '*.parquet'
    csv_count = Get-FileCountSafe -Path (Join-Path $ProjectRoot 'data') -Filter '*.csv'
    model_files_count = (Get-FileCountSafe -Path $modelsDir -Filter '*.joblib') + (Get-FileCountSafe -Path $modelsDir -Filter '*.pkl')
    contract_files_count = (Get-FileCountSafe -Path $contractsDir -Filter '*.yml') + (Get-FileCountSafe -Path $contractsDir -Filter '*.yaml')
    notebook_count = Get-FileCountSafe -Path $notebooksDir -Filter '*.ipynb'
    script_count = Get-FileCountSafe -Path $scriptsDir -Filter '*.py'
    api_py_count = Get-FileCountSafe -Path $apiDir -Filter '*.py'
    docs_md_count = Get-FileCountSafe -Path $docsDir -Filter '*.md'
    data_raw_size_mb = Get-DirSizeMbSafe -Path $dataRaw
    data_processed_size_mb = Get-DirSizeMbSafe -Path $dataProcessed
    reports_size_mb = Get-DirSizeMbSafe -Path $ReportsRoot
}

# Read possible report JSONs
$PossibleArtifacts = @(
    'reports\foundations\foundation_audit_riesgo_caida.json',
    'reports\foundations\inferred_rules_build_report.json',
    'reports\sperant_profile.json',
    'reports\model_report.json',
    'models\model_card.md'
)

$ArtifactAvailability = New-Object System.Collections.ArrayList
foreach ($rel in $PossibleArtifacts) {
    $p = Join-Path $ProjectRoot $rel
    $item = [ordered]@{
        path = $rel
        exists = (Test-Path $p)
        size_kb = 0
    }
    if (Test-Path $p) {
        try { $item.size_kb = [math]::Round(((Get-Item $p).Length / 1KB), 2) } catch {}
    }
    [void]$ArtifactAvailability.Add($item)
}

# Recommendations
if ($Inventory.parquet_raw_count -eq 0) {
    [void]$Recommendations.Add('Add or extract real Sperant parquet files into data/raw/sperant for real-data training.')
}
if ($Inventory.contract_files_count -eq 0) {
    [void]$Recommendations.Add('Create official data and decision contracts before freezing model rules.')
}
if ($Inventory.model_files_count -eq 0) {
    [void]$Recommendations.Add('Train and persist at least one model artifact before exposing production scoring.')
}
if ($Inventory.notebook_count -lt 8) {
    [void]$Recommendations.Add('Complete the 8-notebook university path to preserve the learning sequence.')
}
if ($Inventory.api_py_count -eq 0) {
    [void]$Recommendations.Add('Add FastAPI endpoints for single and batch scoring.')
}
if ($Warnings.Count -gt 0) {
    [void]$Recommendations.Add('Resolve warnings before treating the run as production-ready.')
}

$successCount = @($Steps | Where-Object { $_.status -eq 'success' }).Count
$failedCount = @($Steps | Where-Object { $_.status -eq 'failed' }).Count
$totalSteps = @($Steps).Count

$Readiness = 'red'
if ($failedCount -eq 0 -and $Inventory.parquet_processed_count -gt 0 -and $Inventory.contract_files_count -gt 0) {
    $Readiness = 'green'
}
elseif ($failedCount -le 2 -and $Inventory.contract_files_count -gt 0) {
    $Readiness = 'yellow'
}

$Manifest = [ordered]@{
    project_root = $ProjectRoot
    timestamp = $Timestamp
    mode = $Mode
    install_deps = [bool]$InstallDeps
    extract_limit = $ExtractLimit
    run_tests = [bool]$RunTests
    readiness = $Readiness
    steps_total = $totalSteps
    steps_success = $successCount
    steps_failed = $failedCount
    warnings = $Warnings
    recommendations = $Recommendations
    inventory = $Inventory
    artifact_availability = $ArtifactAvailability
    steps = $Steps
}

$ManifestPath = Join-Path $RunRoot 'run_manifest.json'
ConvertTo-JsonSafe $Manifest | Out-File -FilePath $ManifestPath -Encoding UTF8

# Executive Markdown report - no bold syntax to avoid parser confusion
$ReportPath = Join-Path $RunRoot 'BITACORA_EJECUTIVA.md'
$Md = New-Object System.Collections.ArrayList
function Add-Md {
    Param([string]$Line)
    [void]$Md.Add($Line)
}

Add-Md '# Machine Learning University - Bitacora Ejecutiva'
Add-Md ''
Add-Md ('Proyecto: ' + $ProjectRoot)
Add-Md ('Fecha de ejecucion: ' + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))
Add-Md ('Modo: ' + $Mode)
Add-Md ('Readiness: ' + $Readiness)
Add-Md ''
Add-Md '## 1. Resumen ejecutivo'
Add-Md ''
Add-Md ('Pasos ejecutados: ' + $totalSteps)
Add-Md ('Pasos correctos: ' + $successCount)
Add-Md ('Pasos fallidos: ' + $failedCount)
Add-Md ('Advertencias: ' + $Warnings.Count)
Add-Md ''
Add-Md 'Interpretacion:'
if ($Readiness -eq 'green') {
    Add-Md '- El proyecto tiene suficientes senales para continuar con entrenamiento, scoring o revision ejecutiva.'
}
elseif ($Readiness -eq 'yellow') {
    Add-Md '- El proyecto avanza, pero todavia tiene bloqueadores o tareas pendientes antes de congelar reglas.'
}
else {
    Add-Md '- El proyecto aun no esta listo para ser tratado como pipeline confiable. Revisar advertencias y logs.'
}
Add-Md ''
Add-Md '## 2. Inventario del datacenter local'
Add-Md ''
Add-Md '| Area | Valor |'
Add-Md '|---|---:|'
Add-Md ('| Parquet raw | ' + $Inventory.parquet_raw_count + ' |')
Add-Md ('| Parquet processed | ' + $Inventory.parquet_processed_count + ' |')
Add-Md ('| CSV | ' + $Inventory.csv_count + ' |')
Add-Md ('| Modelos | ' + $Inventory.model_files_count + ' |')
Add-Md ('| Contratos | ' + $Inventory.contract_files_count + ' |')
Add-Md ('| Notebooks | ' + $Inventory.notebook_count + ' |')
Add-Md ('| Scripts Python | ' + $Inventory.script_count + ' |')
Add-Md ('| Archivos API | ' + $Inventory.api_py_count + ' |')
Add-Md ('| Docs Markdown | ' + $Inventory.docs_md_count + ' |')
Add-Md ('| Size raw MB | ' + $Inventory.data_raw_size_mb + ' |')
Add-Md ('| Size processed MB | ' + $Inventory.data_processed_size_mb + ' |')
Add-Md ''
Add-Md '## 3. Pasos ejecutados'
Add-Md ''
Add-Md '| Paso | Estado | Exit code | Duracion seg | Log |'
Add-Md '|---|---|---:|---:|---|'
foreach ($s in $Steps) {
    $logRel = $s.log_file.Replace($ProjectRoot + '\', '')
    Add-Md ('| ' + $s.name + ' | ' + $s.status + ' | ' + $s.exit_code + ' | ' + $s.duration_seconds + ' | ' + $logRel + ' |')
}
if ($Steps.Count -eq 0) {
    Add-Md '| Sin pasos ejecutados | n/a |  |  |  |'
}
Add-Md ''
Add-Md '## 4. Artefactos detectados'
Add-Md ''
Add-Md '| Artefacto | Existe | KB |'
Add-Md '|---|---|---:|'
foreach ($a in $ArtifactAvailability) {
    Add-Md ('| ' + $a.path + ' | ' + $a.exists + ' | ' + $a.size_kb + ' |')
}
Add-Md ''
Add-Md '## 5. Advertencias'
Add-Md ''
if ($Warnings.Count -eq 0) {
    Add-Md '- Sin advertencias.'
}
else {
    foreach ($w in $Warnings) { Add-Md ('- ' + $w) }
}
Add-Md ''
Add-Md '## 6. Recomendaciones ejecutivas'
Add-Md ''
if ($Recommendations.Count -eq 0) {
    Add-Md '- Continuar con revision de resultados y congelamiento de reglas.'
}
else {
    foreach ($r in $Recommendations) { Add-Md ('- ' + $r) }
}
Add-Md ''
Add-Md '## 7. Proximo input recomendado'
Add-Md ''
Add-Md 'Copiar y completar:'
Add-Md ''
Add-Md '```text'
Add-Md 'Quiero continuar Machine Learning University.'
Add-Md 'Adjunto o confirmo:'
Add-Md '1. Reglas oficiales de separacion, venta/minuta y caida.'
Add-Md '2. Horizonte final del target: 15, 30, 45 o 60 dias.'
Add-Md '3. Grano oficial: codigo_proforma, codigo_unidad, o ambos.'
Add-Md '4. Features permitidas antes del snapshot.'
Add-Md '5. Umbrales bajo/medio/alto y capacidad comercial diaria.'
Add-Md '6. Costos economicos de falso positivo y falso negativo.'
Add-Md '7. Destino del feedback loop: parquet, Postgres, Supabase o Power BI.'
Add-Md '```'
Add-Md ''
Add-Md '## 8. Ubicaciones'
Add-Md ''
Add-Md ('Manifest JSON: ' + $ManifestPath)
Add-Md ('Logs: ' + $LogsRoot)
Add-Md ('Artifacts: ' + $ArtifactsRoot)

$Md | Out-File -FilePath $ReportPath -Encoding UTF8

$LatestReport = Join-Path $ReportsRoot 'executive_latest.md'
Copy-Item -Path $ReportPath -Destination $LatestReport -Force

Write-Ok ('Bitacora generated: ' + $ReportPath)
Write-Ok ('Latest report: ' + $LatestReport)
Write-Ok ('Manifest: ' + $ManifestPath)

if ($OpenReport) {
    try {
        Invoke-Item $ReportPath
    }
    catch {
        Write-Warn2 ('Could not open report automatically: ' + $_.Exception.Message)
    }
}
