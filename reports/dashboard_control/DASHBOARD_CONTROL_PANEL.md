# Dashboard Control Panel v1.3

Yo uso este panel para gobernar dashboards, parámetros y decisiones sin tocar código.

- Total dashboards catalogados: **62**
- Estado catálogo: **ok**
- Estado decisiones recomendadas: **ok**

## Decisiones recomendadas ya tomadas

- Railway sirve solo payload agregado CRM, no CRM live.
- Lenovo queda como runner privado para CRM completo.
- GitHub conserva artifacts agregados o anonimizados.
- Proyectos pueden mostrarse públicamente solo agregados.
- Asesores se anonimizan en público.
- Clientes, documentos, teléfonos, emails, direcciones y credenciales nunca salen al payload público.
- RAG consulta CRM solo como tablas anonimizadas/agregadas.

## Catálogo

| # | Dashboard | Pregunta económica | Owner | Prioridad | Donde cambiar |
|---:|---|---|---|---|---|
| 1 | CEO Brief Ejecutivo | ¿Qué debe decidir gerencia esta semana? | Gerencia | mvp | `config/dashboard_params.yml#ceo_brief` |
| 2 | North Star Comercial | ¿La operación comercial mejora o se deteriora? | Gerencia Comercial | professional | `config/metric_contracts.yml#north_star` |
| 3 | Funnel Global | ¿Cuántos leads llegan y cuántos terminan en minuta? | BI Comercial | mvp | `config/business_rules.yml#funnel_rules` |
| 4 | Funnel Tradicional vs Digital | ¿Qué canal convierte mejor? | Marketing / Comercial | professional | `config/dashboard_params.yml#channel_mapping` |
| 5 | Funnel por Proyecto | ¿Qué proyecto convierte mejor desde lead a venta? | Jefatura Comercial | professional | `config/dashboard_params.yml#project_filters` |
| 6 | Funnel por Asesor | ¿Qué asesor convierte mejor y dónde pierde? | Jefatura Comercial | professional | `config/dashboard_params.yml#advisor_filters` |
| 7 | Separaciones Mensuales | ¿Dónde nace la demanda real? | BI Comercial | professional | `config/business_rules.yml#separacion_valida` |
| 8 | Minutas Mensuales | ¿Dónde se materializa la venta? | BI Comercial | professional | `config/business_rules.yml#minuta_valida` |
| 9 | Conversión Separación → Minuta | ¿Qué separaciones convierten y cuáles quedan en riesgo? | Jefatura Comercial | mvp | `config/dashboard_params.yml#conversion_sep_minuta` |
| 10 | Tubería Comercial | ¿Qué ventas están pendientes de cerrar? | Jefatura Comercial | mvp | `config/business_rules.yml#tuberia_activa` |
| 11 | Tubería Envejecida | ¿Qué operaciones llevan demasiado tiempo sin cerrar? | Jefatura Comercial | mvp | `config/alert_thresholds.yml#tuberia` |
| 12 | Riesgo de Caída | ¿Qué operaciones activas tienen mayor probabilidad de caer? | Jefatura Comercial | mvp | `config/model_params.yml#riesgo_caida` |
| 13 | Ranking Riesgo Comercial | ¿A quién llamo hoy primero? | Jefatura Comercial | mvp | `config/alert_thresholds.yml#riesgo_caida_prioridades` |
| 14 | Valor Esperado en Riesgo | ¿Cuánto valor económico está expuesto? | Gerencia Comercial | mvp | `config/dashboard_params.yml#value_at_risk` |
| 15 | Caídas por Motivo | ¿Por qué se pierden operaciones? | Jefatura Comercial | professional | `config/business_rules.yml#caida_motivos` |
| 16 | Caídas por Asesor | ¿Dónde se concentra pérdida comercial por asesor? | Jefatura Comercial | professional | `config/dashboard_params.yml#caidas_asesor` |
| 17 | Caídas por Proyecto | ¿Qué proyectos están perdiendo ventas? | Gerencia Comercial | professional | `config/dashboard_params.yml#caidas_proyecto` |
| 18 | Motivos Financieros | ¿Cuánto pesa el financiamiento en la caída? | Comercial / Finanzas | professional | `config/business_rules.yml#motivos_financieros` |
| 19 | Cuota Inicial | ¿La cuota inicial acelera o protege la venta? | Finanzas / Comercial | professional | `config/business_rules.yml#cuota_inicial` |
| 20 | Días a Cuota Inicial | ¿Cuánto demora el cliente en comprometer caja? | Finanzas / Comercial | professional | `config/dashboard_params.yml#cuota_inicial_timing` |
| 21 | Lead Scoring | ¿Qué leads merecen más esfuerzo comercial? | Marketing / Comercial | professional | `config/model_params.yml#lead_scoring` |
| 22 | Conversión Lead → Separación | ¿Qué canal genera oportunidades reales? | Marketing / Comercial | professional | `config/business_rules.yml#lead_asignado` |
| 23 | Conversión Lead → Minuta | ¿Qué fuentes generan ventas, no solo leads? | Marketing / Comercial | professional | `config/dashboard_params.yml#lead_to_minuta` |
| 24 | Atribución Comercial | ¿Qué canal merece presupuesto? | Marketing | professional | `config/dashboard_params.yml#attribution` |
| 25 | Migración de Canal | ¿Cuántas ventas entran por un canal y cierran por otro? | Marketing / Comercial | professional | `config/dashboard_params.yml#channel_migration` |
| 26 | Medios por Asesor | ¿Qué asesor convierte mejor en cada canal? | Jefatura Comercial | professional | `config/dashboard_params.yml#media_advisor_matrix` |
| 27 | Proyecto × Asesor | ¿Dónde hay dependencia comercial peligrosa? | Gerencia Comercial | professional | `config/alert_thresholds.yml#concentration_risk` |
| 28 | Proyecto × Canal | ¿Qué canal funciona para cada proyecto? | Marketing / Comercial | professional | `config/dashboard_params.yml#project_channel` |
| 29 | Product Mix | ¿Qué dormitorios/tipologías se venden más? | Producto / Comercial | professional | `config/dashboard_params.yml#product_mix` |
| 30 | Stock Disponible | ¿Qué unidades quedan para vender? | Producto / Comercial | professional | `config/business_rules.yml#stock_disponible` |
| 31 | Stock Lento | ¿Qué unidades están envejeciendo sin venta? | Producto / Comercial | mvp | `config/alert_thresholds.yml#stock_lento` |
| 32 | Stock Valorizado | ¿Cuánto valor comercial queda en inventario? | Producto / Finanzas | professional | `config/dashboard_params.yml#stock_valuation` |
| 33 | Pricing por Unidad | ¿Qué unidades están caras o baratas? | Producto / Chief Economist | professional | `config/dashboard_params.yml#pricing_unitario` |
| 34 | Brecha Precio vs Mercado | ¿Estoy por encima o debajo del mercado? | Chief Economist | professional | `config/market_sources.yml#price_m2_market` |
| 35 | Elasticidad Comercial | ¿El precio afecta conversión o stock lento? | Chief Economist | professional | `config/economic_params.yml#elasticity` |
| 36 | Descuentos | ¿Qué descuentos ayudan y cuáles erosionan margen? | Comercial / Finanzas | professional | `config/dashboard_params.yml#discounts` |
| 37 | Absorción Mensual | ¿Qué tan rápido se vende el stock? | Chief Economist | professional | `config/business_rules.yml#absorcion` |
| 38 | Forecast Absorción | ¿Cuántos meses quedan de stock? | Chief Economist / Data Science | professional | `config/model_params.yml#absorcion_forecast` |
| 39 | Cobranza y Caja | ¿Cuánto dinero realmente entró? | Finanzas | professional | `config/business_rules.yml#cobranza` |
| 40 | Pagos no Asignados | ¿Qué pagos no están vinculados a unidad/proyecto? | Finanzas / BI | professional | `config/business_rules.yml#pagos_matching` |
| 41 | Avance de Cobranza por Venta | ¿Qué venta está firmada pero incompleta en caja? | Finanzas | professional | `config/dashboard_params.yml#cobranza_avance` |
| 42 | Riesgo de Cobranza | ¿Qué ventas pueden atrasar caja? | Finanzas / Data Science | professional | `config/model_params.yml#cobranza_riesgo` |
| 43 | Model Registry | ¿Qué modelo está vivo y con qué datos aprendió? | MLOps | professional | `models/registry/model_registry.json` |
| 44 | Drift Monitoring | ¿El mundo cambió respecto al entrenamiento? | MLOps | professional | `config/drift_thresholds.yml#default` |
| 45 | Calibration Dashboard | ¿Las probabilidades son creíbles? | MLOps / Data Science | professional | `config/model_params.yml#calibration` |
| 46 | Lift Deciles | ¿El ranking realmente prioriza mejor que azar? | Data Science | professional | `config/model_params.yml#lift` |
| 47 | Feedback Loop | ¿Qué pasó después de intervenir una alerta? | Jefatura Comercial / Data Science | professional | `config/feedback_contract.yml#riesgo_caida` |
| 48 | Experimentos Comerciales | ¿Intervenir P0 reduce caídas? | Chief Economist / Data Science | professional | `config/experiment_params.yml#riesgo_caida` |
| 49 | RAG Quality | ¿El asistente responde con evidencia? | RAG Owner | mvp | `config/alert_thresholds.yml#rag_quality` |
| 50 | RAG Corpus Coverage | ¿Qué documentos/fuentes están indexados? | RAG Owner | governance | `config/rag_params.yml#corpus` |
| 51 | RAG Citations | ¿Cada respuesta cita evidencia? | RAG Owner | governance | `config/rag_params.yml#citations` |
| 52 | Text-to-SQL RAG | ¿Qué preguntas puede responder con tablas? | RAG Owner / BI | governance | `config/rag_sql_policy.yml#allowed_tables` |
| 53 | UNI Readiness | ¿El trabajo final está completo y defendible? | Product Owner | governance | `config/uni_readiness.yml#checklist` |
| 54 | GitHub Alerts | ¿Qué alertas se activaron y por qué? | MLOps | governance | `config/alert_thresholds.yml#github_actions` |
| 55 | Railway Public Dashboard | ¿Qué puede ver alguien externo sin PII? | Producto / Demo | mvp | `config/privacy_policy.yml#public_dashboard` |
| 56 | Privacy & PII Audit | ¿Hay datos sensibles filtrados? | CDO | mvp | `config/privacy_policy.yml#privacy_rules` |
| 57 | Data Quality | ¿Qué tablas tienen nulos, duplicados o llaves rotas? | CDO / Analytics Engineering | governance | `contracts/data_contract_riesgo_caida.yml` |
| 58 | Lineage Dashboard | ¿De dónde viene cada métrica? | CDO | governance | `contracts/metric_contracts.yml` |
| 59 | Market Intelligence | ¿Qué dice el mercado peruano frente a mi stock? | Chief Economist | governance | `config/market_sources.yml#sources` |
| 60 | Congreso Data Science | ¿Qué gráficos sustentan el sistema? | Product Owner | governance | `config/congress_pack.yml#figures` |
| None | Proxy vs Official Gap | ¿Qué métricas ya tienen mart real y cuáles siguen siendo proxy? | CDO / Chief Economist | P0 | `config/real_mart_expansion.yml#marts` |
| 61 | Decision Action Feedback Lab | ¿Qué acción se tomó sobre cada alerta y qué resultado produjo a 7d/30d? | Jefatura Comercial / BI | mvp | `config/decision_action_feedback_lab.yml#rules` |

## Warnings de configuración

- params_ref sin sección encontrada: config/alert_thresholds.yml#tuberia
- params_ref sin sección encontrada: config/alert_thresholds.yml#riesgo_caida_prioridades
- params_ref sin sección encontrada: config/alert_thresholds.yml#concentration_risk
- params_ref sin sección encontrada: config/alert_thresholds.yml#stock_lento
- params_ref sin sección encontrada: config/privacy_policy.yml#privacy_rules