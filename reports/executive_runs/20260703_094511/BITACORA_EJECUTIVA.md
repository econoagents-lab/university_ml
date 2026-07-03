# Machine Learning University - Bitacora Ejecutiva

Fecha: 2026-07-03 09:45:19
Proyecto: C:\Repos\freelance\ml_university_ready
Modo: sperant

## Resumen ejecutivo

OK: 6
Warnings: 
Fails: 0
Skipped: 

## Diagnostico

Estado general: operativo con o sin advertencias.

## Artefactos clave

Gold oficial entrenamiento: existe
Gold inferred entrenamiento: existe
Modelo riesgo caida: existe

## Pasos ejecutados

| Paso | Estado | Detalle | Log |
|---|---:|---|---|
| Activate virtual environment | ok | .venv activo. |  |
| Normalize local parquets | warning | No se encontraron parquets locales nuevos para copiar. |  |
| Extract Redshift to Parquet | skipped | Omitido por parquets locales existentes. |  |
| Profile Sperant sources | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_094511\logs\profile_sperant.log |
| Build Sperant training dataset | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_094511\logs\build_sperant_training.log |
| Build inferred rules gold table | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_094511\logs\build_inferred_rules.log |
| Validate foundations | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_094511\logs\validate_foundations.log |
| Train from Sperant | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_094511\logs\train_from_sperant.log |

## Lectura ejecutiva

1. Si existe gold oficial, el sistema puede entrenar con dataset estandar.
2. Si solo existe gold inferred, el sistema puede entrenar como borrador, pero requiere congelar reglas oficiales.
3. Si Redshift falla pero hay parquets locales, se recomienda seguir con modo local y corregir extractor despues.
4. Si hay warnings de pandas/redshift_connector, no necesariamente bloquean; revisar exit code y archivos generados.

## Siguiente accion recomendada

Revisar reglas inferidas, congelarlas como oficiales y reentrenar.
