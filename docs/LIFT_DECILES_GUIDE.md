# Guía de Lift por Deciles

## Intuición

El modelo no debe ser juzgado solo como un examen académico. Debe ser juzgado como una lista de llamadas: si el jefe comercial solo puede revisar 50 operaciones, las primeras 50 deben concentrar más riesgo real que una lista aleatoria.

## Qué es lift

Lift compara la tasa de caída en un grupo priorizado contra la tasa promedio histórica.

```text
lift_decile = tasa_caida_decile / tasa_caida_global
```

Si el top decile tiene lift 2.0, significa que ese grupo concentra el doble de caídas que el promedio.

## Decisión comercial

| Decil | Uso operativo |
|---|---|
| 1 | Comité comercial diario / seguimiento inmediato |
| 2-3 | Seguimiento del asesor en 24-48 horas |
| 4-6 | Monitoreo semanal |
| 7-10 | Seguimiento estándar |

## Señal mínima de valor

Para un MVP, esperamos que el primer decil tenga lift > 1.0. Si además top 20% supera claramente el promedio, el ranking ya sirve para priorización.
