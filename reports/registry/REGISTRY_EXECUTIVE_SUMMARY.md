# Registry Executive Summary v0.8

## Estado

- Estado registry: ok
- Champion actual: `riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02`
- Modelos registrados: 3
- Datasets registrados: 1
- Data modes: crm

## Decisión ejecutiva

El sistema queda preparado para operar bajo una lógica de sucesión: el modelo champion puede ser retado por challengers y reemplazado solo bajo criterios de performance, drift, feedback y política de retraining.

## Archivos clave

- `models/registry/model_registry.json`
- `models/registry/dataset_registry.json`
- `models/registry/experiment_history.parquet`
- `reports/registry/champion_vs_challenger_report.md`
- `reports/registry/retraining_decision_report.md`
- `reports/congress/MODEL_OVERVIEW_CONGRESS.md`
