from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

ALLOWED_FEATURES_RIESGO_CAIDA = [
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
    "descuento_pct",
]

FORBIDDEN_COLUMNS_RIESGO_CAIDA = [
    "fecha_caida",
    "motivo_caida",
    "estado_final",
    "fecha_firma_futura",
    "fecha_minuta_futura",
    "fecha_anulacion_futura",
    "monto_pagado_posterior_snapshot",
    "estado_cobranza_posterior_snapshot",
]

REQUIRED_TRAINING_COLUMNS_RIESGO_CAIDA = [
    "codigo_proforma",
    "fecha_snapshot",
    "caida_30d",
    *ALLOWED_FEATURES_RIESGO_CAIDA,
]


@dataclass(frozen=True)
class DecisionRule:
    level: str
    min_score: float
    max_score: float
    action: str
    responsible_role: str
    sla: str


DECISION_RULES_RIESGO_CAIDA = [
    DecisionRule("bajo", 0.0, 0.3999, "seguimiento_estandar", "asesor", "semana"),
    DecisionRule("medio", 0.4, 0.6999, "contacto_priorizado", "asesor", "24_horas"),
    DecisionRule("alto", 0.7, 1.0, "escalamiento_comercial", "jefe_comercial", "hoy"),
]


def validate_required_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> list[str]:
    """Devuelve la lista de columnas faltantes para un contrato.

    No lanza error automáticamente para poder usarlo en reportes de perfilamiento.
    """
    return [column for column in required_columns if column not in df.columns]


def validate_no_forbidden_columns(df: pd.DataFrame, forbidden_columns: Iterable[str]) -> list[str]:
    """Devuelve columnas prohibidas presentes en una tabla de features.

    Una columna prohibida no siempre significa que la tabla gold esté mal: puede existir para auditoría.
    Pero nunca debe entrar a X durante entrenamiento o scoring.
    """
    return [column for column in forbidden_columns if column in df.columns]


def build_model_matrix(df: pd.DataFrame, feature_columns: Iterable[str] = ALLOWED_FEATURES_RIESGO_CAIDA) -> pd.DataFrame:
    """Construye X usando únicamente features permitidas.

    Esta función es el guardián anti-leakage del alumno: aunque la tabla gold tenga fechas finales
    para auditoría, X queda limpia.
    """
    missing = validate_required_columns(df, feature_columns)
    if missing:
        raise ValueError(f"Faltan features permitidas requeridas: {missing}")
    return df[list(feature_columns)].copy()


def classify_risk_level(score: float) -> str:
    """Convierte un score en nivel operativo."""
    value = float(score)
    for rule in DECISION_RULES_RIESGO_CAIDA:
        if rule.min_score <= value <= rule.max_score:
            return rule.level
    raise ValueError(f"Score fuera de rango [0, 1]: {score}")


def decision_from_score(score: float, owner: str | None = None) -> dict:
    """Convierte un score en acción, responsable y SLA."""
    level = classify_risk_level(score)
    rule = next(rule for rule in DECISION_RULES_RIESGO_CAIDA if rule.level == level)
    return {
        "nivel_riesgo": rule.level,
        "accion": rule.action,
        "responsable": owner or rule.responsible_role,
        "rol_responsable": rule.responsible_role,
        "sla": rule.sla,
    }


def expected_value_at_risk(score: float, price: float) -> float:
    """Proxy económico: probabilidad de caída multiplicada por precio de departamento."""
    return round(float(score) * float(price), 2)


def audit_training_dataset(df: pd.DataFrame) -> dict:
    """Audita una tabla gold de riesgo de caída desde los fundamentos.

    La auditoría separa dos planos:
    - columnas requeridas para entrenamiento;
    - columnas prohibidas que no deben entrar a X.
    """
    missing_required = validate_required_columns(df, REQUIRED_TRAINING_COLUMNS_RIESGO_CAIDA)
    forbidden_present = validate_no_forbidden_columns(df, FORBIDDEN_COLUMNS_RIESGO_CAIDA)
    target_rate = None
    if "caida_30d" in df.columns and len(df) > 0:
        target_rate = float(pd.to_numeric(df["caida_30d"], errors="coerce").mean())

    has_snapshot = "fecha_snapshot" in df.columns
    has_grain = "codigo_proforma" in df.columns and has_snapshot

    return {
        "rows": int(len(df)),
        "missing_required_columns": missing_required,
        "forbidden_columns_present": forbidden_present,
        "target_rate": target_rate,
        "has_snapshot_column": has_snapshot,
        "has_minimum_grain": has_grain,
        "ready_for_training": not missing_required and has_snapshot and has_grain,
    }
