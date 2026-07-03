from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd

from src.mlu.calibration import calibration_table, calibration_summary
from src.mlu.official_rules import FEATURE_COLUMNS, TARGET
from src.mlu.config import MODEL_PATH, SPERANT_MODEL_READY_PATH
from src.mlu.leakage import assert_no_forbidden_columns

OUT_DIR = Path("reports/monitoring")


def main() -> None:
    if not SPERANT_MODEL_READY_PATH.exists():
        raise FileNotFoundError(f"No existe model-ready: {SPERANT_MODEL_READY_PATH}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No existe modelo: {MODEL_PATH}")
    df = pd.read_parquet(SPERANT_MODEL_READY_PATH).sort_values("fecha_snapshot").reset_index(drop=True)
    split_idx = int(len(df) * 0.75)
    test = df.iloc[split_idx:].copy()
    X = test.loc[:, FEATURE_COLUMNS].copy()
    X["tiene_cuota_inicial"] = X["tiene_cuota_inicial"].astype(bool).astype(int)
    assert_no_forbidden_columns(X, context="calibration_X")
    y = test[TARGET].astype(int)
    model = joblib.load(MODEL_PATH)
    scores = model.predict_proba(X)[:, 1]
    table = calibration_table(y, scores, n_bins=10)
    summary = calibration_summary(y, scores, n_bins=10)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_DIR / "calibration_table.csv", index=False)
    table.to_parquet(OUT_DIR / "calibration_table.parquet", index=False)
    (OUT_DIR / "calibration_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    md = "# Calibration Report - Riesgo de Caída v0.7\n\n"
    md += "## Lectura ejecutiva\n\nLa calibración evalúa si las probabilidades del modelo se parecen a tasas reales observadas.\n\n"
    md += f"- Brier score: {summary['brier_score']:.4f}\n"
    md += f"- Mean absolute calibration gap: {summary['mean_abs_calibration_gap']:.4f}\n"
    md += f"- Max absolute calibration gap: {summary['max_abs_calibration_gap']:.4f}\n"
    md += "\n## Tabla\n\n" + table.to_markdown(index=False)
    (OUT_DIR / "calibration_report.md").write_text(md, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
