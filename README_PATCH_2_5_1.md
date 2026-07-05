# v2.5.1 · CI Dependency & Lazy Model Fix

Este patch corrige el error de GitHub Actions:

```text
ModuleNotFoundError: No module named 'joblib'
```

## Archivos incluidos

```text
api/services.py
.github/workflows/multi_tenant_client_packaging.yml
requirements-ci.txt
docs/CI_DEPENDENCY_AND_LAZY_MODEL_FIX_v2_5_1.md
v2_5_1_ci_dependency_lazy_model_fix.diff
```

## Aplicación manual rápida

Copia los archivos sobre la raíz del repo actual y ejecuta:

```powershell
pytest -q tests/test_multi_tenant_client_packaging.py
```

## Cambio principal

`api.services` ya no importa `src.mlu.model` al cargar la API. El modelo se importa solo dentro de `predict_riesgo_caida` cuando existe el artefacto `.joblib`.

El workflow multi-tenant instala `joblib` y `scikit-learn` para evitar fallas de dependencia en CI.
