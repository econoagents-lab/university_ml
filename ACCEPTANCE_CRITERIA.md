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
