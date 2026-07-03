# Quickstart v1.0 Production Release

## 1. Crear entorno

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Ejecutar pipeline de release

```powershell
python scripts/45_run_v10_production_release.py
```

## 3. Tests

```powershell
pytest -q
```

## 4. API

```powershell
uvicorn api.main:app --reload
```

Endpoints clave:

- `GET /health`
- `GET /production/health`
- `GET /metadata/release`
- `GET /metadata/production-readiness`
- `GET /metadata/model-registry`
- `GET /dashboard/riesgo-caida`
- `GET /decision/riesgo-caida/queue`
- `POST /feedback/riesgo-caida`

## 5. Auth opcional

```powershell
$env:MLU_AUTH_ENABLED="true"
$env:MLU_API_KEY="cambia_esto"
```

Luego enviar header `X-API-Key`.
