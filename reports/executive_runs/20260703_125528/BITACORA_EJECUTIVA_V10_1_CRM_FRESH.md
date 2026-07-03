# Machine Learning University - BitÃ¡cora Ejecutiva v1.0.1 CRM Fresh

Fecha: 2026-07-03 12:56:44
Proyecto: C:\Repos\freelance\ml_university_ready
Mode: crm
Data mode: sperant
ForceExtract: True
ExtractLimit: 1000

## Resumen ejecutivo

OK: 11
Warnings: 0
Fails: 1
Skipped: 1

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
| Extract Redshift to Parquet | fail | C:\Repos\freelance\ml_university_ready\src\mlu\redshift_client.py:97: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\extract_redshift.log |
| Profile Sperant sources | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\profile_sperant.log |
| Build Sperant training dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\build_sperant_training.log |
| Prepare model-ready dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\prepare_model_ready.log |
| Train/evaluate official model | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\train_evaluate_official.log |
| Score actual riesgo caida | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\score_actual.log |
| Weekly monitoring report | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\weekly_monitoring.log |
| Registry pipeline v0.8 | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\registry_v08.log |
| Decision dashboard pipeline v0.9 | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\decision_dashboard_v09.log |
| Production release pipeline v1.0 | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\production_release_v10.log |
| Pytest | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_125528\logs\pytest.log |

## Lectura ejecutiva

- Esta corrida intentÃ³ validar CRM fresco desde Redshift/Sperant.
- Si Extract Redshift to Parquet estÃ¡ ok, la tuberÃ­a probÃ³ extracciÃ³n fresca.
- Si estÃ¡ skipped, validaste CRM local/parquet, no Redshift vivo.
- Si Gold, model-ready, scoring y production readiness existen, el flujo end-to-end estÃ¡ operativo.

## Siguiente acciÃ³n recomendada

Corregir primero los pasos FAIL revisando logs.
