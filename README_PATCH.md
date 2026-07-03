# MLU v0.6.1 Anti-Leakage Patch

Este patch corrige la frontera raw/audit -> model-ready:

- `fecha_caida` y `fecha_firma` pueden existir en gold audit/debug.
- Nunca entran a `feature_table`, `model_matrix`, `X_train`, `X_test`, `X_scoring` ni ranking operativo.
- El assert anti-leakage sigue estricto.
- Los tests validan synthetic y `MLU_DATA_MODE=sperant`.

## Aplicación manual

Copia estos archivos sobre tu proyecto `machine_learning_university_v0_6_feedback_and_lift` respetando las rutas.

## Validación esperada

```powershell
pytest -q
$env:MLU_DATA_MODE="sperant"
pytest -q
python scripts/15_prepare_model_ready_dataset.py
python scripts/16_train_evaluate_official_model.py
python scripts/14_score_actual_riesgo_caida.py
```

En la prueba realizada:

- `pytest -q`: 25 passed
- `MLU_DATA_MODE=sperant pytest -q`: 25 passed
- model-ready removió `fecha_caida` y `fecha_firma` del dataset final.
