# Experiment Power & Policy Engine

## Qué resuelve

Yo convierto el experimento de intervención comercial en una política operativa defendible: no basta saber si el tratamiento parece funcionar; necesito saber si hay muestra suficiente, si los asesores realmente ejecutaron la acción, qué segmentos responden mejor, qué SLA conviene y cuánta capacidad comercial se requiere.

## Flujo

```text
experiment_assignment_safe.csv
→ experiment_outcomes_safe.csv
→ power analysis
→ compliance de tratamiento
→ impacto por segmento
→ SLA/capacidad
→ política de escalamiento P0/P1/P2
```

## Principio

No prometo causalidad si no hay poder estadístico ni feedback suficiente. Declaro el estado y recomiendo la siguiente acción operacional.

## Outputs

```text
data/processed/policy_engine/experiment_power_analysis.json
data/processed/policy_engine/treatment_compliance_summary.csv
data/processed/policy_engine/segment_policy_impact.csv
data/processed/policy_engine/sla_capacity_recommendations.json
data/processed/policy_engine/escalation_policy.json
reports/policy_engine/EXPERIMENT_POWER_AND_POLICY_ENGINE.md
```
