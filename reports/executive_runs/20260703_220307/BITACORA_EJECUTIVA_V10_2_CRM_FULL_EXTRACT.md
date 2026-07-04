# Machine Learning University - Bitácora Ejecutiva v1.0.2 CRM Fresh Full Extract

Fecha: 2026-07-03 22:03:41
Proyecto: C:\Repos\freelance\ml_university_ready
Mode: crm
Data mode: sperant
ForceExtract: False
ExtractLimit: 0

## Resumen ejecutivo

OK: 7
Warnings: 0
Fails: 0
Skipped: 3

## Artefactos clave

Gold entrenamiento existe: True
Model-ready existe: True
Scoring top 100 existe: True
Production readiness existe: True

## Pasos ejecutados

| Paso | Estado | Detalle | Log |
|---|---:|---|---|
| Activate virtual environment | ok | .venv activo. |  |
| Install dependencies | skipped | No solicitado. |  |
| Extract Redshift to Parquet | skipped | Omitido: se usan parquets locales existentes. Usa -ForceExtract para probar Redshift vivo. |  |
| Profile Sperant sources | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_220307\logs\profile_sperant.log |
| Build Sperant training dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_220307\logs\build_sperant_training.log |
| Prepare model-ready dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_220307\logs\prepare_model_ready.log |
| Train/evaluate official model | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_220307\logs\train_evaluate_official.log |
| Score actual riesgo caida | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_220307\logs\score_actual.log |
| Production/registry/dashboard pipelines | skipped | OnlyCRMValidation activado. |  |
| Pytest | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_220307\logs\pytest.log |

## Lectura ejecutiva

- Esta corrida usó parquets locales si existían. Para Redshift vivo usa -ForceExtract.
- Si Extract Redshift to Parquet está ok, la tubería probó extracción fresca.
- Si está skipped, validaste CRM local/parquet, no Redshift vivo.
- Si Gold, model-ready, scoring y production readiness existen, el flujo end-to-end está operativo.

## Siguiente acción recomendada

Ejecutar una corrida con -ForceExtract -ExtractLimit 1000 para probar Redshift vivo con muestra controlada.
