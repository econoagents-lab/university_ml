# Lift Report - Riesgo de Caída v0.6

## Lectura ejecutiva

El objetivo de este reporte no es volver a preguntar si el modelo es perfecto. La pregunta correcta es si el ranking concentra más caídas reales en los primeros deciles que una selección aleatoria.

## Métricas clave

| Métrica | Valor |
|---|---:|
| Filas test | 880 |
| Tasa caída test | 8.75% |
| ROC AUC test | 0.517 |
| Average Precision test | 0.115 |
| Tasa caída top decil | 9.09% |
| Lift top decil | 1.04x |
| Captura top 20% | 18.18% |

## Interpretación

- Si el lift del primer decil es mayor a 1.0x, el modelo ordena mejor que una lista aleatoria.
- Si el top 20% captura una proporción relevante de caídas, el ranking sirve para priorización comercial.
- Si el lift es débil, el siguiente trabajo no es cambiar de algoritmo primero, sino mejorar features de comportamiento, contacto, banco y cuota inicial.

## Decisión comercial recomendada

1. Revisar diariamente el decil 1.
2. Asignar SLA de 24 horas al decil 1 y 48 horas a deciles 2-3.
3. Registrar feedback por acción tomada.
4. Medir resultados a 7 y 30 días.
