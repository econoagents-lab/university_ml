# Supabase / Postgres Feedback Store

v0.7 deja el esquema SQL para que el feedback deje de vivir en CSV.

Tablas propuestas:

- `ml_prediction_log`
- `ml_feedback_log`
- `ml_experiment_assignments`
- `ml_monitoring_runs`

El objetivo no es guardar datos por guardar. Es cerrar el loop:

```text
score → acción → resultado → aprendizaje → nuevo modelo
```
