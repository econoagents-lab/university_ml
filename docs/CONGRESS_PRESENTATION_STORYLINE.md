# Storyline para congreso de data science

## Tesis

No construí un notebook de predicción. Construí un sistema CRM-first de Machine Learning gobernado para priorizar riesgo de caída inmobiliaria.

## Secuencia recomendada

1. Problema económico: separaciones que caen destruyen valor comercial.
2. Fuente operacional: CRM/Sperant → parquet → gold → model-ready.
3. Diseño anti-leakage: `fecha_caida` solo para target/auditoría, nunca para X.
4. Modelo: baseline/champion/challenger.
5. Métricas: ROC, PR, matriz de confusión, lift.
6. Monitoreo: drift y calibración.
7. Registry: dataset versioning + model registry + política de retraining.
8. Acción: ranking operativo + feedback loop.
9. Resultado: el score termina en responsable, acción y medición.

## Figuras

Ver `reports/congress/CONGRESS_FIGURE_PACK.md`.
