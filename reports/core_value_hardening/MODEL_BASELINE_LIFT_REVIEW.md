# Model Baseline & Lift Review v2.7

## Veredicto técnico

- ROC AUC test: **0.517**
- Average precision test: **0.115**
- Lift top decile: **1.04x**
- Calibration gap medio: **0.42624710583107517**
- Claim recomendado: **modelo_apto_solo_como_ranking_debil_y_gobernado**

## Lectura ejecutiva

No se debe vender el modelo como oráculo de alta precisión. La promesa defendible es:

> Sistema de priorización, trazabilidad, feedback y aprendizaje operativo.

## Precision@K disponible

| K | Positivos | Precision@K | Capture rate |
|---:|---:|---:|---:|
| 10 | 2 | 0.200 | 0.026 |
| 20 | 2 | 0.100 | 0.026 |
| 50 | 5 | 0.100 | 0.065 |
| 100 | 10 | 0.100 | 0.130 |
| 200 | 15 | 0.075 | 0.195 |
| 880 | 77 | 0.087 | 1.000 |

## Acción recomendada

1. Comparar contra reglas simples: días en tubería, cuota inicial, caída histórica por proyecto, asesor/proyecto.
2. Medir lift@capacity: top 30, top 50 y top 100.
3. Recalibrar probabilidades antes de comunicar porcentajes como probabilidad real.
4. Usar el score como ranking hasta que el feedback real mejore evidencia.
