# Model Registry

**Familia:** `registry`  
**Owner:** MLOps  
**Audiencia:** Data Science / Tecnología  
**Prioridad:** professional  
**Estado:** cataloged

## Pregunta económica

¿Qué modelo está vivo y con qué datos aprendió?

## KPIs agregados disponibles

- Total operaciones: **763**
- Valor total en riesgo: **S/ 21,232,580.48**
- Riesgo promedio: **0.398**
- Operaciones P0/P1: **{'operaciones': 761, 'valor_en_riesgo': 21191194.15}**
- Data mode: **crm**
- Fecha generación KPI: **2026-07-04T04:23:08**

## Top proyectos agregados

| proyecto | operaciones | valor_en_riesgo | riesgo_promedio | p0_p1 |
| --- | --- | --- | --- | --- |
| Tizón y Bueno | 82 | 2769922.88 | 0.5073 | 82 |
| Edificio Cuba Connect | 83 | 1986299.7 | 0.2822 | 83 |
| Edificio Urbanzen | 45 | 1783878.84 | 0.4903 | 45 |
| Edificio Santa Cruz Infinite | 84 | 1772295.82 | 0.2639 | 84 |
| Modena | 53 | 1672002.71 | 0.4932 | 53 |

## Top asesores agregados

| asesor_anon | operaciones | valor_en_riesgo | riesgo_promedio | p0_p1 |
| --- | --- | --- | --- | --- |
| Asesor_26DEBB0E | 130 | 4395201.77 | 0.4635 | 130 |
| Asesor_10B2BE3F | 216 | 3678489.2 | 0.2044 | 216 |
| Asesor_C931A67B | 66 | 2219467.94 | 0.4375 | 65 |
| Asesor_1F3B24E1 | 58 | 1961023.49 | 0.5103 | 58 |
| Asesor_B56EAA59 | 58 | 1892075.93 | 0.5045 | 58 |

## Top canales agregados

| canal | operaciones | valor_en_riesgo | riesgo_promedio | p0_p1 |
| --- | --- | --- | --- | --- |
| sin_clasificar | 763 | 21232580.48 | 0.3982 | 761 |

## Métricas específicas de esta familia

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

## Acción recomendada

Revisar estado del champion, drift, lift y política de retraining antes de confiar en el ranking.

## Donde cambiar

`models/registry/model_registry.json`

## Parámetros actuales usados como contexto

```yaml
project: riesgo_caida
current_champion: riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02
models:
- model_id: riesgo_caida_logistic_regression_dataset_riesgo_caida_crm_2026_07_03_v001_c01
  project: riesgo_caida
  algorithm: logistic_regression
  status: challenger
  dataset_version: dataset_riesgo_caida_crm_2026_07_03_v001
  registered_at: '2026-07-03T16:53:37+00:00'
  artifact_path: models/artifacts/riesgo_caida_logistic_regression_dataset_riesgo_caida_crm_2026_07_03_v001_c01.joblib
  artifact_sha256: 3f5190aa23c79c8b5761f37176c970c4a1047dd55decf74a8ae1bae2f1459708
  model_card_path: models/cards/model_card_riesgo_caida_logistic_regression_dataset_riesgo_caida_crm_2026_07_03_v001_c01.md
  metrics:
    roc_auc: 0.5178793808930795
    average_precision: 0.09596477580853703
    threshold: 0.4
    precision: 0.09574468085106383
    recall: 0.8181818181818182
    f1: 0.17142857142857143
    tn: 208
    fp: 595
    fn: 14
    tp: 63
    base_event_rate: 0.0875
    top_decile_event_rate: 0.07954545454545454
    top_decile_lift: 0.9090909090909092
    train_rows: 2638
    test_rows: 880
    dataset_version: dataset_riesgo_caida_crm_2026_07_03_v001
    data_mode: crm
  notes: trained_from_crm_model_ready_dataset
- model_id: riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02
  project: riesgo_caida
  algorithm: random_forest
  status: champion
  dataset_version: dataset_riesgo_caida_crm_2026_07_03_v001
  registered_at: '2026-07-03T16:53:38+00:00'
  artifact_path: models/artifacts/riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02.joblib
  artifact_sha256: 527aec15e99cb1327f519d1389cd8e014abe7add3b84c2b66d613a5ab3018160
  model_card_path: models/cards/model_card_riesgo_caida_random_forest_dataset_riesgo_caida_crm_2026_07_03_v001_c02.md
  metrics:
    roc_auc: 0.5235642315343437
    average_precision: 0.11622117236398827
    threshold: 0.4
    precision: 0.09090909090909091
    recall: 0.961038961038961
    f1: 0.16610549943883277
    tn: 63
    fp: 740
    fn: 3
    tp: 74
    base_event_rate: 0.0875
    top_decile_event_rate: 0.06818181818181818
    top_decile_lift: 0.7792207792207793
    train_rows: 2638
    test_rows: 880
    dataset_version: dataset_riesgo_caida_crm_2026_07_03_v001
    data_mode: crm
  notes: trained_from_crm_model_ready_dataset
  champion_since: '2026-07-03T16:53:52+00:00'
  promotion_reason: v0.8_policy_or_manual_promotion
- model_id: riesgo_caida_gradient_boosting_dataset_riesgo_caida_crm_2026_07_03_v001_c03
  project: riesgo_caida
  algorithm: gradient_boosting
  status: challenger
  dataset_version: dataset_riesgo_caida_crm_2026_07_03_v001
  registered_at: '2026-07-03T16:53:39+00:00'
  artifact_path: models/artifacts/riesgo_caida_gradient_boosting_dataset_riesgo_caida_crm_2026_07_03_v001_c03.joblib
  artifact_sha256: 227049d7960a6aae04054572aaaf7661e5c9d2c41d62c8b2e5978e349e2050e5
  model_card_path: models/cards/model_card_riesgo_caida_gradient_boosting_dataset_riesg
```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
