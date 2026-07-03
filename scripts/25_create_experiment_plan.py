from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.mlu.experiments import create_experiment_assignments

RANKING_PATH = Path("data/processed/scoring/ranking_operaciones_riesgo_caida.parquet")
OUT_DIR = Path("data/experiments")
REPORT_DIR = Path("reports/experiments")


def main() -> None:
    if not RANKING_PATH.exists():
        raise FileNotFoundError(f"No existe ranking operativo: {RANKING_PATH}. Ejecuta scripts/14_score_actual_riesgo_caida.py")
    ranking = pd.read_parquet(RANKING_PATH)
    assignments = create_experiment_assignments(ranking, top_n=min(100, len(ranking)), holdout_rate=0.20, random_state=42)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    assignments.to_parquet(OUT_DIR / "riesgo_caida_experiment_assignments.parquet", index=False)
    assignments.to_csv(OUT_DIR / "riesgo_caida_experiment_assignments.csv", index=False, encoding="utf-8-sig")
    summary = {
        "rows": int(len(assignments)),
        "groups": {str(k): int(v) for k, v in assignments["experiment_group"].value_counts().to_dict().items()},
        "holdout_rate": 0.20,
        "output": str(OUT_DIR / "riesgo_caida_experiment_assignments.parquet"),
    }
    (REPORT_DIR / "experiment_plan_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    md = "# Experiment Plan - Riesgo de Caída v0.7\n\n"
    md += "## Decisión\n\nMedir si el seguimiento priorizado reduce caídas sin negar seguimiento comercial estándar.\n\n"
    md += f"- Operaciones: {summary['rows']}\n- Grupos: {summary['groups']}\n"
    (REPORT_DIR / "experiment_plan.md").write_text(md, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
