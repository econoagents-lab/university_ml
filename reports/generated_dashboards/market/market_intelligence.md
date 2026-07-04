# Market Intelligence

**Familia:** `market`  
**Owner:** Chief Economist  
**Audiencia:** Gerencia / Producto  
**Prioridad:** governance  
**Estado:** cataloged

## Pregunta económica

¿Qué dice el mercado peruano frente a mi stock?

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
| `metric_group` | market |
| `status` | proxy |
| `metric_mode` | real_mart_project_vs_market |
| `proyectos_comparados` | 17 |
| `distritos` | 3 |
| `precio_m2_proyecto_promedio` | 3606.32 |
| `precio_m2_mercado_promedio` | 3606.32 |
| `brecha_precio_m2_promedio` | 0.0 |
| `comparable_source` | ["internal_benchmark_proxy"] |
| `decision` | Yo uso brecha de precio/m² para distinguir problema de precio, producto o presión de mercado. |

## Acción recomendada

Usar el tablero para convertir datos en decisión, responsable, plazo y métrica de resultado.

## Donde cambiar

`config/market_sources.yml#sources`

## Parámetros actuales usados como contexto

```yaml
bcrp:
  status: planned
  use: tasas, crédito, contexto macro
inei:
  status: planned
  use: demografía y distritos
capeco:
  status: planned
  use: mercado inmobiliario
fondo_mivivienda:
  status: planned
  use: financiamiento y demanda
scraping_oferta_lima:
  status: planned
  use: precio m2 comparable

```

## Regla de gobierno

Yo genero este dashboard desde `config/dashboard_catalog.yml` y sus parámetros asociados. Si cambia la decisión económica, cambio configuración; no reescribo el tablero a mano.
