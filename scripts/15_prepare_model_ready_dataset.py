from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.mlu.official_rules import save_model_ready_dataset

DEFAULT_INPUT = Path("data/processed/gold/riesgo_caida_training.parquet")
DEFAULT_OUTPUT = Path("data/processed/gold/riesgo_caida_training_model_ready.parquet")
DEFAULT_REPORT = Path("reports/modeling/model_ready_dataset_report.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye dataset model-ready sin columnas prohibidas.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    result = save_model_ready_dataset(args.input, args.output)
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
