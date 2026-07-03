# Política de alertas comerciales

## Principio

Yo no abro alertas por ruido. Abro alertas cuando hay una decisión pendiente.

## Severidad

| Severidad | Significado | Acción |
|---|---|---|
| OK | Todo está dentro de umbrales | Yo reviso y archivo evidencia |
| Warning | Hay señal que revisar | Yo reviso antes de reunión/demo |
| Critical | Hay riesgo operativo o de entrega | Yo abro issue y asigno acción |

## Alertas críticas típicas

- No existe `ranking_operaciones_riesgo_caida.csv`.
- P0 supera el umbral crítico.
- Valor esperado en riesgo supera el umbral crítico.
- RAGAS-like no puede leerse.
- Faltan archivos obligatorios UNI.
- Railway API no responde.

## Ajuste de umbrales

Yo modifico `config/alert_thresholds.yml` cuando el negocio cambia de capacidad operativa. Si el equipo comercial solo puede revisar 30 operaciones al día, P0 crítico no puede ser 100.
