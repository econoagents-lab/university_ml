# Machine Learning University v1.2 · GitHub Actions Commercial Alerts

## Propósito

Yo convierto los outputs de la Intelligence Factory en alertas comerciales, quality gates y evidencia descargable para operación, UNI y demo ejecutiva.

## Outputs vigilados

```text
data/processed/scoring/ranking_operaciones_riesgo_caida.csv
reports/uni_final/RAGAS_LIKE_SUMMARY.md
reports/uni_final/FINAL_TECHNICAL_REPORT.md
docs/TRACEABILITY_TABLE_UNI.md
```

## Ejecutar local

```powershell
python scripts/66_build_all_alerts.py
python scripts/68_export_alerts_static_site.py
pytest -q
```

## Ejecutar GitHub Actions

- `Commercial KPI Digest`: alerta comercial diaria.
- `RAG Quality Gate`: calidad del asistente RAG.
- `UNI Delivery Readiness`: checklist de entrega final.
- `CRM Full Runner Self-Hosted Lenovo`: corrida real con Lenovo.
- `Railway API Smoke and Alert`: salud de API desplegada.
- `Publish Alerts Static Site`: HTML simple para GitHub Pages.

## Lenovo vs Railway

Yo uso Lenovo para correr CRM real y Railway para exponer API/dashboard. GitHub Actions se convierte en el centro de alertas y evidencia.

## Seguridad

No incluyo `.env`, credenciales ni datos personales sensibles. Usa GitHub Secrets para tokens/webhooks y self-hosted runner para data privada.
