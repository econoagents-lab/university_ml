# Machine Learning University - Bitácora Ejecutiva v1.0.2 CRM Fresh Full Extract

Fecha: 2026-07-03 13:18:12
Proyecto: C:\Repos\freelance\ml_university_ready
Mode: full
Data mode: sperant
ForceExtract: True
ExtractLimit: 0

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
| Extract Redshift to Parquet | fail | C:\Repos\freelance\ml_university_ready\src\mlu\redshift_client.py:97: UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\extract_redshift.log |
| Profile Sperant sources | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\profile_sperant.log |
| Build Sperant training dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\build_sperant_training.log |
| Prepare model-ready dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\prepare_model_ready.log |
| Train/evaluate official model | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\train_evaluate_official.log |
| Score actual riesgo caida | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\score_actual.log |
| Weekly monitoring report | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\weekly_monitoring.log |
| Registry pipeline v0.8 | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\registry_v08.log |
| Decision dashboard pipeline v0.9 | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\decision_dashboard_v09.log |
| Production release pipeline v1.0 | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\production_release_v10.log |
| Pytest | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_131521\logs\pytest.log |

## Lectura ejecutiva

- Esta corrida intentó validar CRM fresco desde Redshift/Sperant.
- Si Extract Redshift to Parquet está ok, la tubería probó extracción fresca.
- Si está skipped, validaste CRM local/parquet, no Redshift vivo.
- Si Gold, model-ready, scoring y production readiness existen, el flujo end-to-end está operativo.

## Siguiente acción recomendada

Corregir primero los pasos FAIL revisando logs.
