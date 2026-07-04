# Quickstart v2.1

```powershell
cd machine_learning_university_v2_1_client_ready_branding_and_deployment
python scripts/112_run_v21_client_ready_branding_and_deployment.py
pytest -q tests/test_client_ready_branding_and_deployment.py
uvicorn api.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/demo/client-ready
```

Con Railway:

```text
MLU_ENV=production
MLU_DISABLE_SAMPLE_FALLBACK=true
MLU_DEMO_AUTH_ENABLED=true
MLU_DEMO_TOKEN=<secret>
```
