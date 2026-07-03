# Experiment Design Playbook - Riesgo de Caída

## Pregunta causal

¿Las operaciones priorizadas por el modelo y efectivamente intervenidas caen menos que operaciones similares con seguimiento estándar?

## Diseño MVP

Tomar top N operaciones por valor esperado en riesgo. Asignar una parte pequeña a holdout operativo sin quitar seguimiento normal. El grupo intervención recibe SLA fuerte.

## Métricas

- Caída real 30d.
- Firma/minuta 30d.
- Contacto realizado.
- Regularización de cuota inicial.
- Tiempo hasta acción.

## Guardrail

El experimento no debe negar atención comercial. Solo mide tratamiento extra.
