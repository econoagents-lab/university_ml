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
| ROC AUC | 0.517 |
| Average Precision | 0.115 |
| Precision | 0.090 |
| Recall | 0.961 |
| F1 | 0.165 |

## 4. Métricas de lift

| Métrica | Valor |
|---|---:|
| Tasa caída test | 8.75% |
| Lift top decil | 1.04x |
| Captura top 20% | 18.18% |

## 5. Top deciles

|   decile |   rows |   positives |   avg_score |   min_score |   max_score |   valor_total |   valor_caidas |   event_rate |   baseline_rate |     lift |   capture_rate |   cum_rows |   cum_positives |   cum_capture_rate |   cum_population_rate |   cum_lift |
|---------:|-------:|------------:|------------:|------------:|------------:|--------------:|---------------:|-------------:|----------------:|---------:|---------------:|-----------:|----------------:|-------------------:|----------------------:|-----------:|
|        1 |     88 |           8 |    0.618396 |    0.597986 |    0.689645 |   3.22838e+07 |    3.5147e+06  |    0.0909091 |          0.0875 | 1.03896  |      0.103896  |         88 |               8 |           0.103896 |                   0.1 |   1.03896  |
|        2 |     88 |           6 |    0.585513 |    0.57403  |    0.597967 |   3.33609e+07 |    2.00172e+06 |    0.0681818 |          0.0875 | 0.779221 |      0.0779221 |        176 |              14 |           0.181818 |                   0.2 |   0.909091 |
|        3 |     88 |           8 |    0.561028 |    0.549383 |    0.573909 |   3.7561e+07  |    2.69226e+06 |    0.0909091 |          0.0875 | 1.03896  |      0.103896  |        264 |              22 |           0.285714 |                   0.3 |   0.952381 |

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
