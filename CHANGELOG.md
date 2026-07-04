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
