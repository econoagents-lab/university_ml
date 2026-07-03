# Acceptance Criteria v1.0

- `pytest -q` pasa sin errores.
- `/health` responde con versión `1.0.0`.
- `/metadata/release` expone release estable.
- `/metadata/production-readiness` expone readiness report.
- `/metadata/model-registry` conserva champion/challenger metadata.
- Dashboard HTML se sirve en `/dashboard/riesgo-caida`.
- Feedback API conserva escritura local.
- Auth opcional no rompe entorno local.
- SQL de Supabase/Postgres existe en `sql/production_feedback_store_schema.sql`.
- No se incluye `.env` ni credenciales.
