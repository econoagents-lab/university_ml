from __future__ import annotations

import pandas as pd
from .leakage import assert_no_forbidden_columns

TARGET = "caida_30d"
CATEGORICAL_FEATURES = ["proyecto", "asesor", "medio_captacion", "canal_agrupado"]
NUMERIC_FEATURES = [
    "dormitorios",
    "precio_departamento",
    "dias_en_tuberia",
    "cambios_unidad",
    "interacciones_ult_7d",
    "descuento_pct",
]
BOOLEAN_FEATURES = ["tiene_cuota_inicial"]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES + BOOLEAN_FEATURES


def build_feature_table(df: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de features del modelo.

    Esta función es deliberadamente simple para que el alumno entienda el flujo:
    tabla histórica -> features limpias -> X/y.
    """
    assert_no_forbidden_columns(df, context="input_dataframe_before_feature_selection")
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    features = df[FEATURE_COLUMNS].copy()
    assert_no_forbidden_columns(features, context="model_matrix_X")
    features["tiene_cuota_inicial"] = features["tiene_cuota_inicial"].astype(bool).astype(int)
    return features


def build_target(df: pd.DataFrame) -> pd.Series:
    if TARGET not in df.columns:
        raise ValueError(f"No existe la variable objetivo: {TARGET}")
    return df[TARGET].astype(int)


def build_scoring_features(df: pd.DataFrame) -> pd.DataFrame:
    return build_feature_table(df)
