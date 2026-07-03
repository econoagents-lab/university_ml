from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.mlu.feedback import build_feedback_template, save_feedback_template, validate_feedback_log

RANKING_PATH = Path("data/processed/scoring/ranking_operaciones_riesgo_caida.parquet")
OUT_DIR = Path("data/feedback")
REPORT_DIR = Path("reports/feedback")


def main(top_n: int = 100) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ranking = pd.read_parquet(RANKING_PATH)
    template = build_feedback_template(ranking, top_n=top_n)
    save_feedback_template(template, OUT_DIR)
    validation = validate_feedback_log(template)
    (REPORT_DIR / "feedback_template_validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
    report = f"""# Feedback Loop Template - Riesgo de Caída v0.6

## Resultado

Se generó una plantilla de feedback para el top {top_n} de operaciones priorizadas.

## Archivos

- `data/feedback/feedback_log_template.csv`
- `data/feedback/feedback_log_template.parquet`

## Cómo usarlo

1. Abrir el CSV.
2. Completar `accion_tomada`, `fecha_accion`, `resultado_7d`, `resultado_30d`, `caida_real_30d` y `comentario`.
3. Guardar una copia como `data/feedback/feedback_log.csv`.
4. Ejecutar `python scripts/19_merge_feedback_outcomes.py`.

## Validación

```json
{json.dumps(validation, indent=2, ensure_ascii=False)}
```
"""
    (REPORT_DIR / "feedback_loop_report.md").write_text(report, encoding="utf-8")
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
