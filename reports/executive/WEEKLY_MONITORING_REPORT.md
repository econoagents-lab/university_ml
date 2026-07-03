# Weekly Monitoring Report - Riesgo de Caída v0.7

Estado global: **fail**

## Lectura ejecutiva

No usar el ranking como prioridad fuerte hasta auditar drift/fuentes o reentrenar.

## Steps

| Script | Estado |
|---|---|
| 22_monitor_feature_drift.py | ok |
| 23_monitor_prediction_drift.py | ok |
| 24_evaluate_calibration.py | ok |
| 25_create_experiment_plan.py | ok |
| 26_analyze_intervention_effect.py | ok |
| 27_export_feedback_store_schema.py | ok |

## Feature drift

```json
{
  "global_status": "fail",
  "feature_status_counts": {
    "ok": 6,
    "fail": 4,
    "warning": 1
  },
  "top_drift_features": [
    {
      "feature": "proyecto",
      "drift_metric": 6.718554791480698,
      "status": "fail"
    },
    {
      "feature": "asesor",
      "drift_metric": 4.917388793971117,
      "status": "fail"
    },
    {
      "feature": "descuento_pct",
      "drift_metric": 1.8585865108747286,
      "status": "fail"
    },
    {
      "feature": "precio_departamento",
      "drift_metric": 0.43669378887585636,
      "status": "fail"
    },
    {
      "feature": "dormitorios",
      "drift_metric": 0.23016309316795758,
      "status": "warning"
    }
  ],
  "prediction_drift": {}
}
```

## Prediction drift

```json
{
  "reference_rows": 2638,
  "current_rows": 880,
  "reference_mean_score": 0.4302683413020061,
  "current_mean_score": 0.540699036487509,
  "reference_p90_score": 0.6105323502979398,
  "current_p90_score": 0.619493083919819,
  "prediction_psi": 3.731872012965562,
  "status": "fail",
  "threshold_warning": 0.1,
  "threshold_fail": 0.25
}
```

## Calibration

```json
{
  "rows": 880,
  "brier_score": 0.28854244499609066,
  "mean_abs_calibration_gap": 0.45319903648750903,
  "max_abs_calibration_gap": 0.5517250154341173,
  "bins": 10
}
```
