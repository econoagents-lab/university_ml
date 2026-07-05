# Dashboard Generator From Catalog

**Versión:** v2.6_public_peru_demo_and_dashboard_route_fix  
**Generados:** 62  
**Fecha:** 2026-07-04T22:36:20

Yo genero estos dashboards desde `config/dashboard_catalog.yml`. Si cambia una pregunta económica, owner o parámetro, cambio configuración y regenero.

## action_feedback
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Decision Action Feedback Lab | mvp | `config/decision_action_feedback_lab.yml#rules` | [decision_action_feedback_lab](reports\generated_dashboards\action_feedback\decision_action_feedback_lab.html) | [decision_action_feedback_lab](reports\generated_dashboards\action_feedback\decision_action_feedback_lab.md) |

## alerts
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| GitHub Alerts | governance | `config/alert_thresholds.yml#github_actions` | [github_alerts](reports\generated_dashboards\alerts\github_alerts.html) | [github_alerts](reports\generated_dashboards\alerts\github_alerts.md) |
| UNI Readiness | governance | `config/uni_readiness.yml#checklist` | [uni_readiness](reports\generated_dashboards\alerts\uni_readiness.html) | [uni_readiness](reports\generated_dashboards\alerts\uni_readiness.md) |

## cobranza
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Avance de Cobranza por Venta | professional | `config/dashboard_params.yml#cobranza_avance` | [avance_cobranza_venta](reports\generated_dashboards\cobranza\avance_cobranza_venta.html) | [avance_cobranza_venta](reports\generated_dashboards\cobranza\avance_cobranza_venta.md) |
| Cobranza y Caja | professional | `config/business_rules.yml#cobranza` | [cobranza_caja](reports\generated_dashboards\cobranza\cobranza_caja.html) | [cobranza_caja](reports\generated_dashboards\cobranza\cobranza_caja.md) |
| Cuota Inicial | professional | `config/business_rules.yml#cuota_inicial` | [cuota_inicial](reports\generated_dashboards\cobranza\cuota_inicial.html) | [cuota_inicial](reports\generated_dashboards\cobranza\cuota_inicial.md) |
| Días a Cuota Inicial | professional | `config/dashboard_params.yml#cuota_inicial_timing` | [dias_a_cuota_inicial](reports\generated_dashboards\cobranza\dias_a_cuota_inicial.html) | [dias_a_cuota_inicial](reports\generated_dashboards\cobranza\dias_a_cuota_inicial.md) |
| Pagos no Asignados | professional | `config/business_rules.yml#pagos_matching` | [pagos_no_asignados](reports\generated_dashboards\cobranza\pagos_no_asignados.html) | [pagos_no_asignados](reports\generated_dashboards\cobranza\pagos_no_asignados.md) |
| Riesgo de Cobranza | professional | `config/model_params.yml#cobranza_riesgo` | [riesgo_cobranza](reports\generated_dashboards\cobranza\riesgo_cobranza.html) | [riesgo_cobranza](reports\generated_dashboards\cobranza\riesgo_cobranza.md) |

