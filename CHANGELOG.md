# Changelog

## v1.2.0 - GitHub Actions Commercial Alerts

- Agregué workflows para Commercial KPI Digest, RAG Quality Gate y UNI Delivery Readiness.
- Agregué workflow global `intelligence_factory_alerts_all.yml`.
- Agregué workflow self-hosted para correr CRM real desde Lenovo.
- Agregué workflow Railway smoke para validar API desplegada.
- Agregué workflow opcional para publicar alertas en GitHub Pages.
- Agregué scripts 61-68 para alertas, quality gates, issue body, webhooks y sitio estático.
- Agregué `config/alert_thresholds.yml` para separar KPIs normales de alertas reales.
- Agregué documentación de seguridad, operación y decisión Lenovo vs Railway.
- Mantengo comentarios y docstrings nuevos en primera persona.

## v1.1.0 - UNI Final RAG Economic Hypothesis Pack

- Paquete RAG económico con hipótesis, corpus seguro, Text-to-SQL, guardrails y RAGAS-like.

## v1.2.1 - Colab notebook + soft GitHub gates

- Corrijo celda del notebook final que generaba `SyntaxError: unterminated string literal` en Colab.
- Cambio `rag_quality_gate.yml` para no fallar por defecto ante alertas `warning`.
- Mantengo modo estricto con `fail_on_alert=true`.
- Agrego `tests/test_notebook_syntax.py` para compilar celdas del notebook final.
