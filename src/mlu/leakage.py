from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import pandas as pd

# Columnas que pueden existir en raw/auditoria para construir target o revisar lineage,
# pero nunca deben entrar a feature_table, model_matrix, X de entrenamiento o X de scoring.
FORBIDDEN_COLUMNS = [
    "fecha_caida",
    "motivo_caida",
    "estado_final",
    "fecha_firma",
    "fecha_anulacion",
    "momento_caida",
    "dias_hasta_caida",
]


@dataclass
class LeakageAudit:
    forbidden_present: list[str]
    status: str


def _normalize_columns(columns: Iterable[str]) -> list[str]:
    return [str(col) for col in columns]


def audit_forbidden_columns(
    df: pd.DataFrame,
    forbidden_columns: list[str] | None = None,
) -> LeakageAudit:
    """Audita columnas prohibidas sin lanzar error.

    Uso correcto:
    - raw/auditoria: se puede auditar y registrar columnas futuras.
    - model_ready/X/scoring: se debe usar assert_no_forbidden_columns.
    """
    forbidden = forbidden_columns or FORBIDDEN_COLUMNS
    present = [col for col in forbidden if col in df.columns]
    return LeakageAudit(forbidden_present=present, status="fail" if present else "ok")


def forbidden_columns_present(
    columns: Iterable[str],
    forbidden_columns: list[str] | None = None,
) -> list[str]:
    """Devuelve nombres prohibidos presentes en una lista de columnas."""
    forbidden = forbidden_columns or FORBIDDEN_COLUMNS
    normalized = set(_normalize_columns(columns))
    return [col for col in forbidden if col in normalized]


def assert_no_forbidden_columns(
    df: pd.DataFrame,
    context: str = "model_matrix",
    forbidden_columns: list[str] | None = None,
) -> None:
    """Falla si el dataframe contiene columnas prohibidas.

    Esta función es estricta a propósito. No debe llamarse sobre raw histórico
    antes de seleccionar features, porque raw puede conservar columnas de auditoría.
    Debe llamarse sobre artefactos model-ready: feature_table, model_matrix,
    X_train, X_test, X_scoring, outputs de scoring que alimenten operación.
    """
    audit = audit_forbidden_columns(df, forbidden_columns=forbidden_columns)
    if audit.forbidden_present:
        raise ValueError(
            f"Anti-leakage fail en {context}. "
            f"Columnas prohibidas presentes: {audit.forbidden_present}"
        )


def assert_columns_are_allowed(
    columns: Iterable[str],
    context: str = "feature_contract",
    forbidden_columns: list[str] | None = None,
) -> None:
    """Falla si el contrato/lista de features intenta usar columnas prohibidas."""
    present = forbidden_columns_present(columns, forbidden_columns=forbidden_columns)
    if present:
        raise ValueError(
            f"Anti-leakage fail en {context}. "
            f"Columnas prohibidas declaradas como features: {present}"
        )


def drop_forbidden_columns(
    df: pd.DataFrame,
    forbidden_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Retira columnas prohibidas y devuelve (dataframe_limpio, columnas_removidas).

    No reemplaza al assert. Sirve para cruzar la frontera raw/audit -> model-ready.
    Después de esta función debe llamarse assert_no_forbidden_columns.
    """
    forbidden = forbidden_columns or FORBIDDEN_COLUMNS
    removed = [col for col in forbidden if col in df.columns]
    clean = df.drop(columns=removed, errors="ignore").copy()
    return clean, removed
