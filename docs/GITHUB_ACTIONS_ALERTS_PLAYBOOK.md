# v1.2 · GitHub Actions Commercial Alerts Playbook

## Escena

Yo ya no quiero que los KPIs duerman en archivos. Quiero que cada ranking, reporte o evaluación se convierta en una alerta amigable, accionable y auditable.

## Qué automatizo

| Workflow | Propósito | Output |
|---|---|---|
| `commercial_kpi_digest.yml` | Yo leo el ranking de riesgo y genero alerta ejecutiva | `reports/alerts/EXECUTIVE_KPI_DIGEST.md` |
| `rag_quality_gate.yml` | Yo valido si el asistente RAG está listo para demo | `reports/alerts/RAGAS_ALERT.md` |
| `uni_delivery_readiness.yml` | Yo valido trazabilidad y entregables UNI | `reports/alerts/UNI_READINESS_ALERT.md` |
| `intelligence_factory_alerts_all.yml` | Yo ejecuto todas las alertas juntas | `reports/alerts/ALERTS_MANIFEST.md` |
| `crm_full_runner_self_hosted.yml` | Yo corro CRM real desde mi Lenovo self-hosted | artifacts CRM + alertas |
| `railway_api_smoke_and_alert.yml` | Yo verifico que la API desplegada en Railway responda | `reports/alerts/RAILWAY_SMOKE.md` |
| `publish_alerts_static_site.yml` | Yo publico las alertas como sitio estático | GitHub Pages |

## Uso recomendado

1. Yo ejecuto `intelligence_factory_alerts_all.yml` para revisar el estado general.
2. Yo uso `commercial_kpi_digest.yml` todos los días útiles antes de la reunión comercial.
3. Yo uso `rag_quality_gate.yml` antes de presentar UNI o vender la demo.
4. Yo uso `crm_full_runner_self_hosted.yml` cuando necesito data CRM real desde mi Lenovo.
5. Yo uso `railway_api_smoke_and_alert.yml` cuando el sistema ya está desplegado.

## Archivos protegidos

Yo nunca subo `.env`, credenciales, DNI, teléfonos ni exports con PII. Para GitHub uso `sample_safe`, artifacts anonimizados y secrets.
