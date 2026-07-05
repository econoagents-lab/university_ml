# Quickstart v2.7 · Core Value Hardening

```powershell
cd C:\Repos\freelance\ml_university_ready
python scripts/136_run_v27_core_value_hardening.py
pytest -q tests/test_core_value_hardening.py
uvicorn api.main:app --reload
```

Luego revisar:

```text
http://127.0.0.1:8000/dashboard/executive-value-brief
http://127.0.0.1:8000/public/decision-dashboard
http://127.0.0.1:8000/decision/riesgo-caida/capacity-queue
```
