# Capacity Prioritization Review v2.7

## Diagnóstico corregido

La versión anterior podía clasificar casi toda la cola como P0/P1. Eso no prioriza: abruma.

## Nueva regla

- P0: top 30 operaciones por valor/riesgo para actuar hoy.
- P1: siguientes 70 operaciones para actuar en 48h.
- P2: siguientes 200 para monitoreo operativo.
- P3: backlog.

## Resultado actual

```json
{
  "total_operaciones": 763,
  "daily_capacity": 30,
  "priority_counts": {
    "P3_backlog": 463,
    "P2_monitor_72h": 200,
    "P1_next_48h": 70,
    "P0_top_capacity_today": 30
  },
  "p0_p1_operaciones": 100,
  "p0_p1_valor_en_riesgo": 5297247.93
}
```

## Decisión de producto

El dashboard público y la cola operativa deben hablar de capacidad, no de urgencia infinita. El valor del sistema es decidir qué se puede ejecutar primero.
