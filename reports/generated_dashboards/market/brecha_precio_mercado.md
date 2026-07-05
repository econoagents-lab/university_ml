# Brecha Precio vs Mercado

**Familia:** `market`  
**Owner:** Chief Economist  
**Audiencia:** Gerencia / Producto  
**Prioridad:** professional  
**Estado:** cataloged

## Pregunta económica

¿Estoy por encima o debajo del mercado?

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
| `metric_group` | stock_pricing |
| `status` | ok |
| `metric_mode` | official_or_real_mart |
| `stock_total` | 3237 |
| `stock_disponible` | 1425 |
| `stock_vendido` | 1364 |
| `stock_valorizado` | 1003112652.4 |
| `absorcion_real_proxy` | 0.421378 |
| `unidades_con_precio_m2` | 3236 |
| `precio_m2_promedio_interno` | 3011.84 |
| `brecha_precio_m2_promedio` | 0.0 |
| `market_comparable_source` | ["internal_benchmark_proxy"] |
| `decision` | Yo uso stock real, precio/m² y brecha de mercado para decidir pricing, campaña o foco de venta. |

## Acción recomendada

Cruzar inventario, precio m² y velocidad de venta para ajustar campaña, descuento o mix de producto.

## Donde cambiar

`config/market_sources.yml#price_m2_market`

## Parámetros actuales usados como contexto

```yaml
granularity: distrito_mes_dormitorios
comparison_metric: brecha_precio_m2_pct

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
