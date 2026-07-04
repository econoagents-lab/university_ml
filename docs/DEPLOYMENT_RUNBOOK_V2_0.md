# Deployment Runbook v2.0

## Local privado Lenovo

```powershell
$env:MLU_PRIVATE_DATA_DIR="C:\Repos\freelance\ml_university_ready\data\raw\sperant"
python scripts/108_run_v20_productized_commercial_intelligence_os.py
pytest -q
```

## Railway público seguro

Variables recomendadas:

```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
MLU_DATA_MODE=crm
```

Railway debe recibir `reports/public/decision_dashboard_payload_public.json` generado previamente y validado sin PII.

## GitHub Actions
Ejecutar manualmente:

```text
Productized Commercial Intelligence OS
Railway Public Payload Bridge
Intelligence Factory Alerts All
Dashboard Generator From Catalog
Experiment Power Policy Engine
```
