# Métricas familia: registry

| Métrica | Valor |
|---|---|
| `metric_group` | mlops |
| `status` | retrain_recommended |
| `champion_model_id` | riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02 |
| `champion_algorithm` | random_forest |
| `registered_models` | 3 |
| `prediction_psi` | 3.7125 |
| `drift_status` | fail |
| `feature_drift_fail_count` | 4 |
| `brier_score` | 0.2647 |
| `top_decile_lift` | 1.039 |
| `champion_recall` | 0.961 |
| `challengers_compared` | 3 |
| `retraining_reasons` | ["prediction_psi_fail", "low_lift"] |
| `decision` | Yo reviso drift, lift y challenger antes de confiar ciegamente en el ranking operativo. |
