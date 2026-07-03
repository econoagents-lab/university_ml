# Machine Learning University v0.6 - Feedback & Lift

Universidad de Machine Learning aplicada a inteligencia comercial inmobiliaria. Esta versión toma el modelo gobernado de riesgo de caída y lo convierte en un sistema operativo de priorización, lift y feedback.

## Flujo principal

```text
gold model-ready
→ entrenamiento oficial
→ scoring actual
→ ranking comercial
→ lift por deciles
→ feedback loop
→ CEO brief
```

## Ejecución rápida

```powershell
python scripts/15_prepare_model_ready_dataset.py
python scripts/16_train_evaluate_official_model.py
python scripts/14_score_actual_riesgo_caida.py
python scripts/17_evaluate_lift_deciles.py
python scripts/18_initialize_feedback_loop.py
python scripts/19_merge_feedback_outcomes.py
python scripts/20_generate_executive_lift_report.py
python -m pytest
```

O todo junto:

```powershell
python scripts/21_daily_risk_control.py
```

Bitácora ejecutiva:

```powershell
.\run_executive_reporting_bitacora_v6_feedback_and_lift.ps1 -Mode sperant -RunTests -OpenReport
```

## Artefactos nuevos

- `reports/modeling/lift_deciles.csv`
- `reports/modeling/lift_report.md`
- `reports/modeling/precision_at_k.csv`
- `reports/modeling/lift_deciles.png`
- `data/feedback/feedback_log_template.csv`
- `data/feedback/feedback_outcomes_merged.parquet`
- `reports/executive/CEO_BRIEF_RIESGO_CAIDA_V0_6.md`

## API

```powershell
uvicorn api.main:app --reload
```

Endpoints nuevos:

- `GET /feedback/riesgo-caida/schema`
- `POST /feedback/riesgo-caida`

## Principio

Ningún modelo termina en un score. Termina en decisión, responsable, acción y medición del resultado.
