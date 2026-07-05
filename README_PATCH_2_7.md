# Patch v2.7 · Core Value Hardening

Aplicar sobre v2.6.

```powershell
python scripts/136_run_v27_core_value_hardening.py
pytest -q tests/test_core_value_hardening.py
uvicorn api.main:app --reload
```

Abrir:

- `/dashboard/executive-value-brief`
- `/public/decision-dashboard`
- `/decision/riesgo-caida/capacity-queue`
- `/metadata/core-value-hardening`
