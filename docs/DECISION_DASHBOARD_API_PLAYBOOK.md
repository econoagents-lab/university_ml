# Decision Dashboard API Playbook v0.9

## Escena mental

El modelo ya no entrega un score: entrega una cola de mando.

## Objetivo de negocio

Convertir el ranking de riesgo de caída en una rutina diaria para jefe comercial, asesores y gerencia.

## Flujo

```text
scoring actual
→ ranking_operaciones_riesgo_caida
→ decision_queue
→ KPIs / action plan / dashboard HTML
→ feedback loop
→ evaluación de intervención
```

## Rutina diaria recomendada

1. Abrir `/dashboard/riesgo-caida`.
2. Revisar P0 y P1.
3. Asignar responsable.
4. Registrar acción tomada vía `/feedback/riesgo-caida`.
5. Medir resultado 7d/30d.

## Lectura correcta del modelo

El dashboard no dice “esta operación caerá”. Dice: “esta operación merece prioridad porque combina riesgo, valor económico y urgencia operativa”.
