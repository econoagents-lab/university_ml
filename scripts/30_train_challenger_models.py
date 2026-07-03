from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import os
from pathlib import Path

from src.mlu.registry import load_dataset_registry, register_dataset_version
from src.mlu.comparison import train_challenger_models


def main() -> None:
    data_mode = os.getenv("MLU_DATA_MODE", "crm").strip().lower()
    dataset_path = Path("data/processed/gold/riesgo_caida_training_model_ready.parquet")
    registry = load_dataset_registry()
    dataset_version = registry.get("latest_dataset")
    if not dataset_version:
        entry = register_dataset_version(dataset_path, data_mode=data_mode)
        dataset_version = entry["dataset_version"]
    results = train_challenger_models(dataset_path, dataset_version=dataset_version, data_mode=data_mode)
    Path("reports/registry").mkdir(parents=True, exist_ok=True)
    Path("reports/registry/challenger_training_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
