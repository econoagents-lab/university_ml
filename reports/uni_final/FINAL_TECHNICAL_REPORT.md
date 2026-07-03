# Reporte técnico final UNI

## Sistema

Yo construí un asistente RAG económico-inmobiliario con corpus seguro, hipótesis económicas, table-to-text, guardrails, Text-to-SQL y evaluación RAGAS-like.

## Métricas

- Faithfulness proxy promedio: 0.844
- Answer relevance proxy promedio: 0.204
- Context relevance proxy promedio: 0.600
- Tasa de rechazo en preguntas trampa: 0.667

## Técnicas avanzadas

1. Citación obligatoria.
2. Guardrails PII y prompt injection.
3. Multi-query expansion.
4. Re-ranking liviano.
5. Text-to-SQL controlado.

## Limitaciones

Yo uso métricas offline inspiradas en RAGAS para reproducibilidad. En producción académica con API disponible, puedo ejecutar la librería `ragas` oficial.
