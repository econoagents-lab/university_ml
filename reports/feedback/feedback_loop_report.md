# Feedback Loop Template - Riesgo de Caída v0.6

## Resultado

Se generó una plantilla de feedback para el top 100 de operaciones priorizadas.

## Archivos

- `data/feedback/feedback_log_template.csv`
- `data/feedback/feedback_log_template.parquet`

## Cómo usarlo

1. Abrir el CSV.
2. Completar `accion_tomada`, `fecha_accion`, `resultado_7d`, `resultado_30d`, `caida_real_30d` y `comentario`.
3. Guardar una copia como `data/feedback/feedback_log.csv`.
4. Ejecutar `python scripts/19_merge_feedback_outcomes.py`.

## Validación

```json
{
  "rows": 100,
  "missing_columns": [],
  "invalid_actions": [],
  "invalid_outcomes": [],
  "is_valid": true
}
```
