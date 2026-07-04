# Decision Action Feedback Lab · v1.7

## Escena ejecutiva
Yo cierro el ciclo entre alerta, acción, responsable, resultado y aprendizaje.

## Cola de decisión
- Operaciones en cola segura: **763**
- P0: **0**
- P1: **221**
- Valor esperado en riesgo: **S/ 21,232,580.48**

## Feedback registrado
- Eventos seguros de feedback: **100**
- Filas de outcome: **3**

## Resultado por prioridad
| prioridad   |   feedback_events |   positive_30d |   negative_30d |   pending_30d |   avg_risk |    value_at_risk |   positive_rate_30d |   negative_rate_30d |
|:------------|------------------:|---------------:|---------------:|--------------:|-----------:|-----------------:|--------------------:|--------------------:|
| P1          |                89 |              0 |              0 |            89 |   0.574525 |      4.80386e+06 |                   0 |                   0 |
| P2          |                 8 |              0 |              0 |             8 |   0.47606  | 359514           |                   0 |                   0 |
| P3          |                 3 |              0 |              0 |             3 |   0.315623 | 133876           |                   0 |                   0 |

## Señal de aprendizaje
- Recomendación: **continuar_recolectando_feedback**
- Reentrenar o recalibrar: **False**
- Razones: **sin_alertas**

## Privacidad
No exporto clientes, DNI, teléfonos, emails, direcciones, códigos de proforma/unidad ni credenciales. Uso `operation_id` y `asesor_id` hasheados.

## Próxima acción
Yo usaría `action_assignment_template.csv` en la reunión comercial, completaría `accion_tomada`, `resultado_7d` y `resultado_30d`, y volvería a correr el pipeline.