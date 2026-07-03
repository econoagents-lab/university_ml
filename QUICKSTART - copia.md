# Quickstart v0.6

```powershell
cd machine_learning_university_v0_6_feedback_and_lift
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/21_daily_risk_control.py
python -m pytest
```

Abrir API:

```powershell
uvicorn api.main:app --reload
```

Abrir reporte ejecutivo:

```powershell
notepad reports\executive\CEO_BRIEF_RIESGO_CAIDA_V0_6.md
```
