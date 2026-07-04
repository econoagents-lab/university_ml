# Acceptance Criteria v1.2.2

- [x] Existe `scripts/69_export_public_dashboard_payload.py`.
- [x] Existe `scripts/70_validate_no_demo_data_in_production.py`.
- [x] Existe `scripts/71_sync_public_payload_to_railway.py`.
- [x] Existe `reports/public/decision_dashboard_payload_public.json`.
- [x] Existe `docs/RAILWAY_REAL_DATA_BRIDGE.md`.
- [x] Existe `docs/PRODUCTION_DATA_PRIVACY_POLICY.md`.
- [x] Existe `tests/test_no_demo_data_in_production.py`.
- [x] La API bloquea fallback demo en producción si falta el payload CRM público.
- [x] El payload público tiene `data_mode = crm`.
- [x] El payload público no contiene cliente, documento, email, teléfono, nombre completo, dirección ni credenciales.
- [x] `pytest -q` pasa.

## v1.3 Acceptance Criteria

- Existe `config/dashboard_catalog.yml` con al menos 60 dashboards.
- Existe `reports/dashboard_control/DASHBOARD_CONTROL_PANEL.md` con columna `Donde cambiar`.
- Existe `reports/dashboard_control/INPUTS_TO_CONFIRM.md` con inputs críticos y rutas de cambio.
- Las decisiones recomendadas quedan codificadas en `dashboard_params.yml` y `privacy_policy.yml`.
- Railway público no expone filas, clientes, documentos, teléfonos, emails, direcciones ni credenciales.
- Los tests pasan con `pytest -q`.

## v1.4 Acceptance Criteria

- [x] Existe `src/mlu/dashboard_generator.py`.
- [x] Existen scripts 77-80 para generar, indexar y validar dashboards.
- [x] Se generan al menos 60 dashboards desde catálogo.
- [x] Cada dashboard contiene pregunta económica, owner, audiencia, acción recomendada y `Donde cambiar`.
- [x] Existe índice maestro HTML/Markdown.
- [x] Existe manifest JSON.
- [x] Existen tests automatizados.
- [x] No se requiere `.env` ni credenciales.
