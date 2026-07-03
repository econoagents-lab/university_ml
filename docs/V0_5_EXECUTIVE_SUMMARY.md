# Executive Summary v0.5

La Universidad ya tiene un modelo gobernado de riesgo de caída con reglas oficiales draft, dataset model-ready, anti-leakage duro, evaluación, model card, scoring actual y ranking comercial.

## Métricas

- ROC AUC: 0.517
- Average Precision: 0.115
- Recall: 0.961
- Precision: 0.090
- F1: 0.165
- Threshold recomendado: 0.40

## Artefactos

- `data/processed/gold/riesgo_caida_training_model_ready.parquet`
- `reports/modeling/evaluation_report.md`
- `models/model_card.md`
- `data/processed/scoring/ranking_operaciones_riesgo_caida.csv`
- `api/main.py` con batch endpoint
