# Calibration Dashboard

**Familia:** `modeling`  
**Owner:** MLOps / Data Science  
**Audiencia:** Data Science  
**Prioridad:** professional  
**Estado:** cataloged

## Pregunta económica

¿Las probabilidades son creíbles?

## KPIs agregados disponibles

- Total operaciones: **763**
- Valor total en riesgo: **S/ 21,232,580.48**
- Riesgo promedio: **0.398**
- Operaciones P0/P1: **{'operaciones': 761, 'valor_en_riesgo': 21191194.15}**
- Data mode: **crm**
- Fecha generación KPI: **2026-07-04T20:23:55**

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

Usar el tablero para convertir datos en decisión, responsable, plazo y métrica de resultado.

## Donde cambiar

`config/model_params.yml#calibration`

## Parámetros actuales usados como contexto

```yaml
bins: 10
min_reliability_threshold: 0.05

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
