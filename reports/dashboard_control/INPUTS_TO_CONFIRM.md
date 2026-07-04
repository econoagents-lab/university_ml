# Inputs críticos a confirmar

Esta tabla convierte dudas de negocio en parámetros editables.

| Input | Decisión que afecta | Recomendación tomada | Donde cambiar |
|---|---|---|---|
| MLU_ENV | Comportamiento local/producción | production en Railway | `Variables Railway / .env` |
| MLU_DISABLE_SAMPLE_FALLBACK | Bloquear demo en producción | true | `Variables Railway / .env` |
| data_mode | Demo vs CRM real | crm | `config/environment.yml` |
| Horizonte riesgo caída | Target del modelo | 30 días | `config/model_params.yml > riesgo_caida.horizon_days` |
| Threshold P0 | Operaciones a intervenir hoy | 0.70 o calibrado por capacidad | `config/model_params.yml > riesgo_caida.thresholds.p0` |
| Threshold P1 | Intervenir en 24h | 0.50 | `config/model_params.yml > riesgo_caida.thresholds.p1` |
| Threshold P2 | Monitoreo 72h | 0.35 | `config/model_params.yml > riesgo_caida.thresholds.p2` |
| Capacidad diaria equipo | Cuántos P0 se pueden atender | 20-50 | `config/alert_thresholds.yml > commercial_risk` |
| Tipo de unidad foco | No mezclar depas con cocheras | departamento | `config/model_params.yml > riesgo_caida.unit_focus` |
| Separación válida | Base comercial | congelar contrato oficial | `config/business_rules.yml > separacion_valida` |
| Minuta válida | Definición de venta | congelar contrato oficial | `config/business_rules.yml > minuta_valida` |
| Caída válida | Definición del target | congelar contrato oficial | `config/business_rules.yml > caida_valida` |
| Columnas prohibidas ML | Anti-leakage | fecha_caida, fecha_firma, fecha_anulacion | `config/model_params.yml > riesgo_caida.forbidden_columns` |
| Columnas prohibidas públicas | Privacidad | cliente, DNI, teléfono, email, dirección, credenciales | `config/privacy_policy.yml > forbidden_public_fields` |
| Top N dashboard público | Exposición agregada | 5 | `config/dashboard_params.yml > public_dashboard.top_n` |
| Proyectos reales en Railway | Demo comercial | sí, agregados | `config/privacy_policy.yml > public_dashboard.expose_project_names` |
| Asesores reales en Railway | Privacidad comercial | no, anonimizar | `config/privacy_policy.yml > public_dashboard.anonymize_advisors_public` |
| Canales públicos | Demo sin PII | sí, agregados | `config/dashboard_params.yml > public_dashboard.include_channel_names` |
| Top operaciones públicas | Privacidad | no | `config/dashboard_params.yml > public_dashboard.include_row_level_operations` |
| RAG CRM access | Seguridad | solo tablas anonimizadas/agregadas | `config/rag_sql_policy.yml` |
| Railway data strategy | Despliegue público | payload agregado, no CRM live | `config/privacy_policy.yml > production_decisions` |
| Lenovo data strategy | Extracción real CRM | private_full_crm_runner | `config/environment.yml > lenovo_self_hosted` |
| GitHub artifacts | No filtrar CRM | solo agregados o anonimizados | `config/privacy_policy.yml > production_decisions` |
| RAG faithfulness mínimo | Calidad demo UNI | 0.75 | `config/alert_thresholds.yml > rag_quality` |
| Trap refusal mínimo | Seguridad RAG | 1.00 | `config/alert_thresholds.yml > rag_quality` |
| Railway URL | Smoke test API | URL Railway | `GitHub Secret MLU_RAILWAY_BASE_URL` |
| Fuente mercado precio m² | Pricing gap | scraping/CSV/API | `config/market_sources.yml` |
| Stock lento días | Alerta stock | 90/120/180 | `config/alert_thresholds.yml > stock_lento` |
| Drift PSI warning/fail | Monitoreo modelo | 0.10 / 0.25 | `config/drift_thresholds.yml` |
| Retraining max age | Reentrenamiento | 30 días | `contracts/retraining_policy.yml` |