# Drift Playbook

## Qué es drift

Drift es cuando el mundo que vio el modelo durante el entrenamiento deja de parecerse al mundo actual.

## Tipos

| Tipo | Pregunta |
|---|---|
| Feature drift | ¿Cambió la distribución de inputs? |
| Prediction drift | ¿Cambió la distribución del score? |
| Concept drift | ¿La relación entre inputs y caída cambió? |
| Calibration drift | ¿Un score 0.40 sigue significando 40% aproximado? |

## Acción recomendada

- PSI < 0.10: observar.
- PSI 0.10–0.25: revisar fuente, reglas y top features.
- PSI > 0.25: auditar antes de usar ranking como prioridad comercial.
