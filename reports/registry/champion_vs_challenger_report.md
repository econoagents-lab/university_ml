# Champion vs Challengers

| model_id                                                                          | algorithm           | status     | dataset_version                              |   roc_auc |   average_precision |   precision |   recall |        f1 |   top_decile_lift |   promotion_score |
|:----------------------------------------------------------------------------------|:--------------------|:-----------|:---------------------------------------------|----------:|--------------------:|------------:|---------:|----------:|------------------:|------------------:|
| riesgo_caida_random_forest_dataset_riesgo_caida_sperant_2026_07_04_v002_c02       | random_forest       | challenger | dataset_riesgo_caida_sperant_2026_07_04_v002 |  0.51458  |           0.117345  |   0.0883392 | 0.974026 | 0.161987  |          1.16883  |          0.466769 |
| riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02           | random_forest       | champion   | dataset_riesgo_caida_crm_2026_07_03_v001     |  0.523564 |           0.116221  |   0.0909091 | 0.961039 | 0.166105  |          0.779221 |          0.44108  |
| riesgo_caida_logistic_regression_dataset_riesgo_caida_crm_2026_07_03_v001_c01     | logistic_regression | challenger | dataset_riesgo_caida_crm_2026_07_03_v001     |  0.517879 |           0.0959648 |   0.0957447 | 0.818182 | 0.171429  |          0.909091 |          0.415942 |
| riesgo_caida_logistic_regression_dataset_riesgo_caida_sperant_2026_07_04_v002_c01 | logistic_regression | challenger | dataset_riesgo_caida_sperant_2026_07_04_v002 |  0.517604 |           0.0959265 |   0.0957447 | 0.818182 | 0.171429  |          0.909091 |          0.415852 |
| riesgo_caida_gradient_boosting_dataset_riesgo_caida_crm_2026_07_03_v001_c03       | gradient_boosting   | challenger | dataset_riesgo_caida_crm_2026_07_03_v001     |  0.496984 |           0.0943967 |   0.133333  | 0.025974 | 0.0434783 |          0.909091 |          0.238123 |
| riesgo_caida_gradient_boosting_dataset_riesgo_caida_sperant_2026_07_04_v002_c03   | gradient_boosting   | challenger | dataset_riesgo_caida_sperant_2026_07_04_v002 |  0.496984 |           0.0943967 |   0.133333  | 0.025974 | 0.0434783 |          0.909091 |          0.238123 |

## Lectura ejecutiva

Mejor candidato por promotion_score: `riesgo_caida_random_forest_dataset_riesgo_caida_sperant_2026_07_04_v002_c02`.
