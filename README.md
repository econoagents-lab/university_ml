# Machine Learning University v1.0 · Production Release

No es un curso de notebooks. Es una universidad ejecutable para convertir data CRM/Sperant en modelos gobernados, APIs, dashboards, feedback loops y decisiones económicas.

## Qué trae v1.0

- API FastAPI productiva con metadata, dashboard, feedback y health checks.
- Autenticación API Key opcional para despliegue local/Railway.
- Feedback store local-first con contrato SQL para PostgreSQL/Supabase.
- Dashboard HTML ejecutivo y cola diaria de decisión.
- Model registry, champion/challenger, dataset versioning y retraining policy.
- Production readiness report, release checklist y demo pack.
- Modo CRM-first con demo/sample data como simulador seguro.

## Ejecución rápida

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/45_run_v10_production_release.py
pytest -q
uvicorn api.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`
Dashboard: `http://127.0.0.1:8000/dashboard/riesgo-caida`

## Seguridad

Por defecto, `MLU_AUTH_ENABLED=false` para no romper el laboratorio local. Para activar API key:

```powershell
$env:MLU_AUTH_ENABLED="true"
$env:MLU_API_KEY="cambia_esto"
uvicorn api.main:app --reload
```

Enviar header:

```text
X-API-Key: cambia_esto
```

## Principio rector

El modelo no termina en un score. Termina en una cola de decisión, un responsable, una acción, un feedback y una medición del resultado.
