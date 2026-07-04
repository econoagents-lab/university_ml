# v1.7 Decision Action Feedback Lab

Yo cierro el ciclo operativo de la fábrica:

```text
alerta de riesgo -> acción comercial -> responsable -> resultado 7d/30d -> señal de aprendizaje -> política de retraining
```

## Qué resuelve

El modelo de riesgo deja de ser una tabla de scores y se convierte en una bitácora de decisiones. La pregunta cambia de “¿quién tiene riesgo?” a “¿qué hice, quién lo hizo, qué pasó y qué aprende el sistema?”.

## Ruta privada recomendada

Si tus parquets raw viven en:

```powershell
C:\Repos\freelance\ml_university_ready\data\raw\sperant
```

usa esa ruta como `MLU_PRIVATE_DATA_DIR`:

```powershell
$env:MLU_PRIVATE_DATA_DIR="C:\Repos\freelance\ml_university_ready\data\raw\sperant"
python scripts/94_run_v17_decision_action_feedback_lab.py
```

O con el runner:

```powershell
.\run_decision_action_feedback_lab.ps1 -PrivateDataDir "C:\Repos\freelance\ml_university_ready\data\raw\sperant" -RunTests -OpenReport
```

## Artefactos

- `data/processed/action_feedback/decision_action_queue_safe.csv`
- `data/processed/action_feedback/action_assignment_template.csv`
- `data/processed/action_feedback/feedback_events_safe.csv`
- `data/processed/action_feedback/action_outcomes_summary.csv`
- `data/processed/action_feedback/retraining_signal.json`
- `reports/action_feedback/DECISION_ACTION_FEEDBACK_LAB.md`

## Privacidad

Yo no exporto clientes, DNI, teléfonos, emails, direcciones, códigos de proforma/unidad ni credenciales. Las operaciones salen como `operation_id` y los asesores como `asesor_id`.
