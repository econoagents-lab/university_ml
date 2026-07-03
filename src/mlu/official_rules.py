from __future__ import annotations

from pathlib import Path
import pandas as pd

from .leakage import assert_no_forbidden_columns, FORBIDDEN_COLUMNS

TARGET = "caida_30d"
FEATURE_COLUMNS = [
    "proyecto",
    "asesor",
    "medio_captacion",
    "canal_agrupado",
    "dormitorios",
    "precio_departamento",
    "dias_en_tuberia",
    "tiene_cuota_inicial",
    "cambios_unidad",
    "interacciones_ult_7d",
    "descuento_pct"
]
ID_COLUMNS = [
    "codigo_proforma",
    "codigo_unidad",
    "fecha_separacion",
    "fecha_snapshot",
    "snapshot_day",
    "source_system",
    "dataset_version"
]


def build_model_ready_dataset(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in FEATURE_COLUMNS + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas para model-ready: {missing}")
    selected = [c for c in ID_COLUMNS if c in df.columns] + FEATURE_COLUMNS + [TARGET]
    model_ready = df[selected].copy()
    assert_no_forbidden_columns(model_ready, context="model_ready_dataset")
    model_ready[TARGET] = model_ready[TARGET].astype(int)
    model_ready["tiene_cuota_inicial"] = model_ready["tiene_cuota_inicial"].astype(bool)
    return model_ready


def save_model_ready_dataset(input_path: str | Path, output_path: str | Path) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)
    df = pd.read_parquet(input_path)
    model_ready = build_model_ready_dataset(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model_ready.to_parquet(output_path, index=False)
    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "rows": int(len(model_ready)),
        "target_rate": float(model_ready[TARGET].mean()),
        "forbidden_columns_removed": FORBIDDEN_COLUMNS,
    }
