from __future__ import annotations

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import os
from pathlib import Path

from src.mlu.registry import register_dataset_version


def main() -> None:
    data_mode = os.getenv("MLU_DATA_MODE", "crm").strip().lower()
    dataset_path = Path("data/processed/gold/riesgo_caida_training_model_ready.parquet")
    if not dataset_path.exists():
        raise FileNotFoundError("Ejecuta primero scripts/15_prepare_model_ready_dataset.py")
    result = register_dataset_version(dataset_path, data_mode=data_mode)
    Path("reports/registry").mkdir(parents=True, exist_ok=True)
    Path("reports/registry/latest_dataset_version.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
