# Production Release Checklist v1.0

## Seguridad

- [ ] Definir `MLU_AUTH_ENABLED=true` en Railway/producción.
- [ ] Definir `MLU_API_KEY` como secret, no en código.
- [ ] No subir `.env`.

## Datos

- [ ] Confirmar fuente CRM/Sperant o parquets locales vigentes.
- [ ] Confirmar que model-ready no contiene columnas prohibidas.
- [ ] Confirmar que el registry tiene champion vigente.

## Operación

- [ ] Ejecutar `python scripts/45_run_v10_production_release.py`.
- [ ] Revisar `reports/production/PRODUCTION_READINESS_REPORT.md`.
- [ ] Revisar dashboard en `/dashboard/riesgo-caida`.
- [ ] Registrar feedback real de acciones comerciales.

## Presentación

- [ ] Usar `reports/congress/` para congreso.
- [ ] Usar `reports/dashboard/EXECUTIVE_DECISION_BRIEF_RIESGO_CAIDA.md` para gerencia.
