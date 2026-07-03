from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.mlu.feedback import merge_feedback_with_ranking, validate_feedback_log

RANKING_PATH = Path("data/processed/scoring/ranking_operaciones_riesgo_caida.parquet")
FEEDBACK_PATH = Path("data/feedback/feedback_log.csv")
TEMPLATE_PATH = Path("data/feedback/feedback_log_template.csv")
OUT_PATH = Path("data/feedback/feedback_outcomes_merged.parquet")
REPORT_PATH = Path("reports/feedback/feedback_merge_report.md")


def main() -> None:
    if FEEDBACK_PATH.exists():
        feedback = pd.read_csv(FEEDBACK_PATH)
        source = str(FEEDBACK_PATH)
    elif TEMPLATE_PATH.exists():
        feedback = pd.read_csv(TEMPLATE_PATH)
        source = str(TEMPLATE_PATH)
    else:
        raise FileNotFoundError("No existe feedback_log.csv ni feedback_log_template.csv. Ejecuta primero scripts/18_initialize_feedback_loop.py")

    ranking = pd.read_parquet(RANKING_PATH)
    validation = validate_feedback_log(feedback)
    merged = merge_feedback_with_ranking(feedback, ranking)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(OUT_PATH, index=False)
    action_counts = feedback.get("accion_tomada", pd.Series(dtype=str)).value_counts(dropna=False).to_dict()
    outcome_counts = feedback.get("resultado_30d", pd.Series(dtype=str)).value_counts(dropna=False).to_dict()
    summary = {
        "source": source,
        "rows_feedback": int(len(feedback)),
        "rows_merged": int(len(merged)),
        "validation": validation,
        "action_counts": {str(k): int(v) for k, v in action_counts.items()},
        "resultado_30d_counts": {str(k): int(v) for k, v in outcome_counts.items()},
    }
    report = f"""# Feedback Merge Report - Riesgo de Caída v0.6

## Fuente

`{source}`

## Resultado

- Filas feedback: {summary['rows_feedback']}
- Filas merged: {summary['rows_merged']}
- Output: `data/feedback/feedback_outcomes_merged.parquet`

## Validación

```json
{json.dumps(validation, indent=2, ensure_ascii=False)}
```

## Acciones registradas

```json
{json.dumps(summary['action_counts'], indent=2, ensure_ascii=False)}
```

## Resultados 30d registrados

```json
{json.dumps(summary['resultado_30d_counts'], indent=2, ensure_ascii=False)}
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
