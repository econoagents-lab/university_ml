# Machine Learning University v1.5 — Dashboard Metrics Engine

Yo uso esta versión para que cada familia de dashboard calcule inteligencia específica por producto económico.

## Qué agrega

- Métricas de funnel: tasas por etapa y proxies explícitos.
- Métricas de riesgo: P0/P1, valor en riesgo, SLA.
- Métricas de stock/pricing: días, valorización, descuentos, mercado.
- Métricas de cobranza: saldo proxy y faltantes de mart de pagos.
- Métricas RAG: faithfulness, answer relevance, context relevance, trap refusal.
- Métricas MLOps: drift, lift, calibration, champion/challenger.

## Ejecución

```powershell
python scripts/84_run_v15_dashboard_metrics_engine.py
python -m pytest -q
```

O:

```powershell
.
un_dashboard_metrics_engine.ps1 -RunTests -OpenReport
```

## Outputs clave

- `reports/dashboard_metrics/DASHBOARD_METRICS_ENGINE.md`
- `reports/dashboard_metrics/family_metrics.json`
- `reports/generated_dashboards/index.html`

No incluyo `.env`, credenciales ni PII.


## v1.6 · Real Mart Expansion

Esta versión agrega marts reales seguros para funnel, cobranza, stock, pricing, mercado y feedback. Ejecuta:

```powershell
python scripts/88_run_v16_real_mart_expansion.py
pytest -q
```

Reporte principal: `reports/real_marts/REAL_MART_EXPANSION.md`.
