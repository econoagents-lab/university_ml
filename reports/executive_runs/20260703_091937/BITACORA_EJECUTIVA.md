# Machine Learning University - Bitacora Ejecutiva

Fecha: 2026-07-03 09:19:38
Proyecto: C:\Repos\freelance\ml_university_ready
Modo: safe

## Resumen ejecutivo

OK: 2
Warnings: 0
Fails: 0
Skipped: 0

## Diagnostico

Estado general: operativo con o sin advertencias.

## Artefactos clave

Gold oficial entrenamiento: no existe
Gold inferred entrenamiento: no existe
Modelo riesgo caida: existe

## Pasos ejecutados

| Paso | Estado | Detalle | Log |
|---|---:|---|---|
| Activate virtual environment | ok | .venv activo. |  |
| Validate foundations | ok | Completado. | C:\Repos\freelance\ml_university_ready\reports\executive_runs\20260703_091937\logs\validate_foundations.log |

## Lectura ejecutiva

1. Si existe gold oficial, el sistema puede entrenar con dataset estandar.
2. Si solo existe gold inferred, el sistema puede entrenar como borrador, pero requiere congelar reglas oficiales.
3. Si Redshift falla pero hay parquets locales, se recomienda seguir con modo local y corregir extractor despues.
4. Si hay warnings de pandas/redshift_connector, no necesariamente bloquean; revisar exit code y archivos generados.

## Siguiente accion recomendada

Copiar procesos.parquet y unidades.parquet a data/raw/sperant o ejecutar extractor Redshift con ForceExtract.
