# Proxy vs Official Gap

**Familia:** `real_marts`  
**Owner:** CDO / Chief Economist  
**Audiencia:** Gerencia / Data Team  
**Prioridad:** P0  
**Estado:** cataloged

## Pregunta económica

¿Qué métricas ya tienen mart real y cuáles siguen siendo proxy?

## KPIs agregados disponibles

- Total operaciones: **763**
- Valor total en riesgo: **S/ 21,232,580.48**
- Riesgo promedio: **0.398**
- Operaciones P0/P1: **{'operaciones': 761, 'valor_en_riesgo': 21191194.15}**
- Data mode: **crm**
- Fecha generación KPI: **2026-07-04T20:23:55**

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
| `metric_group` | real_marts |
| `status` | ok |
| `marts_generados` | 7 |
| `validation_status` | ok |
| `gaps_cerrados` | 2 |
| `familias_con_mart` | ["cobranza", "feedback", "funnel", "market", "pricing", "proxy_vs_official_gap", "stock"] |
| `safe_aggregate_only` | True |
| `decision` | Yo uso este control para saber qué dashboard se defiende con mart real y cuál sigue requiriendo fuente oficial. |

## Acción recomendada

Usar el tablero para convertir datos en decisión, responsable, plazo y métrica de resultado.

## Donde cambiar

`config/real_mart_expansion.yml#marts`

## Parámetros actuales usados como contexto

```yaml
funnel:
  preferred_sources:
  - fact_conversion_leads
  - riesgo_caida_training_model_ready
  - ranking_operaciones_riesgo_caida
  grain: periodo_mes
cobranza:
  preferred_sources:
  - fact_separacion_cuota_inicial
  - procesos
  - ranking_operaciones_riesgo_caida
  grain: periodo_mes_proyecto
stock:
  preferred_sources:
  - unidades
  - product_stock_pricing
  grain: periodo_mes_proyecto_tipo_unidad
pricing:
  preferred_sources:
  - unidades
  - proforma_unidad
  grain: unidad_hash
market:
  preferred_sources:
  - proyectos
  - mart_market_district_month
  grain: periodo_mes_proyecto_distrito
feedback:
  preferred_sources:
  - feedback_outcomes_merged
  - feedback_log_template
  grain: periodo_mes_accion_resultado

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
