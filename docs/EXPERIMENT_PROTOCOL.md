# Experiment Protocol · Machine Learning University

## 1. Principio

El modelo es un profesor. El experimento es el examen. La producción es el mundo real.

---

## 2. Secuencia obligatoria

1. Definir pregunta económica.
2. Declarar grano de tabla.
3. Declarar target.
4. Declarar horizonte temporal.
5. Separar features permitidas y prohibidas.
6. Construir baseline.
7. Entrenar modelo simple.
8. Evaluar con validación temporal si hay suficientes datos.
9. Analizar errores.
10. Generar model card.
11. Publicar API o batch scoring.
12. Registrar feedback.

---

## 3. Baselines aceptados

- Regla por días en tubería.
- Regla por cuota inicial.
- Regla por precio alto.
- Regla combinada.

El modelo ML debe superar al baseline para justificar complejidad.

---

## 4. Split recomendado

Para datos inmobiliarios históricos, preferir validación temporal:

```text
train = meses antiguos
validation = meses intermedios
test = meses recientes
```

Si aún no hay suficientes datos, usar `train_test_split` educativo, documentando la limitación.

---

## 5. Registro mínimo de experimento

```text
experiment_id
fecha_entrenamiento
dataset_version
filas_entrenamiento
target_rate
features
modelo
metricas
thresholds
comentarios
```

---

## 6. Criterio de avance

Un experimento puede avanzar a API si:

- no usa features prohibidas;
- supera baseline en métrica principal;
- tiene model card;
- genera predicciones interpretables;
- tiene decisión por umbral;
- existe plan de feedback.
