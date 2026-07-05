# Decision Action Feedback Lab

**Familia:** `action_feedback`  
**Owner:** Jefatura Comercial / BI  
**Audiencia:** Gerencia Comercial / Asesores / Data Science  
**Prioridad:** mvp  
**Estado:** cataloged

## Pregunta económica

¿Qué acción se tomó sobre cada alerta y qué resultado produjo a 7d/30d?

## KPIs agregados disponibles

- Total operaciones: **763**
- Valor total en riesgo: **S/ 21,232,580.48**
- Riesgo promedio: **0.398**
- Operaciones P0/P1: **{'operaciones': 761, 'valor_en_riesgo': 21191194.15}**
- Data mode: **crm**
- Fecha generación KPI: **2026-07-04T20:10:16**

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
| `metric_group` | action_feedback |
| `status` | ok |
| `queue_rows` | 763 |
| `p0_actions` | 0 |
| `p1_actions` | 221 |
| `feedback_events` | 100 |
| `outcome_rows` | 3 |
| `value_at_risk_in_queue` | 21232580.48 |
| `retraining_recommendation` | continuar_recolectando_feedback |
| `should_retrain_or_recalibrate` | False |
| `privacy_status` | ok |
| `decision` | Yo uso esta familia para medir si las alertas realmente se convierten en acciones, resultados y aprendizaje. |

## Acción recomendada

Usar el tablero para convertir datos en decisión, responsable, plazo y métrica de resultado.

## Donde cambiar

`config/decision_action_feedback_lab.yml#rules`

## Parámetros actuales usados como contexto

```yaml
priority_thresholds:
  p0: 0.7
  p1: 0.5
  p2: 0.35
sla_hours:
  p0: 0
  p1: 24
  p2: 72
  p3: 168
daily_capacity:
  max_p0_actions: 25
  max_total_actions: 80
default_owner_when_missing: OWNER_SIN_ASIGNAR
action_catalog:
  p0: Contactar hoy, validar financiamiento/cuota inicial y registrar resultado.
  p1: Contactar en 24h y confirmar siguiente hito de cierre.
  p2: Monitorear en 72h y actualizar estado comercial.
  p3: Seguimiento regular.
accepted_actions:
- pendiente
- llamado_realizado
- whatsapp_enviado
- cita_agendada
- financiamiento_validado
- cuota_inicial_pagada
- cambio_unidad_gestionado
- descuento_evaluado
- no_contactado
positive_outcomes:
- minuta
- sigue_activo
- cuota_inicial_pagada
- cita_agendada
- financiamiento_validado
negative_outcomes:
- caida
- no_contactado
- sin_respuesta
- desistio

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
