# Error Cost Matrix · Riesgo de Caída

## 1. Por qué esta matriz existe

Una métrica sin costo económico es un número sin dueño. Esta matriz traduce errores del modelo a consecuencias comerciales.

---

## 2. Matriz conceptual

| Realidad / Predicción | Predice bajo riesgo | Predice alto riesgo |
|---|---|---|
| No cae | Correcto: seguimiento normal | Falso positivo: seguimiento extra |
| Cae | Falso negativo: venta en riesgo no intervenida | Correcto: operación priorizada |

---

## 3. Falso positivo

El modelo marca una operación como riesgosa, pero no cae.

Costo probable:

- Tiempo comercial adicional.
- Llamada innecesaria.
- Escalamiento no requerido.

Impacto económico esperado: bajo o medio.

---

## 4. Falso negativo

El modelo marca bajo riesgo, pero la operación cae.

Costo probable:

- Venta perdida.
- Caja no materializada.
- Stock regresa al inventario.
- Pérdida de confianza gerencial.

Impacto económico esperado: alto.

---

## 5. Decisión de métrica principal

Para el MVP, la métrica principal será **Recall de caídas** porque preferimos detectar más operaciones riesgosas aunque el equipo revise algunos casos extra.

## 6. Regla de negocio inicial

```text
Si riesgo >= 0.70:
    intervenir hoy.
Si riesgo >= 0.40 y < 0.70:
    priorizar en 24 horas.
Si riesgo < 0.40:
    seguimiento estándar.
```

## 7. Parámetros que deben validarse con negocio

- Costo promedio de seguimiento extra.
- Valor promedio de venta en riesgo.
- Capacidad diaria del equipo para intervenir casos.
- Umbral máximo de falsos positivos tolerable.
- Horizonte correcto: 15, 30 o 45 días.
