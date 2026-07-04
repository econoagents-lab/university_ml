# QUICKSTART v1.2.2

## 1. Generar payload público CRM para Railway

```powershell
python scripts/69_export_public_dashboard_payload.py
python scripts/70_validate_no_demo_data_in_production.py --environment production
```

Output:

```text
reports/public/decision_dashboard_payload_public.json
reports/public/production_public_payload_validation.json
```

## 2. Correr tests

```powershell
pytest -q
```

Resultado esperado:

```text
71 passed, 1 warning
```

## 3. Levantar API local

```powershell
uvicorn api.main:app --reload
```

Endpoints públicos:

```text
http://127.0.0.1:8000/public/decision-dashboard/payload
http://127.0.0.1:8000/public/decision-dashboard
```

## 4. Configuración Railway recomendada

```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
```

Con esa configuración, si falta `reports/public/decision_dashboard_payload_public.json`, la API no sirve sample data.
