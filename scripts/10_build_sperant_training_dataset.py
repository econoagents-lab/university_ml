from __future__ import annotations

from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from pathlib import Path

from src.mlu.config import RAW_SPERANT_DIR, SPERANT_TRAINING_PATH, SPERANT_SCORING_PATH
from src.mlu.sperant_adapter import build_riesgo_caida_training_dataset, build_current_scoring_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construye gold tables de riesgo de caída desde Sperant/Redshift.")
    parser.add_argument("--input-dir", default=str(RAW_SPERANT_DIR))
    parser.add_argument("--output", default=str(SPERANT_TRAINING_PATH))
    parser.add_argument("--scoring-output", default=str(SPERANT_SCORING_PATH))
    parser.add_argument("--unit-focus", default="departamentos", choices=["departamentos", "all"])
    parser.add_argument("--snapshot-days", nargs="+", type=int, default=[7, 14, 30])
    parser.add_argument("--as-of-date", default=None)
    args = parser.parse_args()

    training = build_riesgo_caida_training_dataset(
        input_dir=Path(args.input_dir),
        output_path=Path(args.output),
        unit_focus=args.unit_focus,
        snapshot_days=args.snapshot_days,
    )
    scoring = build_current_scoring_dataset(
        input_dir=Path(args.input_dir),
        output_path=Path(args.scoring_output),
        unit_focus=args.unit_focus,
        as_of_date=args.as_of_date,
    )
    print(f"OK: training gold -> {args.output} | rows={len(training)} | target_rate={training['caida_30d'].mean():.2%}")
    print(f"OK: scoring actual -> {args.scoring_output} | rows={len(scoring)}")
