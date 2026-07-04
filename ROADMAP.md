# ROADMAP

## v1.2.2 Railway Real Data Bridge

- Payload público agregado para Railway.
- Bloqueo de sample fallback en producción.
- Validación anti-PII del payload.
- Endpoint público seguro.
- GitHub Action para validar/generar artifact.

## Próximo paso sugerido: v1.3_public_demo_release

- Railway deploy documentado de punta a punta.
- GitHub Pages/Static dashboard opcional.
- Demo ejecutiva pública con datos agregados.
- Autenticación opcional para endpoints privados.

## Después de v1.3

- v1.4: Power BI / HTML dashboard generator desde `dashboard_catalog.yml`.
- v1.5: Market intelligence real con scrapers/fuentes externas.
- v1.6: Multi-model operations: riesgo caída + lead scoring + stock lento + cobranza.

## v1.4 · Dashboard Generator From Catalog

Estado: implementado. El catálogo de 60 dashboards ahora produce artefactos navegables. Próximo paso sugerido: `v1.5_dashboard_metrics_engine`, para que cada familia tenga cálculos específicos propios y no solo KPIs globales agregados.
