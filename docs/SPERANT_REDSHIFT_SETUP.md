# Puerta Redshift · Sperant dentro de Machine Learning University

## La idea

Un notebook sin fuente real es una maqueta. Redshift/Sperant convierte la universidad en una fábrica: procesos, unidades, proformas, clientes y leads pasan a ser contratos, features y decisiones.

## Flujo recomendado

```text
Redshift/Sperant
  -> data/raw/sperant/*.parquet
  -> data/processed/gold/riesgo_caida_training.parquet
  -> modelo riesgo_caida_model.joblib
  -> API /predict/riesgo-caida
  -> dashboard / seguimiento comercial
```

## 1. Configurar `.env`

Copia `.env.example` como `.env` y completa credenciales localmente.

Nunca subas `.env` ni `data/raw` a GitHub.

## 2. Extraer tablas

```powershell
python scripts/00_extract_redshift_to_parquet.py
```

Para prueba rápida:

```powershell
python scripts/00_extract_redshift_to_parquet.py --limit 1000
```

## 3. Perfilar fuentes

```powershell
python scripts/09_profile_sperant_sources.py
```

## 4. Construir gold table de riesgo de caída

```powershell
python scripts/10_build_sperant_training_dataset.py --unit-focus departamentos --snapshot-days 7 14 30
```

## 5. Entrenar con data real

```powershell
$env:MLU_DATA_MODE="sperant"
python scripts/11_train_from_sperant.py
```

## 6. Levantar API

```powershell
uvicorn api.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Decisión técnica recomendada

MVP: Parquet local + DuckDB/Pandas + FastAPI local.  
Profesional: extracción diaria Redshift -> Parquet -> gold marts -> modelo.  
Enterprise: feature store, registry, drift, feedback loop y acciones integradas al CRM.
