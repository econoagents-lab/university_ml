Param(
    [ValidateSet("01","02","03","04","05","06","07","08")]
    [string]$Chapter = "01",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "=== Machine Learning University ===" -ForegroundColor Cyan
Write-Host "Modo de datos MLU_DATA_MODE=$env:MLU_DATA_MODE (vacío = synthetic)" -ForegroundColor DarkCyan
Write-Host "Capítulo solicitado: $Chapter" -ForegroundColor Yellow

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (!(Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Verificando dependencias..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

if (!(Test-Path "data\sample\fact_operaciones_sample.csv")) {
    Write-Host "Generando datos sintéticos seguros..." -ForegroundColor Yellow
    python scripts/01_generate_sample_data.py
}

if (-not $Force) {
    python scripts/05_unlock_chapter.py --chapter $Chapter
}

$NotebookMap = @{
    "01" = "notebooks/01_Historia_del_Negocio.ipynb"
    "02" = "notebooks/02_Exploracion_Visual.ipynb"
    "03" = "notebooks/03_Profesor_Estudiando.ipynb"
    "04" = "notebooks/04_Entrenamiento_del_Modelo.ipynb"
    "05" = "notebooks/05_Dia_del_Examen.ipynb"
    "06" = "notebooks/06_Correccion_del_Examen.ipynb"
    "07" = "notebooks/07_Que_Aprendio_El_Profesor.ipynb"
    "08" = "notebooks/08_Alumno_Nuevo.ipynb"
}

$NotebookPath = $NotebookMap[$Chapter]
Write-Host "Abriendo notebook: $NotebookPath" -ForegroundColor Green
jupyter lab $NotebookPath
