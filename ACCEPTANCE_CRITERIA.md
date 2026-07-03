# Acceptance Criteria v1.2

La versión v1.2 queda aceptada si:

- [ ] `python scripts/66_build_all_alerts.py` genera todos los reportes en `reports/alerts/`.
- [ ] `commercial_kpi_digest.yml` puede leer el ranking de riesgo y publicar summary.
- [ ] `rag_quality_gate.yml` detecta métricas RAGAS-like bajo umbral.
- [ ] `uni_delivery_readiness.yml` valida trazabilidad y reporte final.
- [ ] `crm_full_runner_self_hosted.yml` está listo para Lenovo self-hosted.
- [ ] `railway_api_smoke_and_alert.yml` está listo para API desplegada.
- [ ] Los scripts no requieren `.env` para funcionar en modo alerta local.
- [ ] Los comentarios/docstrings nuevos están escritos en primera persona.
- [ ] `pytest -q` pasa.
