from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_SPERANT_DIR = RAW_DIR / "sperant"
PROCESSED_DIR = DATA_DIR / "processed"
SILVER_DIR = PROCESSED_DIR / "silver"
GOLD_DIR = PROCESSED_DIR / "gold"
METADATA_DIR = DATA_DIR / "metadata"

SAMPLE_DATA_PATH = DATA_DIR / "sample" / "fact_operaciones_sample.csv"
NEW_CASES_PATH = DATA_DIR / "new" / "alumno_nuevo_sample.csv"
SPERANT_TRAINING_PATH = GOLD_DIR / "riesgo_caida_training.parquet"
SPERANT_SCORING_PATH = GOLD_DIR / "riesgo_caida_scoring_actual.parquet"

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "riesgo_caida_model.joblib"
FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.json"
MODEL_MANIFEST_PATH = MODELS_DIR / "model_manifest.json"
STATE_PATH = PROJECT_ROOT / "state" / "progress.json"
REPORTS_DIR = PROJECT_ROOT / "reports"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"

# synthetic: usa dataset educativo seguro.
# sperant: usa data/processed/gold/riesgo_caida_training.parquet si existe.
MLU_DATA_MODE = os.getenv("MLU_DATA_MODE", "synthetic").strip().lower()

# Carpeta local donde el alumno puede copiar parquets exportados desde Redshift/Sperant.
# Ejemplo: MLU_SPERANT_LOCAL_DIR=C:/data/sperant_exports
MLU_SPERANT_LOCAL_DIR = os.getenv("MLU_SPERANT_LOCAL_DIR", "").strip()

SPERANT_MODEL_READY_PATH = GOLD_DIR / "riesgo_caida_training_model_ready.parquet"
SCORING_RANKING_PATH = PROCESSED_DIR / "scoring" / "ranking_operaciones_riesgo_caida.parquet"
