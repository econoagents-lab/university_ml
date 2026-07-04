# CHANGELOG

## v1.2.2_railway_real_data_bridge

- Agrego bridge CRM real → Railway con payload público agregado.
- Agrego `scripts/69_export_public_dashboard_payload.py`.
- Agrego `scripts/70_validate_no_demo_data_in_production.py`.
- Agrego `scripts/71_sync_public_payload_to_railway.py`.
- Agrego `reports/public/decision_dashboard_payload_public.json`.
- Agrego `docs/RAILWAY_REAL_DATA_BRIDGE.md`.
- Agrego `docs/PRODUCTION_DATA_PRIVACY_POLICY.md`.
- Agrego `tests/test_no_demo_data_in_production.py`.
- Agrego endpoint público `/public/decision-dashboard/payload`.
- Agrego endpoint público `/public/decision-dashboard`.
- Endurezco producción: si `MLU_ENV=production` y `MLU_DISABLE_SAMPLE_FALLBACK=true`, la API no sirve datos demo cuando falta el payload CRM público.
- Hago fallback CSV para la cola de decisión si no existe `pyarrow` en entornos livianos.

Validación: `71 passed, 1 warning`.

## v1.3_dashboard_catalog_parameter_control

- Agregado catálogo de 60 dashboards posibles.
- Agregada columna `Donde cambiar` para inputs y parámetros críticos.
- Agregados `dashboard_params.yml`, `model_params.yml`, `privacy_policy.yml`, `market_sources.yml`, `rag_params.yml` y políticas asociadas.
- Codificadas decisiones recomendadas: Railway agregado, Lenovo privado, GitHub agregado/anonimizado, asesores anónimos en público.
- Agregado módulo `src/mlu/dashboard_control.py`.
- Agregados scripts 72-76 para listar, validar y generar el panel de control.
- Agregados endpoints `/metadata/dashboard-catalog` y `/metadata/dashboard-params`.
- Agregados tests de catálogo, parámetros y privacidad pública.

## v1.4_dashboard_generator_from_catalog

- Agrego generador automático de dashboards desde `dashboard_catalog.yml`.
- Genero Markdown, HTML y JSON por cada dashboard catalogado.
- Agrego índice maestro y por familia en `reports/generated_dashboards/`.
- Agrego endpoints `/metadata/generated-dashboards` y `/dashboard/catalog`.
- Agrego workflow `dashboard_generator_from_catalog.yml`.
- Agrego tests de generación y validación.
