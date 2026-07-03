from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd

FEEDBACK_COLUMNS = [
    "codigo_proforma",
    "codigo_unidad",
    "fecha_score",
    "riesgo_caida",
    "nivel_riesgo",
    "ranking_prioridad",
    "responsable",
    "accion_tomada",
    "fecha_accion",
    "resultado_7d",
    "resultado_30d",
    "caida_real_30d",
    "comentario",
]

ALLOWED_ACTIONS = {
    "contactado_cliente",
    "contactado_banco",
    "renegociacion_precio",
    "regularizo_cuota_inicial",
    "cambio_unidad",
    "escalado_gerencia",
    "sin_accion",
    "pendiente",
}
ALLOWED_OUTCOMES = {"sigue_tuberia", "firmo_minuta", "cayo", "reprogramado", "sin_actualizacion", "pendiente"}


def build_feedback_template(ranking: pd.DataFrame, top_n: int = 100, fecha_score: str | None = None) -> pd.DataFrame:
    if ranking.empty:
        raise ValueError("ranking vacío; no se puede crear feedback template")
    fecha_score = fecha_score or date.today().isoformat()
    cols = [c for c in ["codigo_proforma", "codigo_unidad", "riesgo_caida", "nivel_riesgo", "ranking_prioridad", "responsable"] if c in ranking.columns]
    out = ranking.sort_values("ranking_prioridad").head(top_n)[cols].copy()
    out["fecha_score"] = fecha_score
    out["accion_tomada"] = "pendiente"
    out["fecha_accion"] = ""
    out["resultado_7d"] = "pendiente"
    out["resultado_30d"] = "pendiente"
    out["caida_real_30d"] = ""
    out["comentario"] = ""
    return out[[c for c in FEEDBACK_COLUMNS if c in out.columns]]


def validate_feedback_log(df: pd.DataFrame) -> dict:
    missing = [c for c in FEEDBACK_COLUMNS if c not in df.columns]
    invalid_actions = []
    invalid_outcomes = []
    if "accion_tomada" in df.columns:
        invalid_actions = sorted(set(df["accion_tomada"].dropna().astype(str)) - ALLOWED_ACTIONS)
    if "resultado_7d" in df.columns:
        invalid_outcomes += sorted(set(df["resultado_7d"].dropna().astype(str)) - ALLOWED_OUTCOMES)
    if "resultado_30d" in df.columns:
        invalid_outcomes += sorted(set(df["resultado_30d"].dropna().astype(str)) - ALLOWED_OUTCOMES)
    return {
        "rows": int(len(df)),
        "missing_columns": missing,
        "invalid_actions": sorted(set(invalid_actions)),
        "invalid_outcomes": sorted(set(invalid_outcomes)),
        "is_valid": not missing and not invalid_actions and not invalid_outcomes,
    }


def merge_feedback_with_ranking(feedback: pd.DataFrame, ranking: pd.DataFrame) -> pd.DataFrame:
    keys = ["codigo_proforma", "codigo_unidad"]
    for key in keys:
        if key not in feedback.columns or key not in ranking.columns:
            raise ValueError(f"Falta llave para merge feedback-ranking: {key}")
    ranking_cols = [c for c in ["codigo_proforma", "codigo_unidad", "proyecto", "asesor", "precio_departamento", "valor_esperado_en_riesgo"] if c in ranking.columns]
    return feedback.merge(ranking[ranking_cols], on=keys, how="left", suffixes=("", "_ranking"))


def save_feedback_template(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "feedback_log_template.csv", index=False, encoding="utf-8-sig")
    df.to_parquet(output_dir / "feedback_log_template.parquet", index=False)
