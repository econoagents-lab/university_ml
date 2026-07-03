# Model Brief · Riesgo de Caída

## 1. Pregunta económica

¿Qué separaciones activas tienen mayor probabilidad de caer en los próximos 30 días?

## 2. Usuario dueño

- Jefe comercial.
- Gerencia comercial.
- Asesor responsable.

## 3. Decisión que habilita

Priorizar seguimiento comercial, renegociación, intervención gerencial o validación financiera antes de que la operación caiga.

## 4. Unidad de análisis

Una operación inmobiliaria observada en un snapshot posterior a la separación.

```text
Grano recomendado = codigo_proforma + codigo_unidad + fecha_snapshot
```

## 5. Target

```text
caida_30d = 1 si la operación cae dentro de los 30 días posteriores al snapshot.
caida_30d = 0 si no cae dentro de ese horizonte.
```

## 6. Momento de predicción

El modelo solo puede usar información disponible hasta `fecha_snapshot`.

Ejemplos de snapshots:

- día 7 después de separación;
- día 14 después de separación;
- día 30 después de separación.

## 7. Features permitidas v0.3

```text
proyecto
asesor
medio_captacion
canal_agrupado
dormitorios
precio_departamento
dias_en_tuberia
tiene_cuota_inicial
cambios_unidad
interacciones_ult_7d
descuento_pct
```

## 8. Features prohibidas

```text
fecha_caida
motivo_caida
estado_final
fecha_firma futura
fecha_minuta futura
monto_pagado posterior al snapshot
cualquier variable registrada después de fecha_snapshot
```

## 9. Baseline obligatorio

Antes de entrenar un modelo, se debe comparar contra esta regla mínima:

```text
Riesgo alto si:
- dias_en_tuberia >= 30, o
- no tiene cuota inicial, o
- precio_departamento es alto, o
- hubo cambios de unidad.
```

## 10. Métrica principal

**Recall de caídas.**

Justificación: en este caso, el error más peligroso es no detectar una operación que sí caerá.

## 11. Métricas secundarias

- Precision.
- F1.
- ROC AUC.
- PR AUC.
- Matriz de confusión.
- Valor esperado en riesgo.

## 12. Matriz de acción

| Nivel | Umbral | Acción | Responsable | Plazo |
|---|---:|---|---|---|
| Bajo | < 0.40 | Seguimiento estándar | Asesor | Semana |
| Medio | 0.40 a 0.69 | Contacto priorizado | Asesor + coordinación | 24 horas |
| Alto | >= 0.70 | Escalar y diseñar intervención | Jefe comercial | Hoy |

## 13. Feedback loop

Después de cada score se debe registrar:

```text
codigo_proforma
fecha_score
riesgo_predicho
accion_tomada
responsable
fecha_contacto
resultado_30d
caida_real
minuta_real
comentario
```

## 14. Criterio de éxito

El modelo no se considera exitoso por tener una métrica bonita. Se considera exitoso si:

1. Detecta más operaciones riesgosas que el baseline.
2. Permite priorizar seguimiento.
3. Reduce caídas o acelera minutas frente a un grupo comparable.
4. Genera una lista accionable entendida por el equipo comercial.
