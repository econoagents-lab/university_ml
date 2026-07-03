from __future__ import annotations

from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.mlu.experiments import analyze_intervention_effect

FEEDBACK_PATH = Path("data/feedback/feedback_outcomes_merged.parquet")
OUT_DIR = Path("reports/experiments")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if FEEDBACK_PATH.exists():
        feedback = pd.read_parquet(FEEDBACK_PATH)
    else:
        feedback = pd.DataFrame()
    result = analyze_intervention_effect(feedback)
    (OUT_DIR / "intervention_effect_report.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md = "# Intervention Effect Report - Riesgo de Caída v0.7\n\n"
    md += f"Estado: {result.get('status')}\n\n"
    md += result.get("message", "Análisis generado.") + "\n"
    (OUT_DIR / "intervention_effect_report.md").write_text(md, encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
