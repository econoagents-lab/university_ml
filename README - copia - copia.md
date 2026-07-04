# Machine Learning University v2.0 · Productized Commercial Intelligence OS

Sistema comercial inmobiliario productizado: API + dashboards + RAG + Railway public payload + GitHub alerts + feedback + experiment policy.

## Quickstart

```powershell
python scripts/108_run_v20_productized_commercial_intelligence_os.py
pytest -q
uvicorn api.main:app --reload
```

## Endpoints clave

```text
/metadata/productized-os
/dashboard/productized-os
/product/demo/package
/public/decision-dashboard
/dashboard/catalog
/dashboard/action-feedback
/dashboard/experiment-power-policy
```

## Seguridad
Railway solo debe servir payloads agregados. CRM privado se procesa en Lenovo o self-hosted runner.
