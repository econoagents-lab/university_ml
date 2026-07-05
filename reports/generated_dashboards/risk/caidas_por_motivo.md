# Caídas por Motivo

**Familia:** `risk`  
**Owner:** Jefatura Comercial  
**Audiencia:** Comercial  
**Prioridad:** professional  
**Estado:** cataloged

## Pregunta económica

¿Por qué se pierden operaciones?

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
| `metric_group` | risk |
| `status` | ok |
| `total_operaciones` | 763 |
| `p0_intervenir_hoy` | 0 |
| `p1_24h` | 221 |
| `p2_72h` | 288 |
| `p0_p1_total` | 221 |
| `valor_total_en_riesgo` | 21232580.48 |
| `riesgo_promedio` | 0.3982 |
| `riesgo_p90` | 0.5631 |
| `sla` | {"p0_hours": 0, "p1_hours": 24, "p2_hours": 72} |
| `decision` | Yo priorizo P0/P1 por valor esperado en riesgo y obligo feedback de intervención. |

## Acción recomendada

Revisar operaciones P0/P1, asignar responsable y registrar feedback de intervención.

## Donde cambiar

`config/business_rules.yml#caida_motivos`

## Parámetros actuales usados como contexto

```yaml
homologation_required: true

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
