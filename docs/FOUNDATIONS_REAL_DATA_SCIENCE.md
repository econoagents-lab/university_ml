# Foundations Real Data Science

## Machine Learning University · Capa de fundamentos v0.3

> No se modela para decorar un dashboard. Se modela para cambiar una decisión, proteger dinero y aprender del resultado.

Este documento define el núcleo mental de la Universidad. Antes de tocar `fit()`, el alumno debe poder explicar el sistema que va a construir.

---

## 1. Las cinco leyes personales

1. **No modelo sin pregunta económica.**
   - Todo modelo nace para responder una pregunta de negocio.
   - Ejemplo: “¿qué separaciones activas podrían caer en los próximos 30 días?”

2. **No predicción sin momento de decisión.**
   - El score debe llegar antes de que el negocio pueda actuar.
   - Si se predice después de la caída, no es inteligencia; es autopsia.

3. **No feature sin verificar si existía antes del target.**
   - Una variable posterior al evento introduce leakage.
   - El modelo no debe ver el futuro.

4. **No métrica sin costo de error.**
   - Accuracy sola no basta.
   - En riesgo de caída importa especialmente el costo de no detectar una operación que sí cae.

5. **No score sin responsable, acción y feedback.**
   - Un score sin acción es un número huérfano.
   - Un modelo serio termina en responsable, tarea, fecha y medición del resultado.

---

## 2. La secuencia correcta de Data Science real

```text
pregunta económica
→ contrato de datos
→ grano de tabla
→ target
→ features válidas
→ baseline
→ modelo
→ evaluación
→ interpretación
→ API/dashboard
→ decisión
→ feedback
```

---

## 3. Los siete fundamentos

### 3.1 Negocio

Preguntas obligatorias:

- ¿Qué decisión habilita el modelo?
- ¿Quién usará el resultado?
- ¿Qué error cuesta más?
- ¿En qué momento debe llegar la predicción?
- ¿Qué dinero está en juego?

### 3.2 SQL y modelado analítico

El alumno debe dominar:

- JOINs y CTEs.
- Window functions.
- Grano de tabla.
- Llaves naturales y llaves técnicas.
- Bronze / Silver / Gold.
- Snapshots temporales.
- Detección de duplicados.

### 3.3 Estadística aplicada

Prioridad:

- Distribuciones.
- Outliers.
- Correlación.
- Desbalance de clases.
- Falsos positivos y falsos negativos.
- Validación temporal.
- Intervalos de confianza.

### 3.4 Machine Learning como sistema

Orden recomendado:

```text
baseline rule
→ logistic regression
→ decision tree
→ random forest
→ gradient boosting
→ calibración
→ interpretabilidad
→ API
```

### 3.5 Feature engineering

Las mejores variables nacen del negocio:

- días en tubería;
- cuota inicial registrada;
- precio del departamento;
- descuento;
- asesor;
- proyecto;
- canal;
- cambios de unidad;
- interacciones recientes;
- historial de conversión del asesor;
- historial de caída del proyecto;
- velocidad comercial del proyecto.

### 3.6 MLOps básico

Artefactos mínimos:

```text
models/riesgo_caida_model.joblib
models/feature_columns.json
models/model_card.md
contracts/*.yml
data/processed/gold/riesgo_caida_training.parquet
reports/evaluation_report.md
api/main.py
```

### 3.7 Comunicación ejecutiva

Formato de explicación:

```text
Qué predice:
    Riesgo de caída en próximos 30 días.

Para quién:
    Jefe comercial / asesores / gerencia.

Qué acción habilita:
    Priorizar seguimiento y proteger venta en riesgo.

Qué mide:
    Probabilidad de caída y valor esperado en riesgo.

Cómo aprende:
    Observa separaciones históricas, snapshots y resultados posteriores.
```

---

## 4. Checklist antes de entrenar

- [ ] Pregunta económica escrita.
- [ ] Usuario dueño definido.
- [ ] Decisión concreta definida.
- [ ] Grano de tabla declarado.
- [ ] Target declarado.
- [ ] Horizonte temporal declarado.
- [ ] Features permitidas declaradas.
- [ ] Features prohibidas declaradas.
- [ ] Métrica principal declarada.
- [ ] Costo de falso positivo y falso negativo declarado.
- [ ] Acción por umbral declarada.
- [ ] Feedback esperado declarado.

---

## 5. Mini examen

1. Explica por qué `fecha_caida` no puede ser feature si estás prediciendo caída.
2. Define el grano correcto de una tabla de entrenamiento de riesgo de caída.
3. ¿Por qué una accuracy alta puede ser inútil en un problema con pocas caídas?
4. ¿Qué decisión concreta cambia si el score de caída supera 70%?
5. Diseña una feature válida que exista antes del momento de predicción.
