# Quickstart v1.2

```powershell
python scripts/66_build_all_alerts.py
python scripts/61_build_commercial_alert_digest.py
python scripts/63_validate_ragas_quality_gate.py
python scripts/62_validate_uni_readiness.py
python scripts/68_export_alerts_static_site.py
pytest -q
```

## Workflows principales

```text
.github/workflows/commercial_kpi_digest.yml
.github/workflows/rag_quality_gate.yml
.github/workflows/uni_delivery_readiness.yml
.github/workflows/intelligence_factory_alerts_all.yml
.github/workflows/crm_full_runner_self_hosted.yml
.github/workflows/railway_api_smoke_and_alert.yml
.github/workflows/publish_alerts_static_site.yml
```

## Salidas

```text
reports/alerts/EXECUTIVE_KPI_DIGEST.md
reports/alerts/RAGAS_ALERT.md
reports/alerts/UNI_READINESS_ALERT.md
reports/alerts/ALERTS_MANIFEST.md
site/alerts/index.html
```

## Validación v1.2.1

```powershell
python scripts/66_build_all_alerts.py
python scripts/68_export_alerts_static_site.py
pytest -q
```

En GitHub Actions, `RAG Quality Gate` ahora es amigable por defecto: publica alertas y artifacts sin fallar, salvo que ejecutes manualmente con `fail_on_alert=true`.
