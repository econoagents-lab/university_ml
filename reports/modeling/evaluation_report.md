# Evaluation Report - Riesgo de Caída v0.5 Official Rules

## Lectura ejecutiva

Modelo gobernado de riesgo de caída entrenado sobre dataset model-ready sin columnas prohibidas.

## Dataset

| Métrica | Valor |
|---|---:|
| Filas totales | 3,518 |
| Filas entrenamiento | 2,638 |
| Filas prueba | 880 |
| Tasa histórica de caída 30d | 7.28% |

## Métricas

| Métrica | Valor |
|---|---:|
| ROC AUC | 0.499 |
| Average Precision | 0.112 |
| Threshold recomendado | 0.50 |
| Precision | 0.095 |
| Recall | 0.844 |
| F1 | 0.171 |

## Confusion Matrix

| Real / Predicho | Predice No Caída | Predice Caída |
|---|---:|---:|
| Real No Caída | 185 | 618 |
| Real Caída | 12 | 65 |

## Lectura económica

- El evento es minoritario; no usar accuracy como métrica principal.
- El falso negativo es el error más caro: una caída no priorizada.
- El ranking operativo debe ordenar por valor esperado en riesgo.

## Anti-leakage

Si `fecha_caida` o cualquier columna prohibida entra a X, el entrenamiento falla.
