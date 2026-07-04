# Railway Final Deployment Guide v2.1

## Start command
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

## Variables
```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
MLU_DEMO_AUTH_ENABLED=true
MLU_DEMO_TOKEN=<configurar en Railway>
```

## Validación
1. Ejecutar `python scripts/112_run_v21_client_ready_branding_and_deployment.py`.
2. Confirmar que `reports/public/decision_dashboard_payload_public.json` existe.
3. Confirmar que `/demo/client-ready` responde.
4. Confirmar que `/public/decision-dashboard` no expone filas ni PII.
