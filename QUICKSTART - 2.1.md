# Quickstart v2.2

```powershell
cd machine_learning_university_v2_2_multi_tenant_client_packaging
python scripts/116_run_v22_multi_tenant_client_packaging.py
pytest -q tests/test_multi_tenant_client_packaging.py
uvicorn api.main:app --reload
```

Abrir:

```text
reports/client_tenants/tenant_index.html
http://127.0.0.1:8000/demo/tenants
http://127.0.0.1:8000/demo/client/cliente_alpha
http://127.0.0.1:8000/product/client/cliente_alpha/package
```
