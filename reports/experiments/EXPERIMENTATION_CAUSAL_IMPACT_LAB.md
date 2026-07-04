# Experimentation Causal Impact Lab · v1.8

## Escena ejecutiva
Yo convierto la cola de riesgo en un experimento operativo: tratamiento, control, resultado y aprendizaje económico.

## Diseño experimental
- Experimento: **riesgo_caida_action_impact_v1**
- Unidad de análisis: **operation_id**
- Método de asignación: **deterministic_hash_stratified**
- Métrica principal: **negative_rate_30d**
- Nota de confianza: MVP descriptivo; no causal definitivo sin aleatorización operativa y muestra suficiente.

## Asignación
- Filas asignadas: **500**
- Brazos: **{'not_eligible': 279, 'treatment': 153, 'control': 68}**
- P0 en tratamiento obligatorio: **0**

## Impacto estimado
- Estado: **needs_more_feedback**
- Tratamiento n: **153**
- Control n: **68**
- Uplift positivo 30d: **0.0 pp**
- Reducción caída/pérdida 30d: **0.0 pp**
- Valor salvado proxy: **S/ 0.00**
- Recomendación: **seguir_recolectando_feedback**

## Tabla de resumen
| experiment_arm   |   n |   positive_30d |   negative_30d |   pending_30d |   positive_rate_30d |   negative_rate_30d |   pending_rate_30d |   contact_rate |   valor_esperado_en_riesgo |
|:-----------------|----:|---------------:|---------------:|--------------:|--------------------:|--------------------:|-------------------:|---------------:|---------------------------:|
| treatment        | 153 |              0 |              0 |           153 |                   0 |                   0 |                  1 |              0 |                5.97742e+06 |
| control          |  68 |              0 |              0 |            68 |                   0 |                   0 |                  1 |              0 |                2.68391e+06 |
| impact_delta     | 221 |              0 |              0 |           221 |                   0 |                   0 |                  0 |              0 |                0           |

## Interpretación económica
Si tratamiento reduce la tasa negativa frente a control, el sistema puede estimar valor salvado. Si no hay muestra suficiente, la decisión correcta no es inventar impacto: es seguir capturando feedback.

## Privacidad
No exporto clientes, DNI, teléfonos, emails, direcciones, códigos de proforma/unidad ni credenciales. Trabajo con `operation_id` y `asesor_id` seguros.

## Próxima acción
Yo ejecutaría el experimento por cohortes semanales, completaría resultados 7d/30d y recién después movería presupuesto, SLA o política de intervención.