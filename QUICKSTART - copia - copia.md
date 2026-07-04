# Quickstart v2.0

```powershell
cd machine_learning_university_v2_0_productized_commercial_intelligence_os
python scripts/108_run_v20_productized_commercial_intelligence_os.py
pytest -q
uvicorn api.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/metadata/productized-os
http://127.0.0.1:8000/dashboard/productized-os
http://127.0.0.1:8000/product/demo/package
```

Con ruta privada CRM:

```powershell
.un_productized_commercial_intelligence_os.ps1 -PrivateDataDir "C:\Reposreelance\ml_university_ready\dataaw\sperant" -RunTests -OpenReport
```
