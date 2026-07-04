# Experiment Power & Policy Engine · v1.9

## Escena ejecutiva
Yo convierto el experimento de riesgo de caída en política comercial: poder estadístico, cumplimiento, segmentos, SLA, capacidad y escalamiento.

## Power analysis
- MDE objetivo: **5.0 pp**
- N requerido por brazo: **800**
- N observado mínimo por brazo: **68**
- Efecto detectable con muestra actual: **0.28 pp**
- Decisión: **seguir_acumulando_muestra_y_feedback**

## Compliance de tratamiento
| metric                     |   value |   target | direction   | status   | decision_use                                                      |
|:---------------------------|--------:|---------:|:------------|:---------|:------------------------------------------------------------------|
| treatment_contact_rate     |       0 |      0.8 | >=          | warning  | si falla, no culpo al modelo; primero corrijo ejecución comercial |
| p0_treatment_coverage      |       0 |      1   | >=          | warning  | si falla, no culpo al modelo; primero corrijo ejecución comercial |
| control_contamination_rate |       0 |      0.1 | <=          | ok       | si falla, no culpo al modelo; primero corrijo ejecución comercial |
| feedback_completion_30d    |       0 |      0.6 | >=          | warning  | si falla, no culpo al modelo; primero corrijo ejecución comercial |
| treatment_rows             |     153 |      1   | >=          | ok       | muestra operacional                                               |
| control_rows               |      68 |      1   | >=          | ok       | contrafactual operativo                                           |

## SLA y capacidad
- Estado: **capacity_warning**
- Capacidad diaria actual: **30**
- Capacidad diaria recomendada: **74**
- P0: **0** con SLA **4h**
- P1: **221** con SLA **24h**
- Días estimados para limpiar P0/P1: **19**
- Recomendación: **aumentar_capacidad_o_subir_umbral_p0**

## Política de escalamiento
- Decisión ejecutiva: **corregir_cumplimiento_antes_de_escalar**
- P0: tratamiento obligatorio, SLA corto, sin holdout.
- P1: tratamiento/control permitido de forma controlada, SLA 24h.
- P2: monitoreo y escalamiento si sube el riesgo.

## Top segmentos por valor salvado proxy
| dimension   | segment             |   treatment_n |   control_n | sample_ready   |   treatment_negative_rate_30d |   control_negative_rate_30d |   negative_reduction_pp |   positive_uplift_pp |   valor_en_riesgo_segmento |   valor_salvado_proxy | policy_signal           |
|:------------|:--------------------|--------------:|------------:|:---------------|------------------------------:|----------------------------:|------------------------:|---------------------:|---------------------------:|----------------------:|:------------------------|
| proyecto    | Tizón y Bueno       |            25 |          22 | True           |                             0 |                           0 |                       0 |                    0 |                2.73299e+06 |                     0 | no_escalar_aun          |
| proyecto    | Modena              |            15 |           7 | True           |                             0 |                           0 |                       0 |                    0 |                1.672e+06   |                     0 | no_escalar_aun          |
| proyecto    | Torre Nápoles       |            24 |           7 | True           |                             0 |                           0 |                       0 |                    0 |                1.21118e+06 |                     0 | no_escalar_aun          |
| proyecto    | Sialia              |            24 |           8 | True           |                             0 |                           0 |                       0 |                    0 |                1.49859e+06 |                     0 | no_escalar_aun          |
| proyecto    | Fenix               |             7 |           2 | False          |                             0 |                           0 |                       0 |                    0 |                1.36747e+06 |                     0 | recolectar_mas_feedback |
| proyecto    | Edificio Urbanzen   |            18 |           6 | True           |                             0 |                           0 |                       0 |                    0 |                1.7461e+06  |                     0 | no_escalar_aun          |
| proyecto    | Alicanto            |            10 |           5 | True           |                             0 |                           0 |                       0 |                    0 |                1.16817e+06 |                     0 | no_escalar_aun          |
| proyecto    | Capadocia           |            13 |           4 | False          |                             0 |                           0 |                       0 |                    0 |                1.34541e+06 |                     0 | recolectar_mas_feedback |
| proyecto    | Matera              |             2 |           0 | False          |                             0 |                           0 |                       0 |                    0 |           894398           |                     0 | recolectar_mas_feedback |
| proyecto    | Edificio Mariategui |             7 |           6 | True           |                             0 |                           0 |                       0 |                    0 |                1.04343e+06 |                     0 | no_escalar_aun          |

## Interpretación económica
Si el experimento aún no tiene poder, la fábrica no debe prometer causalidad. Debe operar política MVP, medir cumplimiento, completar feedback 7d/30d y recién escalar reglas por segmento.

## Privacidad
Validación de privacidad: **ok**. No publico clientes, documentos, teléfonos, emails, direcciones ni credenciales.

## Próxima acción
Yo usaría esta política para definir capacidad diaria, SLA por prioridad y qué segmentos merecen intervención reforzada en la próxima reunión comercial.