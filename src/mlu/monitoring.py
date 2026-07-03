from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DriftStatus:
    metric: float
    status: str
    threshold_warning: float
    threshold_fail: float


def _status(value: float, warning: float = 0.10, fail: float = 0.25) -> str:
    if pd.isna(value):
        return "unknown"
    if value >= fail:
        return "fail"
    if value >= warning:
        return "warning"
    return "ok"


def _safe_distribution(values: pd.Series) -> pd.Series:
    counts = values.fillna("__MISSING__").astype(str).value_counts(normalize=True)
    return counts.sort_index()


def population_stability_index(expected: pd.Series, actual: pd.Series, bins: int = 10, epsilon: float = 1e-6) -> float:
    """Calcula PSI. Para numéricos usa cuantiles de expected; para categóricos usa distribución por categoría."""
    if expected.empty or actual.empty:
        return float("nan")

    expected_non_null = expected.dropna()
    actual_non_null = actual.dropna()

    if (pd.api.types.is_numeric_dtype(expected) and not pd.api.types.is_bool_dtype(expected) and expected_non_null.nunique() > 1):
        quantiles = np.linspace(0, 1, bins + 1)
        edges = np.unique(np.nanquantile(expected_non_null.astype(float), quantiles))
        if len(edges) <= 2:
            exp_dist = _safe_distribution(expected)
            act_dist = _safe_distribution(actual)
        else:
            edges[0] = -np.inf
            edges[-1] = np.inf
            exp_bins = pd.cut(expected.astype(float), bins=edges, include_lowest=True)
            act_bins = pd.cut(actual.astype(float), bins=edges, include_lowest=True)
            exp_dist = exp_bins.value_counts(normalize=True, sort=False)
            act_dist = act_bins.value_counts(normalize=True, sort=False)
    else:
        exp_dist = _safe_distribution(expected)
        act_dist = _safe_distribution(actual)

    categories = exp_dist.index.union(act_dist.index)
    exp = exp_dist.reindex(categories, fill_value=0).astype(float) + epsilon
    act = act_dist.reindex(categories, fill_value=0).astype(float) + epsilon
    return float(((act - exp) * np.log(act / exp)).sum())


def build_feature_profile(df: pd.DataFrame, feature_columns: Iterable[str]) -> pd.DataFrame:
    rows: list[dict] = []
    total = len(df)
    for col in feature_columns:
        if col not in df.columns:
            rows.append({"feature": col, "exists": False, "rows": total, "null_rate": 1.0, "dtype": "missing"})
            continue
        s = df[col]
        row = {
            "feature": col,
            "exists": True,
            "rows": total,
            "null_rate": float(s.isna().mean()) if total else 0.0,
            "dtype": str(s.dtype),
            "n_unique": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
            row.update({
                "mean": float(s.mean()) if len(s.dropna()) else np.nan,
                "std": float(s.std()) if len(s.dropna()) else np.nan,
                "p10": float(s.quantile(0.10)) if len(s.dropna()) else np.nan,
                "p50": float(s.quantile(0.50)) if len(s.dropna()) else np.nan,
                "p90": float(s.quantile(0.90)) if len(s.dropna()) else np.nan,
            })
        else:
            mode = s.dropna().astype(str).mode()
            row["top_value"] = str(mode.iloc[0]) if not mode.empty else ""
        rows.append(row)
    return pd.DataFrame(rows)


def compute_feature_drift(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    feature_columns: Iterable[str],
    threshold_warning: float = 0.10,
    threshold_fail: float = 0.25,
) -> pd.DataFrame:
    rows: list[dict] = []
    for col in feature_columns:
        if col not in reference_df.columns or col not in current_df.columns:
            rows.append({
                "feature": col,
                "drift_metric": np.nan,
                "status": "missing",
                "reference_rows": int(len(reference_df)),
                "current_rows": int(len(current_df)),
            })
            continue
        metric = population_stability_index(reference_df[col], current_df[col])
        rows.append({
            "feature": col,
            "drift_metric": metric,
            "status": _status(metric, threshold_warning, threshold_fail),
            "reference_rows": int(reference_df[col].notna().sum()),
            "current_rows": int(current_df[col].notna().sum()),
            "reference_null_rate": float(reference_df[col].isna().mean()),
            "current_null_rate": float(current_df[col].isna().mean()),
        })
    return pd.DataFrame(rows).sort_values(["status", "drift_metric"], ascending=[True, False]).reset_index(drop=True)


def compute_prediction_drift(
    reference_scores: pd.Series,
    current_scores: pd.Series,
    threshold_warning: float = 0.10,
    threshold_fail: float = 0.25,
) -> dict:
    psi = population_stability_index(reference_scores.astype(float), current_scores.astype(float))
    return {
        "reference_rows": int(len(reference_scores)),
        "current_rows": int(len(current_scores)),
        "reference_mean_score": float(reference_scores.mean()),
        "current_mean_score": float(current_scores.mean()),
        "reference_p90_score": float(reference_scores.quantile(0.90)),
        "current_p90_score": float(current_scores.quantile(0.90)),
        "prediction_psi": float(psi),
        "status": _status(float(psi), threshold_warning, threshold_fail),
        "threshold_warning": threshold_warning,
        "threshold_fail": threshold_fail,
    }


def summarize_drift(feature_drift: pd.DataFrame, prediction_drift: dict | None = None) -> dict:
    status_counts = feature_drift["status"].value_counts().to_dict() if not feature_drift.empty else {}
    worst = feature_drift.sort_values("drift_metric", ascending=False).head(5)
    global_status = "ok"
    if "fail" in status_counts or (prediction_drift and prediction_drift.get("status") == "fail"):
        global_status = "fail"
    elif "warning" in status_counts or (prediction_drift and prediction_drift.get("status") == "warning"):
        global_status = "warning"
    return {
        "global_status": global_status,
        "feature_status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "top_drift_features": worst[["feature", "drift_metric", "status"]].to_dict(orient="records") if not worst.empty else [],
        "prediction_drift": prediction_drift or {},
    }
