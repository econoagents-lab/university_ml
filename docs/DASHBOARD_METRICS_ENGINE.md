# Dashboard Metrics Engine v1.5

Yo agrego esta capa para que cada familia de dashboards calcule métricas propias y no dependa únicamente de KPIs globales.

## Familias cubiertas

- funnel: tasas por etapa y proxies de conversión cuando falta lead-level completo.
- riesgo: P0/P1/P2, valor esperado en riesgo, riesgo promedio y SLA.
- stock/pricing: días en tubería/stock, stock lento, valorización, descuento y contexto de mercado.
- cobranza: saldo proxy y requerimientos explícitos de mart de pagos.
- RAG: faithfulness, answer relevance, context relevance y trap refusal.
- MLOps: drift, lift, calibration, champion/challenger y razones de retraining.

## Regla de gobierno

Yo prefiero una métrica marcada como `requires_payment_mart` o `proxy` antes que inventar precisión falsa. Si falta un mart, el dashboard debe decir qué contrato o fuente falta.

## Archivos generados

- `reports/dashboard_metrics/family_metrics.json`
- `reports/dashboard_metrics/DASHBOARD_METRICS_ENGINE.md`
- `reports/dashboard_metrics/families/*.md`
- dashboards regenerados con sección `Métricas específicas de esta familia`.
