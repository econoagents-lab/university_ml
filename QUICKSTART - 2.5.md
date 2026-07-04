# Quickstart v2.5

```powershell
cd machine_learning_university_v2_5_client_success_and_renewal_intelligence
python scripts/128_run_v25_client_success_and_renewal_intelligence.py
pytest -q tests/test_client_success_and_renewal_intelligence.py
uvicorn api.main:app --reload
```

Abrir:

```text
reports/client_success/client_success_index.html
http://127.0.0.1:8000/success/clients
http://127.0.0.1:8000/success/client/cliente_alpha/health
```

Con ruta privada CRM, si aplica:

```powershell
.\run_client_success_and_renewal_intelligence.ps1 `
  -PrivateDataDir "C:\Repos\freelance\ml_university_ready\data\raw\sperant" `
  -RunTests `
  -OpenIndex
```
