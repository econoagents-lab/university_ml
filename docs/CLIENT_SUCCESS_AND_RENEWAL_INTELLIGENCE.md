# v2.5 · Client Success & Renewal Intelligence

Este release convierte la venta e implementación en una máquina de customer success:

```text
implementación iniciada
→ avance por hitos
→ adopción del tenant
→ salud del proyecto
→ riesgo de churn
→ oportunidades de upsell
→ renovación / referido
```

## Ejecutar

```powershell
python scripts/128_run_v25_client_success_and_renewal_intelligence.py
pytest -q tests/test_client_success_and_renewal_intelligence.py
uvicorn api.main:app --reload
```

## Outputs

```text
reports/client_success/client_success_index.html
reports/client_success/CLIENT_SUCCESS_AND_RENEWAL_INTELLIGENCE.md
reports/client_success/<tenant>/success_health.html
reports/client_success/<tenant>/renewal_plan.html
reports/client_success/<tenant>/client_success_package.json
```

## Privacidad

No se publican PII ni información sensible. El motor trabaja por tenant, módulos, hitos, adopción, salud y renovación. El motor trabaja por tenant, módulos, hitos, adopción, salud y renovación.
