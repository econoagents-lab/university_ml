from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.mlu.monitoring import build_feature_profile, compute_feature_drift, summarize_drift
from src.mlu.official_rules import FEATURE_COLUMNS
from src.mlu.config import SPERANT_MODEL_READY_PATH

OUT_DIR = Path("reports/monitoring")


def main() -> None:
    if not SPERANT_MODEL_READY_PATH.exists():
        raise FileNotFoundError(f"No existe model-ready: {SPERANT_MODEL_READY_PATH}")
    df = pd.read_parquet(SPERANT_MODEL_READY_PATH).sort_values("fecha_snapshot").reset_index(drop=True)
    split_idx = int(len(df) * 0.75)
    reference = df.iloc[:split_idx].copy()
    current = df.iloc[split_idx:].copy()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reference_profile = build_feature_profile(reference, FEATURE_COLUMNS)
    current_profile = build_feature_profile(current, FEATURE_COLUMNS)
    drift = compute_feature_drift(reference, current, FEATURE_COLUMNS)
    reference_profile.to_csv(OUT_DIR / "reference_feature_profile.csv", index=False)
    current_profile.to_csv(OUT_DIR / "current_feature_profile.csv", index=False)
    drift.to_csv(OUT_DIR / "feature_drift.csv", index=False)
    drift.to_parquet(OUT_DIR / "feature_drift.parquet", index=False)
    summary = summarize_drift(drift)
    (OUT_DIR / "feature_drift_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
