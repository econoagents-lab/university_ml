# Real Mart Expansion v1.6

Yo reemplazo proxies por marts reales seguros para que cada dashboard pueda defender una métrica con fuente, grano y modo de evidencia.

**Generado:** 2026-07-04T16:17:48  
**Safe aggregate only:** True  
**Private data copied to repo:** False

## Marts generados

| Mart | Estado | Filas | Modo |
|---|---:|---:|---|
| funnel | ok | 1 | real_source:riesgo_caida_training_model_ready.parquet |
| cobranza | ok | 17 | real_source:procesos.parquet |
| stock | ok | 134 | real_source:unidades.parquet |
| pricing | ok | 3236 | real_source:unidades.parquet |
| market | proxy | 17 | internal_benchmark_proxy |
| feedback | ok | 15 | real_source:feedback_outcomes_merged.parquet |
| proxy_vs_official_gap | ok | 6 | control |

## Política de privacidad

No exporto cliente, documento, email, teléfono, dirección, credenciales ni filas operativas individuales. Cuando necesito trazabilidad por persona operativa, uso IDs hasheados estables.

## Decisión económica

Yo uso marts reales para separar lo que ya puede presentarse como evidencia dura de lo que todavía requiere una fuente oficial.