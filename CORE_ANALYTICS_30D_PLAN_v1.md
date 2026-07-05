# CORE_ANALYTICS_30D_PLAN_v1

## La escena mental

Este plan cierra el showroom y baja al sótano de la fábrica: contratos, cohortes, stock, cobranza, modelo, feedback y valor económico.  
La meta no es producir más pantallas; la meta es producir evidencia que gerencia no pueda discutir fácilmente.

## Objetivo ejecutivo

Durante 30 días, fortalecer el core analítico para que el sistema pase de demo poderosa a motor económico defendible.

**Foco:**
1. Marts reales.
2. Cohortes.
3. Stock y cobranza.
4. Recalibración del modelo.
5. Feedback real.
6. Scorecard de defendibilidad económica.

## Ruta privada recomendada

Si tus parquets raw están en:

```powershell
C:\Repos\freelance\ml_university_ready\data\raw\sperant
```

úsalo como:

```powershell
$env:MLU_PRIVATE_DATA_DIR="C:\Repos\freelance\ml_university_ready\data\raw\sperant"
```

## Entregables principales

- `tables/30_day_roadmap.csv`
- `tables/metric_contract_matrix.csv`
- `tables/analytics_improvement_backlog.csv`
- `tables/model_audit_findings.csv`
- `tables/inputs_to_confirm.csv`
- `config/core_analytics_params.yml`
- `contracts/*.yml`
- `reports/CORE_ANALYTICS_30D_EXECUTIVE_BRIEF_TEMPLATE.md`
- `VALUE_DEFENSIBILITY_SCORECARD_TEMPLATE.md`
- `CORE_ANALYTICS_30D_PLAN_v1.xlsx`

## Decisión recomendada

No avanzar con más branding ni más tenants hasta que el core analítico tenga:

- 70% de métricas core en estado oficial.
- 20% proxy declarado.
- 10% demo/bloqueado/retirar como máximo.
- Modelo evaluado por lift/capacidad, no por accuracy.
- Feedback real 7d/30d.
- Stock y cobranza conectados a decisión económica.

## Comando operativo sugerido

```powershell
python scripts/run_core_analytics_30d.py --private-data-dir "C:\Repos\freelance\ml_university_ready\data\raw\sperant"
```
