# Model Registry Metadata

Estado: **ok**

Champion actual: `riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02`

Modelos registrados: 3

Datasets registrados: 1

## Payload API

```json
{
  "status": "ok",
  "project": "riesgo_caida",
  "current_champion": "riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02",
  "champion": {
    "model_id": "riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02",
    "project": "riesgo_caida",
    "algorithm": "random_forest",
    "status": "champion",
    "dataset_version": "dataset_riesgo_caida_crm_2026_07_03_v001",
    "registered_at": "2026-07-03T16:53:38+00:00",
    "artifact_path": "models/artifacts/riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02.joblib",
    "artifact_sha256": "527aec15e99cb1327f519d1389cd8e014abe7add3b84c2b66d613a5ab3018160",
    "model_card_path": "models/cards/model_card_riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02.md",
    "metrics": {
      "roc_auc": 0.5235642315343437,
      "average_precision": 0.11622117236398827,
      "threshold": 0.4,
      "precision": 0.09090909090909091,
      "recall": 0.961038961038961,
      "f1": 0.16610549943883277,
      "tn": 63,
      "fp": 740,
      "fn": 3,
      "tp": 74,
      "base_event_rate": 0.0875,
      "top_decile_event_rate": 0.06818181818181818,
      "top_decile_lift": 0.7792207792207793,
      "train_rows": 2638,
      "test_rows": 880,
      "dataset_version": "dataset_riesgo_caida_crm_2026_07_03_v001",
      "data_mode": "crm"
    },
    "notes": "trained_from_crm_model_ready_dataset",
    "champion_since": "2026-07-03T16:53:52+00:00",
    "promotion_reason": "v0.8_policy_or_manual_promotion"
  },
  "n_registered_models": 3,
  "latest_dataset": "dataset_riesgo_caida_crm_2026_07_03_v001",
  "n_dataset_versions": 1,
  "data_modes": [
    "crm"
  ],
  "registry_paths": {
    "model_registry": "models/registry/model_registry.json",
    "dataset_registry": "models/registry/dataset_registry.json",
    "experiment_history": "models/registry/experiment_history.parquet"
  }
}
```
