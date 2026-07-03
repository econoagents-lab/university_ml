# CEO Brief - Riesgo de Caída v0.6

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
| ROC AUC | 0.499 |
| Average Precision | 0.112 |
| Precision | 0.095 |
| Recall | 0.844 |
| F1 | 0.171 |

## 4. Métricas de lift

| Métrica | Valor |
|---|---:|
| Tasa caída test | 8.75% |
| Lift top decil | 1.17x |
| Captura top 20% | 18.18% |

## 5. Top deciles

|   decile |   rows |   positives |   avg_score |   min_score |   max_score |   valor_total |   valor_caidas |   event_rate |   baseline_rate |     lift |   capture_rate |   cum_rows |   cum_positives |   cum_capture_rate |   cum_population_rate |   cum_lift |
|---------:|-------:|------------:|------------:|------------:|------------:|--------------:|---------------:|-------------:|----------------:|---------:|---------------:|-----------:|----------------:|-------------------:|----------------------:|-----------:|
|        1 |     88 |           9 |    0.636131 |    0.619596 |    0.701942 |   3.21397e+07 |    3.7347e+06  |    0.102273  |          0.0875 | 1.16883  |      0.116883  |         88 |               9 |           0.116883 |                   0.1 |   1.16883  |
|        2 |     88 |           5 |    0.608556 |    0.598772 |    0.619482 |   3.3301e+07  |    2.06372e+06 |    0.0568182 |          0.0875 | 0.649351 |      0.0649351 |        176 |              14 |           0.181818 |                   0.2 |   0.909091 |
|        3 |     88 |           6 |    0.587852 |    0.577049 |    0.598388 |   3.84206e+07 |    2.08689e+06 |    0.0681818 |          0.0875 | 0.779221 |      0.0779221 |        264 |              20 |           0.25974  |                   0.3 |   0.865801 |

## 6. Scoring operativo

| Métrica | Valor |
|---|---:|
| Operaciones scoreadas | 0 |
| Top 100 generado | Sí |

## 7. Recomendación

- Revisar diariamente el top 50 o top 100.
- Registrar acción tomada en `data/feedback/feedback_log.csv`.
- Medir si las operaciones intervenidas caen menos o firman más rápido que las no intervenidas.
- Pasar a v0.7 con monitoreo semanal y experimentos ligeros por cohortes.
