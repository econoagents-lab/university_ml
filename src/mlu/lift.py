from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LiftSummary:
    baseline_rate: float
    top_decile_rate: float
    top_decile_lift: float
    top_20_capture_rate: float
    total_positives: int


def assign_deciles(scores: pd.Series, n_deciles: int = 10) -> pd.Series:
    """Assign deciles where 1 means highest risk."""
    ranked = scores.rank(method="first", ascending=False)
    deciles = pd.qcut(ranked, q=n_deciles, labels=False, duplicates="drop") + 1
    return deciles.astype(int)


def compute_lift_deciles(
    df: pd.DataFrame,
    score_col: str = "riesgo_caida",
    target_col: str = "caida_30d",
    value_col: str | None = "precio_departamento",
    n_deciles: int = 10,
) -> pd.DataFrame:
    required = {score_col, target_col}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas requeridas para lift: {missing}")
    if df.empty:
        raise ValueError("No se puede calcular lift con dataframe vacío.")

    work = df.copy()
    work[target_col] = work[target_col].astype(int)
    work["decile"] = assign_deciles(work[score_col], n_deciles=n_deciles)
    baseline_rate = float(work[target_col].mean())
    total_positives = int(work[target_col].sum())

    aggregations = {
        "rows": (target_col, "size"),
        "positives": (target_col, "sum"),
        "avg_score": (score_col, "mean"),
        "min_score": (score_col, "min"),
        "max_score": (score_col, "max"),
    }
    if value_col and value_col in work.columns:
        aggregations["valor_total"] = (value_col, "sum")
        work["valor_positivo"] = work[value_col] * work[target_col]
        aggregations["valor_caidas"] = ("valor_positivo", "sum")

    out = work.groupby("decile", as_index=False).agg(**aggregations).sort_values("decile")
    out["event_rate"] = out["positives"] / out["rows"]
    out["baseline_rate"] = baseline_rate
    out["lift"] = np.where(baseline_rate > 0, out["event_rate"] / baseline_rate, np.nan)
    out["capture_rate"] = np.where(total_positives > 0, out["positives"] / total_positives, 0.0)
    out["cum_rows"] = out["rows"].cumsum()
    out["cum_positives"] = out["positives"].cumsum()
    out["cum_capture_rate"] = np.where(total_positives > 0, out["cum_positives"] / total_positives, 0.0)
    out["cum_population_rate"] = out["cum_rows"] / len(work)
    out["cum_lift"] = np.where(out["cum_population_rate"] > 0, out["cum_capture_rate"] / out["cum_population_rate"], np.nan)
    return out


def precision_at_k(df: pd.DataFrame, score_col: str, target_col: str, k_values: Iterable[int]) -> pd.DataFrame:
    work = df.sort_values(score_col, ascending=False).reset_index(drop=True).copy()
    total_positives = int(work[target_col].astype(int).sum())
    rows = []
    for k in k_values:
        k = min(int(k), len(work))
        if k <= 0:
            continue
        top = work.head(k)
        positives = int(top[target_col].astype(int).sum())
        rows.append({
            "k": k,
            "positives": positives,
            "precision_at_k": positives / k,
            "capture_rate_at_k": positives / total_positives if total_positives else 0.0,
        })
    return pd.DataFrame(rows)


def summarize_lift(lift_df: pd.DataFrame) -> LiftSummary:
    if lift_df.empty:
        raise ValueError("lift_df vacío")
    top = lift_df.sort_values("decile").iloc[0]
    top_20 = lift_df[lift_df["decile"].isin([1, 2])]
    return LiftSummary(
        baseline_rate=float(lift_df["baseline_rate"].iloc[0]),
        top_decile_rate=float(top["event_rate"]),
        top_decile_lift=float(top["lift"]),
        top_20_capture_rate=float(top_20["positives"].sum() / lift_df["positives"].sum()) if lift_df["positives"].sum() else 0.0,
        total_positives=int(lift_df["positives"].sum()),
    )
