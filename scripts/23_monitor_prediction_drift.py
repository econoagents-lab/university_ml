from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd

from src.mlu.monitoring import compute_prediction_drift
from src.mlu.official_rules import FEATURE_COLUMNS
from src.mlu.config import MODEL_PATH, SPERANT_MODEL_READY_PATH
from src.mlu.leakage import assert_no_forbidden_columns

OUT_DIR = Path("reports/monitoring")


def _prepare_x(df: pd.DataFrame) -> pd.DataFrame:
    X = df.loc[:, FEATURE_COLUMNS].copy()
    X["tiene_cuota_inicial"] = X["tiene_cuota_inicial"].astype(bool).astype(int)
    assert_no_forbidden_columns(X, context="prediction_drift_X")
    return X


def main() -> None:
    if not SPERANT_MODEL_READY_PATH.exists():
        raise FileNotFoundError(f"No existe model-ready: {SPERANT_MODEL_READY_PATH}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No existe modelo: {MODEL_PATH}")
    df = pd.read_parquet(SPERANT_MODEL_READY_PATH).sort_values("fecha_snapshot").reset_index(drop=True)
    split_idx = int(len(df) * 0.75)
    reference, current = df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()
    model = joblib.load(MODEL_PATH)
    ref_scores = pd.Series(model.predict_proba(_prepare_x(reference))[:, 1])
    cur_scores = pd.Series(model.predict_proba(_prepare_x(current))[:, 1])
    summary = compute_prediction_drift(ref_scores, cur_scores)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"segment": "reference", "score": ref_scores}).to_csv(OUT_DIR / "reference_scores.csv", index=False)
    pd.DataFrame({"segment": "current", "score": cur_scores}).to_csv(OUT_DIR / "current_scores.csv", index=False)
    (OUT_DIR / "prediction_drift.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
