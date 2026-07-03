from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss


def calibration_table(y_true, y_score, n_bins: int = 10) -> pd.DataFrame:
    df = pd.DataFrame({"y_true": np.asarray(y_true, dtype=int), "score": np.asarray(y_score, dtype=float)})
    df = df.dropna().copy()
    if df.empty:
        raise ValueError("No se puede calcular calibración con datos vacíos.")
    df["bin"] = pd.qcut(df["score"].rank(method="first"), q=min(n_bins, len(df)), labels=False, duplicates="drop") + 1
    out = df.groupby("bin", as_index=False).agg(
        rows=("y_true", "size"),
        avg_score=("score", "mean"),
        event_rate=("y_true", "mean"),
        positives=("y_true", "sum"),
        min_score=("score", "min"),
        max_score=("score", "max"),
    )
    out["calibration_gap"] = out["event_rate"] - out["avg_score"]
    return out


def calibration_summary(y_true, y_score, n_bins: int = 10) -> dict:
    table = calibration_table(y_true, y_score, n_bins=n_bins)
    return {
        "rows": int(table["rows"].sum()),
        "brier_score": float(brier_score_loss(y_true, y_score)),
        "mean_abs_calibration_gap": float(table["calibration_gap"].abs().mean()),
        "max_abs_calibration_gap": float(table["calibration_gap"].abs().max()),
        "bins": int(len(table)),
    }