## commercial
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Atribución Comercial | professional | `config/dashboard_params.yml#attribution` | [atribucion_comercial](reports\generated_dashboards\commercial\atribucion_comercial.html) | [atribucion_comercial](reports\generated_dashboards\commercial\atribucion_comercial.md) |
| Conversión Lead → Minuta | professional | `config/dashboard_params.yml#lead_to_minuta` | [conversion_lead_minuta](reports\generated_dashboards\commercial\conversion_lead_minuta.html) | [conversion_lead_minuta](reports\generated_dashboards\commercial\conversion_lead_minuta.md) |
| Conversión Lead → Separación | professional | `config/business_rules.yml#lead_asignado` | [conversion_lead_separacion](reports\generated_dashboards\commercial\conversion_lead_separacion.html) | [conversion_lead_separacion](reports\generated_dashboards\commercial\conversion_lead_separacion.md) |
| Conversión Separación → Minuta | mvp | `config/dashboard_params.yml#conversion_sep_minuta` | [conversion_sep_minuta](reports\generated_dashboards\commercial\conversion_sep_minuta.html) | [conversion_sep_minuta](reports\generated_dashboards\commercial\conversion_sep_minuta.md) |
| Funnel Global | mvp | `config/business_rules.yml#funnel_rules` | [funnel_global](reports\generated_dashboards\commercial\funnel_global.html) | [funnel_global](reports\generated_dashboards\commercial\funnel_global.md) |
| Funnel por Asesor | professional | `config/dashboard_params.yml#advisor_filters` | [funnel_por_asesor](reports\generated_dashboards\commercial\funnel_por_asesor.html) | [funnel_por_asesor](reports\generated_dashboards\commercial\funnel_por_asesor.md) |
| Funnel por Proyecto | professional | `config/dashboard_params.yml#project_filters` | [funnel_por_proyecto](reports\generated_dashboards\commercial\funnel_por_proyecto.html) | [funnel_por_proyecto](reports\generated_dashboards\commercial\funnel_por_proyecto.md) |
| Funnel Tradicional vs Digital | professional | `config/dashboard_params.yml#channel_mapping` | [funnel_tradicional_vs_digital](reports\generated_dashboards\commercial\funnel_tradicional_vs_digital.html) | [funnel_tradicional_vs_digital](reports\generated_dashboards\commercial\funnel_tradicional_vs_digital.md) |
| Lead Scoring | professional | `config/model_params.yml#lead_scoring` | [lead_scoring](reports\generated_dashboards\commercial\lead_scoring.html) | [lead_scoring](reports\generated_dashboards\commercial\lead_scoring.md) |
| Medios por Asesor | professional | `config/dashboard_params.yml#media_advisor_matrix` | [medios_por_asesor](reports\generated_dashboards\commercial\medios_por_asesor.html) | [medios_por_asesor](reports\generated_dashboards\commercial\medios_por_asesor.md) |
| Migración de Canal | professional | `config/dashboard_params.yml#channel_migration` | [migracion_canal](reports\generated_dashboards\commercial\migracion_canal.html) | [migracion_canal](reports\generated_dashboards\commercial\migracion_canal.md) |
| Minutas Mensuales | professional | `config/business_rules.yml#minuta_valida` | [minutas_mensuales](reports\generated_dashboards\commercial\minutas_mensuales.html) | [minutas_mensuales](reports\generated_dashboards\commercial\minutas_mensuales.md) |
| Proyecto × Asesor | professional | `config/alert_thresholds.yml#concentration_risk` | [proyecto_asesor](reports\generated_dashboards\commercial\proyecto_asesor.html) | [proyecto_asesor](reports\generated_dashboards\commercial\proyecto_asesor.md) |
| Proyecto × Canal | professional | `config/dashboard_params.yml#project_channel` | [proyecto_canal](reports\generated_dashboards\commercial\proyecto_canal.html) | [proyecto_canal](reports\generated_dashboards\commercial\proyecto_canal.md) |
| Separaciones Mensuales | professional | `config/business_rules.yml#separacion_valida` | [separaciones_mensuales](reports\generated_dashboards\commercial\separaciones_mensuales.html) | [separaciones_mensuales](reports\generated_dashboards\commercial\separaciones_mensuales.md) |
| Tubería Comercial | mvp | `config/business_rules.yml#tuberia_activa` | [tuberia_comercial](reports\generated_dashboards\commercial\tuberia_comercial.html) | [tuberia_comercial](reports\generated_dashboards\commercial\tuberia_comercial.md) |

## congress
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Congreso Data Science | governance | `config/congress_pack.yml#figures` | [congreso_data_science](reports\generated_dashboards\congress\congreso_data_science.html) | [congreso_data_science](reports\generated_dashboards\congress\congreso_data_science.md) |

## data_quality
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Data Quality | governance | `contracts/data_contract_riesgo_caida.yml` | [data_quality](reports\generated_dashboards\data_quality\data_quality.html) | [data_quality](reports\generated_dashboards\data_quality\data_quality.md) |

## executive
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| CEO Brief Ejecutivo | mvp | `config/dashboard_params.yml#ceo_brief` | [ceo_brief](reports\generated_dashboards\executive\ceo_brief.html) | [ceo_brief](reports\generated_dashboards\executive\ceo_brief.md) |
| North Star Comercial | professional | `config/metric_contracts.yml#north_star` | [north_star_comercial](reports\generated_dashboards\executive\north_star_comercial.html) | [north_star_comercial](reports\generated_dashboards\executive\north_star_comercial.md) |

## experiments
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Experimentos Comerciales | professional | `config/experiment_params.yml#riesgo_caida` | [experimentos_comerciales](reports\generated_dashboards\experiments\experimentos_comerciales.html) | [experimentos_comerciales](reports\generated_dashboards\experiments\experimentos_comerciales.md) |

