# v2.5.1 · CI Dependency & Lazy Model Fix

## Problema

El workflow `multi_tenant_client_packaging.yml` instalaba dependencias mínimas, pero `tests/test_multi_tenant_client_packaging.py` importaba `api.main`. Esa importación cargaba `api.services`, que importaba `src.mlu.model` y por tanto requería `joblib` y `scikit-learn` aunque el test solo validara endpoints multi-tenant.

## Decisión

1. Yo hago lazy import de `load_model` dentro de `predict_riesgo_caida`.
2. Yo refuerzo el workflow multi-tenant instalando `numpy`, `scikit-learn` y `joblib`.
3. Yo agrego `requirements-ci.txt` como set liviano para workflows de metadata/demo.

## Por qué esto es correcto

Los endpoints de demo, metadata y multi-tenant no deben depender del artefacto ML. El modelo debe cargarse solo cuando se llama un endpoint predictivo o cuando existe el artefacto `.joblib`.

## Comando de validación

```powershell
pytest -q tests/test_multi_tenant_client_packaging.py
```
