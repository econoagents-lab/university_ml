from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.mlu.business_rules import build_gold_riesgo_caida_from_processes, summarize_inferred_rules
from src.mlu.config import RAW_SPERANT_DIR, GOLD_DIR, REPORTS_DIR
from src.mlu.foundations import audit_training_dataset, build_model_matrix


def find_processes_path() -> Path:
    candidates = [
        RAW_SPERANT_DIR / "procesos.parquet",
        PROJECT_ROOT / "data" / "raw" / "procesos.parquet",
        PROJECT_ROOT / "data" / "sample" / "procesos.parquet",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No encontré procesos.parquet. Copia tu parquet a data/raw/sperant/procesos.parquet "
        "o ejecuta scripts/00_extract_redshift_to_parquet.py."
    )


def main() -> None:
    source_path = find_processes_path()
    procesos = pd.read_parquet(source_path)

    summary = summarize_inferred_rules(procesos)
    gold = build_gold_riesgo_caida_from_processes(procesos, snapshot_days=(7, 14, 30), horizon_days=30)

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GOLD_DIR / "riesgo_caida_training_inferred.parquet"
    gold.to_parquet(out_path, index=False)

    audit = audit_training_dataset(gold)
    if audit["ready_for_training"]:
        x = build_model_matrix(gold)
        audit["model_matrix_columns"] = list(x.columns)
        audit["model_matrix_rows"] = int(len(x))

    report = {
        "source_path": str(source_path),
        "output_path": str(out_path),
        "rules_summary": summary,
        "gold_rows": int(len(gold)),
        "target_rate": float(gold["caida_30d"].mean()) if len(gold) else None,
        "foundation_audit": audit,
        "status": "draft_inferred_rules_review_required",
    }

    report_dir = REPORTS_DIR / "foundations"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "inferred_rules_build_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nGold generado en: {out_path}")
    print(f"Reporte guardado en: {report_path}")


if __name__ == "__main__":
    main()
