# v0.8 Retraining Registry · CRM-first Congress Pack

## Qué cambia

v0.8 convierte el modelo de riesgo de caída en un sistema con sucesión gobernada:

- datasets versionados;
- model registry local;
- challengers entrenados contra el champion;
- política de retraining;
- endpoint `/metadata/model-registry`;
- pack de figuras para congreso de data science.

## Alineación CRM-first

El modo principal es `crm`: consume `data/processed/gold/riesgo_caida_training_model_ready.parquet` construido desde Sperant/Redshift/parquets locales. El modo `demo` queda como simulador seguro para enseñanza y presentaciones públicas sin data real.

## Por qué existe

El reporte v0.7 mostró drift global `fail`; por eso v0.8 introduce registry y política de reentrenamiento para decidir cuándo el champion debe ser retado o reemplazado.
