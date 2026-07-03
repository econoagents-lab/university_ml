# Machine Learning University v0.6 - Feedback & Lift

## La escena

El modelo ya no es una criatura aislada. Ahora entra al circuito operativo: ranking, lift, seguimiento, feedback y aprendizaje.

## Qué cambia en v0.6

v0.5 gobernó el modelo: reglas oficiales, model-ready, anti-leakage, evaluación y scoring.
v0.6 convierte ese score en una disciplina diaria:

1. Medir si el modelo concentra caídas en los primeros deciles.
2. Traducir deciles en prioridades comerciales.
3. Crear un feedback loop para registrar acciones reales.
4. Medir si las intervenciones reducen caídas o aceleran minutas.
5. Generar un brief ejecutivo reutilizable.

## Artefactos principales

- `reports/modeling/lift_deciles.csv`
- `reports/modeling/lift_report.md`
- `reports/modeling/precision_at_k.csv`
- `data/feedback/feedback_log_template.csv`
- `data/feedback/feedback_outcomes_merged.parquet`
- `reports/executive/CEO_BRIEF_RIESGO_CAIDA_V0_6.md`
- `contracts/feedback_contract_riesgo_caida.yml`
- `contracts/lift_contract_riesgo_caida.yml`

## Lectura ejecutiva

Un modelo con ROC AUC moderado puede ser útil si ordena correctamente la cola superior de riesgo. Por eso v0.6 deja de preguntar solamente "qué tan bueno es el modelo" y empieza a preguntar:

> ¿El top 10% del ranking concentra más caídas que el promedio histórico?

Si la respuesta es sí, el modelo ya tiene valor operativo aunque todavía sea perfectible.
