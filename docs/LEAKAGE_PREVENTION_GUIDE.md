# Leakage Prevention Guide

## La puerta prohibida del castillo

Un modelo con leakage parece inteligente, pero solo está mirando el final del expediente antes de rendir el examen.

## Regla central

> Una feature solo puede usarse si existía antes o durante `fecha_snapshot`.

---

## 1. Columnas prohibidas por defecto

```text
fecha_caida
motivo_caida
estado_final
fecha_firma futura
fecha_minuta futura
fecha_anulacion futura
monto_pagado posterior al snapshot
estado_cobranza posterior al snapshot
comentarios escritos después del resultado
```

---

## 2. Preguntas para cada feature

1. ¿Existía antes de que el negocio tomara la decisión?
2. ¿Se habría visto en producción?
3. ¿Es una consecuencia directa del target?
4. ¿Está actualizada por un proceso posterior?
5. ¿Tiene fecha de captura o fecha de corte?

Si alguna respuesta amenaza el tiempo, se excluye.

---

## 3. Ejemplos inmobiliarios

| Variable | ¿Permitida? | Razón |
|---|---|---|
| dias_en_tuberia | Sí | Se conoce al momento del snapshot |
| tiene_cuota_inicial hasta snapshot | Sí | Es información disponible antes de decidir |
| motivo_caida | No | Solo existe después de caer |
| fecha_caida | No | Es el evento que intentas predecir |
| fecha_minuta futura | No | Revela el futuro |
| asesor | Sí | Existe desde la operación |
| proyecto | Sí | Existe desde la operación |
| historial del proyecto calculado antes del snapshot | Sí | Es contexto histórico válido |

---

## 4. Señales de alarma

- Accuracy demasiado alta sin explicación.
- Una variable domina el modelo y parece describir el resultado.
- El modelo funciona perfecto en histórico y mal en producción.
- Las fechas de features no están controladas.
- La tabla gold mezcla eventos anteriores y posteriores sin `fecha_snapshot`.

---

## 5. Mini examen

1. ¿Por qué `motivo_caida` no debe usarse como feature?
2. ¿Cuál es la diferencia entre `fecha_evento` y `fecha_snapshot`?
3. Diseña una versión válida de `total_pagado` para evitar leakage.
4. ¿Qué harías si una feature no tiene fecha de captura?
