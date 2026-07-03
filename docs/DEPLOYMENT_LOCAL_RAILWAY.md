# Deployment local/Railway v1.0

## Local

```powershell
python scripts/45_run_v10_production_release.py
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Railway

Start command:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Variables recomendadas:

```text
MLU_ENV=production
MLU_AUTH_ENABLED=true
MLU_API_KEY=<secret>
MLU_DATA_MODE=crm
```

Variables opcionales para feedback store futuro:

```text
MLU_FEEDBACK_DATABASE_URL=<postgres_url>
SUPABASE_URL=<url>
SUPABASE_SERVICE_ROLE_KEY=<secret>
```

v1.0 mantiene escritura local-first para feedback. La tabla SQL queda lista para migrar a Supabase/Postgres.
