# Experimentation Causal Impact Lab · v1.8

## Qué resuelve

Yo convierto una cola de riesgo en un experimento operativo. El objetivo no es solo intervenir operaciones P0/P1, sino medir si esa intervención reduce caídas, aumenta resultados positivos y protege valor económico.

## Flujo

```text
ranking riesgo → cola segura → asignación tratamiento/control → acción comercial → resultado 7d/30d → impacto → política de escalamiento
```

## Diseño recomendado

- P0: tratamiento obligatorio por ética comercial. No se retiene una operación crítica si ya se considera urgente.
- P1: holdout control estratificado para medir impacto.
- P2/P3: no elegibles en MVP, sirven como monitoreo.

## Métricas

- tasa negativa 30d tratamiento vs control.
- tasa positiva 30d tratamiento vs control.
- contact rate.
- valor esperado en riesgo tratado.
- valor salvado proxy.

## Limitación honesta

Este MVP produce impacto descriptivo. Para inferencia causal fuerte se necesita asignación experimental sostenida, cumplimiento de tratamiento y muestra suficiente por brazo.
