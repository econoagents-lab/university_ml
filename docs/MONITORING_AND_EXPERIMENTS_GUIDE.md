# Monitoring & Experiments Guide v0.7

## Historia del capítulo

El modelo ya no es una respuesta. Es una maquinaria viva. Si el mercado cambia, si los asesores cambian, si los medios cambian o si la operación altera sus reglas, el score puede perder sentido sin avisar.

## Objetivo de negocio

Evitar que el ranking de riesgo de caída se use cuando la distribución de datos, la distribución de scores o la calibración se han degradado.

## Flujo técnico

```text
model-ready histórico
→ feature drift
→ prediction drift
→ calibration
→ experiment assignments
→ intervention analysis
→ weekly executive report
```

## Decisión económica

- OK: usar ranking diario.
- Warning: usar ranking con revisión humana y mirar top features con drift.
- Fail: congelar uso operativo, auditar fuentes o reentrenar.

## Archivos clave

- `scripts/22_monitor_feature_drift.py`
- `scripts/23_monitor_prediction_drift.py`
- `scripts/24_evaluate_calibration.py`
- `scripts/25_create_experiment_plan.py`
- `scripts/26_analyze_intervention_effect.py`
- `scripts/28_weekly_monitoring_report.py`
