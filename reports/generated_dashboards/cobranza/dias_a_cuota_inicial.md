# Días a Cuota Inicial

**Familia:** `cobranza`  
**Owner:** Finanzas / Comercial  
**Audiencia:** Finanzas / Comercial  
**Prioridad:** professional  
**Estado:** cataloged

## Pregunta económica

¿Cuánto demora el cliente en comprometer caja?

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
| `metric_group` | cobranza |
| `status` | ok |
| `metric_mode` | official_or_real_mart |
| `operaciones_cobranza` | 4784 |
| `valor_venta_total` | 1835649695.74 |
| `monto_pagado_total` | 29843527.61 |
| `saldo_pendiente_total` | 173084323.73 |
| `avance_cobranza` | 0.016258 |
| `source_status` | ["ok"] |
| `decision` | Yo priorizo caja real: ventas con saldo pendiente y bajo avance de cobranza. |

## Acción recomendada

Priorizar saldos pendientes y pagos no asignados para proteger caja y trazabilidad financiera.

## Donde cambiar

`config/dashboard_params.yml#cuota_inicial_timing`

## Parámetros actuales usados como contexto

```yaml
warning_days: 7
critical_days: 14

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
