from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

ACTION_PENDING = {"pendiente", "sin_accion", "", "nan", "none"}


def create_experiment_assignments(
    ranking: pd.DataFrame,
    top_n: int = 100,
    holdout_rate: float = 0.20,
    random_state: int = 42,
) -> pd.DataFrame:
    if ranking.empty:
        raise ValueError("ranking vacío; no se puede crear experimento.")
    if not 0 < holdout_rate < 0.5:
        raise ValueError("holdout_rate debe estar entre 0 y 0.5 para no bloquear la operación comercial.")
    work = ranking.sort_values(["ranking_prioridad" if "ranking_prioridad" in ranking.columns else "riesgo_caida"], ascending=True).head(top_n).copy()
    rng = np.random.default_rng(random_state)
    work["random_value"] = rng.random(len(work))
    work["experiment_group"] = np.where(work["random_value"] < holdout_rate, "control_holdout", "intervention")
    work["experiment_name"] = "riesgo_caida_followup_v0_7"
    work["experiment_version"] = "0.7.0"
    work["holdout_rate"] = holdout_rate
    work["is_eligible"] = True
    return work


def analyze_intervention_effect(feedback: pd.DataFrame) -> dict:
    if feedback.empty:
        return {"status": "no_data", "rows": 0, "message": "No hay feedback operativo registrado."}
    df = feedback.copy()
    if "caida_real_30d" not in df.columns:
        return {"status": "missing_outcome", "rows": int(len(df)), "message": "Falta caida_real_30d."}
    action = df.get("accion_tomada", pd.Series(["pendiente"] * len(df), index=df.index)).fillna("pendiente").astype(str).str.lower()
    df["intervened"] = ~action.isin(ACTION_PENDING)
    outcome_raw = df["caida_real_30d"].replace({"": np.nan, "True": 1, "False": 0, True: 1, False: 0})
    outcome = pd.to_numeric(outcome_raw, errors="coerce")
    df = df.assign(caida_real_30d_num=outcome).dropna(subset=["caida_real_30d_num"])
    if len(df) < 20 or df["intervened"].nunique() < 2:
        return {
            "status": "insufficient_data",
            "rows_with_outcome": int(len(df)),
            "message": "Se necesitan al menos 20 resultados y ambos grupos: intervenido/no intervenido.",
        }
    grouped = df.groupby("intervened").agg(rows=("caida_real_30d_num", "size"), event_rate=("caida_real_30d_num", "mean")).reset_index()
    rates = dict(zip(grouped["intervened"].astype(bool), grouped["event_rate"].astype(float)))
    intervention_rate = rates.get(True, np.nan)
    control_rate = rates.get(False, np.nan)
    return {
        "status": "ok",
        "rows_with_outcome": int(len(df)),
        "intervention_event_rate": float(intervention_rate),
        "control_event_rate": float(control_rate),
        "absolute_lift_reduction": float(control_rate - intervention_rate),
        "relative_lift_reduction": float((control_rate - intervention_rate) / control_rate) if control_rate and not np.isnan(control_rate) else np.nan,
        "group_table": grouped.to_dict(orient="records"),
    }
