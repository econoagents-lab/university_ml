# Quickstart

## 1. Crear entorno

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Generar data sintética

```powershell
python scripts/01_generate_sample_data.py
```

## 3. Entrenar modelo

```powershell
python scripts/02_train_model.py
```

## 4. Abrir notebook

```powershell
.\run.ps1 -Chapter 01
```

## 5. Servir API

```powershell
uvicorn api.main:app --reload
```

## 6. Probar endpoint

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/predict/riesgo-caida `
  -ContentType "application/json" `
  -Body '{
    "proyecto":"Proyecto Aurora",
    "asesor":"Asesor Norte",
    "medio_captacion":"facebook",
    "precio_departamento":620000,
    "dias_en_tuberia":45,
    "dormitorios":3,
    "tiene_cuota_inicial":false,
    "cambios_unidad":1,
    "interacciones_ult_7d":0,
    "descuento_pct":0.03
  }'
```

## Camino con Sperant/Redshift

```powershell
copy .env.example .env
# completar credenciales en .env
python scripts/00_extract_redshift_to_parquet.py --limit 1000
python scripts/09_profile_sperant_sources.py
python scripts/10_build_sperant_training_dataset.py --unit-focus departamentos
$env:MLU_DATA_MODE="sperant"
python scripts/11_train_from_sperant.py
uvicorn api.main:app --reload
```

Para usar parquets ya exportados manualmente:

```powershell
python scripts/10_build_sperant_training_dataset.py --input-dir "C:\ruta\a\parquets"
```

---

## v0.4 · Usar reglas inferidas

1. Copia `procesos.parquet` a:

```powershell
mkdir data\raw\sperant
copy C:\ruta\a\procesos.parquet data\raw\sperant\procesos.parquet
```

2. Construye gold table con reglas inferidas:

```powershell
python scripts/13_build_from_inferred_rules.py
```

3. Revisa:

```text
reports/foundations/inferred_rules_build_report.json
```

4. Ajusta las reglas desde:

```text
docs/TODO_NEXT_INPUT_FILLED_FROM_HISTORY.md
```
