# v1.2.2 Railway Real Data Bridge

Esta versión agrega un puente seguro para publicar en Railway un dashboard/API público con data CRM agregada.

## Nuevos archivos

```text
scripts/69_export_public_dashboard_payload.py
scripts/70_validate_no_demo_data_in_production.py
scripts/71_sync_public_payload_to_railway.py
reports/public/decision_dashboard_payload_public.json
docs/RAILWAY_REAL_DATA_BRIDGE.md
docs/PRODUCTION_DATA_PRIVACY_POLICY.md
tests/test_no_demo_data_in_production.py
.github/workflows/railway_public_payload_bridge.yml
```

## Decisión técnica

Yo no subo filas operativas a Railway. Solo subo agregados públicos.

## Resultado

Railway puede servir:

```text
/public/decision-dashboard/payload
/public/decision-dashboard
```

sin exponer PII.
