# Prueba local de reglas inferidas con `procesos.parquet`

Esta prueba se ejecutó contra el `procesos.parquet` disponible en el entorno de trabajo, sin incluir ese parquet dentro del ZIP.

## Resultado

```json
{
  "rows": 4609,
  "separaciones_validas": 1828,
  "ventas_minutas_validas": 370,
  "caidas_validas": 946,
  "familias_unidad": {
    "departamento": 3673,
    "estacionamiento": 827,
    "deposito": 106,
    "local": 3
  },
  "gold_rows": 3846,
  "target_rate": 0.03380135205408216,
  "ready_for_training": true
}
```

## Interpretación

- Las reglas inferidas encontraron separaciones, ventas/minutas y caídas suficientes para construir una primera gold table.
- El target `caida_30d` quedó alrededor de 3.38%, lo que confirma que el problema está desbalanceado.
- Por eso, en evaluación, `accuracy` no debe ser la métrica principal. El primer criterio debe priorizar recall de caídas, precision operativa y valor económico en riesgo.
- La columna `fecha_caida` puede existir en la tabla gold para auditoría y construcción del target, pero nunca debe entrar a `X`. El guardián `build_model_matrix()` la excluye.

## Acción recomendada

Usar v0.4 como borrador operativo, corregir reglas en `TODO_NEXT_INPUT_FILLED_FROM_HISTORY.md`, y luego congelar v0.5 como reglas oficiales.
