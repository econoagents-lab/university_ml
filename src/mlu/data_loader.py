from __future__ import annotations

from pathlib import Path
import pandas as pd

from .config import (
    SAMPLE_DATA_PATH,
    NEW_CASES_PATH,
    SPERANT_TRAINING_PATH,
    MLU_DATA_MODE,
)
from .data_generator import save_sample_data


def load_operations(path: Path | None = None) -> pd.DataFrame:
    """Carga el dataset usado por los notebooks.

    Modo educativo seguro:
        MLU_DATA_MODE=synthetic -> usa data/sample/fact_operaciones_sample.csv

    Modo Sperant/Redshift:
        MLU_DATA_MODE=sperant -> usa data/processed/gold/riesgo_caida_training.parquet
        Este archivo se construye con scripts/10_build_sperant_training_dataset.py.
    """
    if path is not None:
        return _read_any(path)

    if MLU_DATA_MODE == "sperant" and SPERANT_TRAINING_PATH.exists():
        return pd.read_parquet(SPERANT_TRAINING_PATH)

    if not SAMPLE_DATA_PATH.exists():
        save_sample_data(SAMPLE_DATA_PATH, NEW_CASES_PATH)
    return pd.read_csv(SAMPLE_DATA_PATH, parse_dates=["fecha_separacion"])


def load_new_cases(path: Path = NEW_CASES_PATH) -> pd.DataFrame:
    if not path.exists():
        save_sample_data(SAMPLE_DATA_PATH, NEW_CASES_PATH)
    return pd.read_csv(path, parse_dates=["fecha_separacion"])


def _read_any(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Formato no soportado: {path}")
