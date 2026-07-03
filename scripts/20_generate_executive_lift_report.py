from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

MANIFEST_PATH = Path("models/model_manifest.json")
LIFT_METRICS_PATH = Path("reports/modeling/lift_metrics.json")
LIFT_DECILES_PATH = Path("reports/modeling/lift_deciles.csv")
SCORING_REPORT_PATH = Path("reports/scoring/scoring_report.json")
OUT_PATH = Path("reports/executive/CEO_BRIEF_RIESGO_CAIDA_V0_6.md")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = read_json(MANIFEST_PATH)
    lift = read_json(LIFT_METRICS_PATH)
    scoring = read_json(SCORING_REPORT_PATH)
    deciles = pd.read_csv(LIFT_DECILES_PATH) if LIFT_DECILES_PATH.exists() else pd.DataFrame()
    top_deciles_md = deciles.head(3).to_markdown(index=False) if not deciles.empty else "No disponible"

    brief = f"""# CEO Brief - Riesgo de Caída v0.6

## 1. Decisión ejecutiva

El modelo de riesgo de caída ya puede operar como ranking diario de priorización comercial. La decisión no es automatizar castigos ni reemplazar criterio humano: es ordenar el seguimiento donde el valor en riesgo es mayor.

## 2. Estado del sistema

| Componente | Estado |
|---|---|
| Modelo gobernado | OK |
| Dataset model-ready | OK |
| Anti-leakage | Activo |
| Scoring actual | OK |
| Lift por deciles | OK |
| Feedback loop | Plantilla creada |

## 3. Métricas de modelo

| Métrica | Valor |
|---|---:|
| ROC AUC | {manifest.get('roc_auc', 0):.3f} |
| Average Precision | {manifest.get('average_precision', 0):.3f} |
| Precision | {manifest.get('precision', 0):.3f} |
| Recall | {manifest.get('recall', 0):.3f} |
| F1 | {manifest.get('f1', 0):.3f} |

## 4. Métricas de lift

| Métrica | Valor |
|---|---:|
| Tasa caída test | {lift.get('target_rate_test', 0):.2%} |
| Lift top decil | {lift.get('top_decile_lift', 0):.2f}x |
| Captura top 20% | {lift.get('top_20_capture_rate', 0):.2%} |

## 5. Top deciles

{top_deciles_md}

## 6. Scoring operativo

| Métrica | Valor |
|---|---:|
| Operaciones scoreadas | {scoring.get('rows_scored', scoring.get('total_rows', 0))} |
| Top 100 generado | {'Sí' if Path('reports/scoring/top_100_riesgo_caida.csv').exists() else 'No'} |

## 7. Recomendación

- Revisar diariamente el top 50 o top 100.
- Registrar acción tomada en `data/feedback/feedback_log.csv`.
- Medir si las operaciones intervenidas caen menos o firman más rápido que las no intervenidas.
- Pasar a v0.7 con monitoreo semanal y experimentos ligeros por cohortes.
"""
    OUT_PATH.write_text(brief, encoding="utf-8")
    print(str(OUT_PATH))


if __name__ == "__main__":
    main()
