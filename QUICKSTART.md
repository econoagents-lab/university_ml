# Quickstart v0.9

```powershell
cd machine_learning_university_v0_9_decision_dashboard_api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/41_run_v09_decision_dashboard_pipeline.py
python -m pytest -q
uvicorn api.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/dashboard/riesgo-caida
http://127.0.0.1:8000/docs
```

Output principal:

- `reports/dashboard/decision_queue_riesgo_caida.csv`
- `reports/dashboard/decision_dashboard_payload.json`
- `reports/dashboard/DECISION_DASHBOARD_RIESGO_CAIDA.html`
- `reports/dashboard/EXECUTIVE_DECISION_BRIEF_RIESGO_CAIDA.md`