## feedback
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Feedback Loop | professional | `config/feedback_contract.yml#riesgo_caida` | [feedback_loop](reports\generated_dashboards\feedback\feedback_loop.html) | [feedback_loop](reports\generated_dashboards\feedback\feedback_loop.md) |

## lineage
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Lineage Dashboard | governance | `contracts/metric_contracts.yml` | [lineage_dashboard](reports\generated_dashboards\lineage\lineage_dashboard.html) | [lineage_dashboard](reports\generated_dashboards\lineage\lineage_dashboard.md) |

## market
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Absorción Mensual | professional | `config/business_rules.yml#absorcion` | [absorcion_mensual](reports\generated_dashboards\market\absorcion_mensual.html) | [absorcion_mensual](reports\generated_dashboards\market\absorcion_mensual.md) |
| Brecha Precio vs Mercado | professional | `config/market_sources.yml#price_m2_market` | [brecha_precio_mercado](reports\generated_dashboards\market\brecha_precio_mercado.html) | [brecha_precio_mercado](reports\generated_dashboards\market\brecha_precio_mercado.md) |
| Elasticidad Comercial | professional | `config/economic_params.yml#elasticity` | [elasticidad_comercial](reports\generated_dashboards\market\elasticidad_comercial.html) | [elasticidad_comercial](reports\generated_dashboards\market\elasticidad_comercial.md) |
| Forecast Absorción | professional | `config/model_params.yml#absorcion_forecast` | [forecast_absorcion](reports\generated_dashboards\market\forecast_absorcion.html) | [forecast_absorcion](reports\generated_dashboards\market\forecast_absorcion.md) |
| Market Intelligence | governance | `config/market_sources.yml#sources` | [market_intelligence](reports\generated_dashboards\market\market_intelligence.html) | [market_intelligence](reports\generated_dashboards\market\market_intelligence.md) |

## modeling
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Calibration Dashboard | professional | `config/model_params.yml#calibration` | [calibration_dashboard](reports\generated_dashboards\modeling\calibration_dashboard.html) | [calibration_dashboard](reports\generated_dashboards\modeling\calibration_dashboard.md) |
| Lift Deciles | professional | `config/model_params.yml#lift` | [lift_deciles](reports\generated_dashboards\modeling\lift_deciles.html) | [lift_deciles](reports\generated_dashboards\modeling\lift_deciles.md) |

## monitoring
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Drift Monitoring | professional | `config/drift_thresholds.yml#default` | [drift_monitoring](reports\generated_dashboards\monitoring\drift_monitoring.html) | [drift_monitoring](reports\generated_dashboards\monitoring\drift_monitoring.md) |

## public
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Privacy & PII Audit | mvp | `config/privacy_policy.yml#privacy_rules` | [privacy_pii_audit](reports\generated_dashboards\public\privacy_pii_audit.html) | [privacy_pii_audit](reports\generated_dashboards\public\privacy_pii_audit.md) |
| Railway Public Dashboard | mvp | `config/privacy_policy.yml#public_dashboard` | [railway_public_dashboard](reports\generated_dashboards\public\railway_public_dashboard.html) | [railway_public_dashboard](reports\generated_dashboards\public\railway_public_dashboard.md) |

## real_marts
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Proxy vs Official Gap | P0 | `config/real_mart_expansion.yml#marts` | [proxy_vs_official_gap](reports\generated_dashboards\real_marts\proxy_vs_official_gap.html) | [proxy_vs_official_gap](reports\generated_dashboards\real_marts\proxy_vs_official_gap.md) |

## registry
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Model Registry | professional | `models/registry/model_registry.json` | [model_registry](reports\generated_dashboards\registry\model_registry.html) | [model_registry](reports\generated_dashboards\registry\model_registry.md) |

