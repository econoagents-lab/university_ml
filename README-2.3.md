# Machine Learning University v2.3 · Client Proposal & Contract Automation

Sistema operativo comercial inmobiliario productizado con automatización de propuestas por cliente, contrato de métricas, alcance, pricing sugerido, onboarding y plan de implementación de 30 días.

## Ejecutar

```powershell
python scripts/120_run_v23_client_proposal_and_contract_automation.py
pytest -q
uvicorn api.main:app --reload
```

## Artefactos principales

- `reports/client_proposals/proposal_index.html`
- `reports/client_proposals/CLIENT_PROPOSAL_INDEX.md`
- `reports/client_proposals/<tenant_id>/proposal.md`
- `reports/client_proposals/<tenant_id>/metric_contract.yml`
- `reports/client_proposals/<tenant_id>/implementation_scope.md`
- `reports/client_proposals/<tenant_id>/onboarding_checklist.md`
- `reports/client_proposals/<tenant_id>/thirty_day_plan.md`
- `reports/client_proposals/<tenant_id>/pricing_summary.json`

## Principio

No vendo dashboards. Vendo una fábrica de decisiones: datos confiables, métricas contratadas, alertas accionables, RAG con evidencia y feedback que aprende.
