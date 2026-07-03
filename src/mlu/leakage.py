from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

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


def audit_forbidden_columns(df: pd.DataFrame, forbidden_columns: list[str] | None = None) -> LeakageAudit:
    forbidden = forbidden_columns or FORBIDDEN_COLUMNS
    present = [col for col in forbidden if col in df.columns]
    return LeakageAudit(forbidden_present=present, status="fail" if present else "ok")


def assert_no_forbidden_columns(df: pd.DataFrame, context: str = "model_matrix") -> None:
    audit = audit_forbidden_columns(df)
    if audit.forbidden_present:
        raise ValueError(
            f"Anti-leakage fail en {context}. Columnas prohibidas presentes: {audit.forbidden_present}"
        )