## risk
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Caídas por Asesor | professional | `config/dashboard_params.yml#caidas_asesor` | [caidas_por_asesor](reports\generated_dashboards\risk\caidas_por_asesor.html) | [caidas_por_asesor](reports\generated_dashboards\risk\caidas_por_asesor.md) |
| Caídas por Motivo | professional | `config/business_rules.yml#caida_motivos` | [caidas_por_motivo](reports\generated_dashboards\risk\caidas_por_motivo.html) | [caidas_por_motivo](reports\generated_dashboards\risk\caidas_por_motivo.md) |
| Caídas por Proyecto | professional | `config/dashboard_params.yml#caidas_proyecto` | [caidas_por_proyecto](reports\generated_dashboards\risk\caidas_por_proyecto.html) | [caidas_por_proyecto](reports\generated_dashboards\risk\caidas_por_proyecto.md) |
| Motivos Financieros | professional | `config/business_rules.yml#motivos_financieros` | [motivos_financieros](reports\generated_dashboards\risk\motivos_financieros.html) | [motivos_financieros](reports\generated_dashboards\risk\motivos_financieros.md) |
| Ranking Riesgo Comercial | mvp | `config/alert_thresholds.yml#riesgo_caida_prioridades` | [ranking_riesgo_comercial](reports\generated_dashboards\risk\ranking_riesgo_comercial.html) | [ranking_riesgo_comercial](reports\generated_dashboards\risk\ranking_riesgo_comercial.md) |
| Riesgo de Caída | mvp | `config/model_params.yml#riesgo_caida` | [riesgo_caida](reports\generated_dashboards\risk\riesgo_caida.html) | [riesgo_caida](reports\generated_dashboards\risk\riesgo_caida.md) |
| Tubería Envejecida | mvp | `config/alert_thresholds.yml#tuberia` | [tuberia_envejecida](reports\generated_dashboards\risk\tuberia_envejecida.html) | [tuberia_envejecida](reports\generated_dashboards\risk\tuberia_envejecida.md) |
| Valor Esperado en Riesgo | mvp | `config/dashboard_params.yml#value_at_risk` | [valor_esperado_en_riesgo](reports\generated_dashboards\risk\valor_esperado_en_riesgo.html) | [valor_esperado_en_riesgo](reports\generated_dashboards\risk\valor_esperado_en_riesgo.md) |

## stock_pricing
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| Descuentos | professional | `config/dashboard_params.yml#discounts` | [descuentos](reports\generated_dashboards\stock_pricing\descuentos.html) | [descuentos](reports\generated_dashboards\stock_pricing\descuentos.md) |
| Pricing por Unidad | professional | `config/dashboard_params.yml#pricing_unitario` | [pricing_unitario](reports\generated_dashboards\stock_pricing\pricing_unitario.html) | [pricing_unitario](reports\generated_dashboards\stock_pricing\pricing_unitario.md) |
| Product Mix | professional | `config/dashboard_params.yml#product_mix` | [product_mix](reports\generated_dashboards\stock_pricing\product_mix.html) | [product_mix](reports\generated_dashboards\stock_pricing\product_mix.md) |
| Stock Disponible | professional | `config/business_rules.yml#stock_disponible` | [stock_disponible](reports\generated_dashboards\stock_pricing\stock_disponible.html) | [stock_disponible](reports\generated_dashboards\stock_pricing\stock_disponible.md) |
| Stock Lento | mvp | `config/alert_thresholds.yml#stock_lento` | [stock_lento](reports\generated_dashboards\stock_pricing\stock_lento.html) | [stock_lento](reports\generated_dashboards\stock_pricing\stock_lento.md) |
| Stock Valorizado | professional | `config/dashboard_params.yml#stock_valuation` | [stock_valorizado](reports\generated_dashboards\stock_pricing\stock_valorizado.html) | [stock_valorizado](reports\generated_dashboards\stock_pricing\stock_valorizado.md) |

## uni_final
| Dashboard | Prioridad | Donde cambiar | HTML | Markdown |
|---|---|---|---|---|
| RAG Citations | governance | `config/rag_params.yml#citations` | [rag_citations](reports\generated_dashboards\uni_final\rag_citations.html) | [rag_citations](reports\generated_dashboards\uni_final\rag_citations.md) |
| RAG Corpus Coverage | governance | `config/rag_params.yml#corpus` | [rag_corpus_coverage](reports\generated_dashboards\uni_final\rag_corpus_coverage.html) | [rag_corpus_coverage](reports\generated_dashboards\uni_final\rag_corpus_coverage.md) |
| RAG Quality | mvp | `config/alert_thresholds.yml#rag_quality` | [rag_quality](reports\generated_dashboards\uni_final\rag_quality.html) | [rag_quality](reports\generated_dashboards\uni_final\rag_quality.md) |
| Text-to-SQL RAG | governance | `config/rag_sql_policy.yml#allowed_tables` | [text_to_sql_rag](reports\generated_dashboards\uni_final\text_to_sql_rag.html) | [text_to_sql_rag](reports\generated_dashboards\uni_final\text_to_sql_rag.md) |
