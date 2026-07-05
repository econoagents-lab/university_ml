# Executive Value Brief v2.7

## Decisión de auditoría

Se congela la expansión superficial y se prioriza el core: marts reales, cohortes, stock/cobranza, modelo recalibrado, ranking por capacidad y feedback real.

## Qué cambia en esta versión

1. P0/P1 deja de ser umbral bruto y pasa a ser capacidad accionable.
2. El modelo se comunica como ranking gobernado, no como oráculo.
3. El dashboard público se anonimiza por defecto.
4. La demo se reduce a una historia ejecutiva de valor.
5. Se crea scorecard de defendibilidad económica.

## KPIs corregidos

- Operaciones evaluadas: **763**
- Valor total en riesgo: **S/ 21,232,580**
- P0/P1 accionable: **100**
- Valor P0/P1: **S/ 5,297,248**
- Riesgo promedio: **0.398**

## Veredicto del modelo

- ROC AUC: **0.517**
- Average precision: **0.115**
- Lift top decile: **1.04x**
- Claim recomendado: **modelo_apto_solo_como_ranking_debil_y_gobernado**

## Scorecard de defendibilidad

| Módulo | Estado | Evidencia | Riesgo |
|---|---|---|---|
| Marts reales | parcial | `reports/real_marts/REAL_MART_EXPANSION.md` | Falta validar reglas oficiales con gerencia. |
| Cohortes | planificado | `CORE_ANALYTICS_30D_PLAN_v1` | Todavía debe ejecutarse sobre CRM privado. |
| Modelo riesgo | débil_gobernado | `reports/modeling/lift_metrics.json` | No vender como alta precisión. |
| Ranking accionable | mejorado | `data/processed/core_value_hardening/capacity_risk_queue_safe.csv` | Ahora depende de capacidad comercial. |
| Feedback real | estructura | `data/processed/action_feedback/feedback_events_safe.csv` | Falta captura sostenida 7d/30d. |
| Impacto causal | prematuro | `reports/experiments/EXPERIMENTATION_CAUSAL_IMPACT_LAB.md` | Muestra insuficiente. |
| Dashboard público | mejorado | `reports/public/DECISION_DASHBOARD_PUBLIC.html` | Debe mantenerse agregado y anonimizado. |
| Demo comercial | enfocado | `reports/core_value_hardening/EXECUTIVE_VALUE_BRIEF.html` | Reducir a historia de valor. |

## Próxima decisión

Ejecutar CORE_ANALYTICS_30D sobre CRM privado y presentar solo 6 puertas ejecutivas: brief, dashboard público, riesgo/acción, cohortes, stock/cobranza y feedback/valor.
