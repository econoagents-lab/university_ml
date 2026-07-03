from __future__ import annotations

import pandas as pd
from .leakage import assert_columns_are_allowed, assert_no_forbidden_columns, audit_forbidden_columns

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

    Arquitectura anti-leakage:
    1. El dataframe de entrada puede ser raw/auditable y contener columnas futuras
       como fecha_caida o fecha_firma.
    2. Esta función NO entrena sobre ese raw. Primero cruza la frontera y selecciona
       únicamente FEATURE_COLUMNS.
    3. Recién sobre la tabla de features se ejecuta el assert estricto.

    Resultado: fecha_caida puede existir en raw para construir target/auditoría,
    pero nunca aparece en feature_table/model_matrix.
    """
    # Auditoría no bloqueante del raw: útil para bitácora, no para matar el flujo.
    _raw_audit = audit_forbidden_columns(df)

    # El contrato de features sí debe ser estrictamente limpio.
    assert_columns_are_allowed(FEATURE_COLUMNS, context="feature_columns_contract")

    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    features = df.loc[:, FEATURE_COLUMNS].copy()
    assert_no_forbidden_columns(features, context="feature_table_after_selection")
    features["tiene_cuota_inicial"] = features["tiene_cuota_inicial"].astype(bool).astype(int)
    return features


def build_target(df: pd.DataFrame) -> pd.Series:
    if TARGET not in df.columns:
        raise ValueError(f"No existe la variable objetivo: {TARGET}")
    return df[TARGET].astype(int)


def build_scoring_features(df: pd.DataFrame) -> pd.DataFrame:
    X = build_feature_table(df)
    assert_no_forbidden_columns(X, context="scoring_X")
    return X
