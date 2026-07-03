# Executive Decision Brief - Riesgo de Caída v1.0

## Estado operativo

La cola de decisión convierte el scoring de riesgo de caída en una lista priorizada por responsable, SLA y valor esperado en riesgo.

## KPIs

- Operaciones activas en cola: 2
- Valor total esperado en riesgo: S/ 122,000
- Riesgo promedio: 0.370
- P0 intervenir hoy: 1
- P1 24 horas: 0
- Valor P0/P1: S/ 110,000
- Proyecto principal por valor en riesgo: Proyecto Aurora (S/ 110,000)
- Asesor principal por valor en riesgo: Asesor Uno (S/ 110,000)

## Decisión recomendada

1. Revisar diariamente P0 y P1.
2. Registrar acción tomada en feedback loop.
3. Comparar caídas reales versus operaciones intervenidas.
4. No presentar el modelo como oráculo: presentarlo como sistema de priorización gobernado.

## Output operativo

- reports/dashboard/decision_queue_riesgo_caida.csv
- reports/dashboard/decision_dashboard_payload.json
- reports/dashboard/DECISION_DASHBOARD_RIESGO_CAIDA.html
