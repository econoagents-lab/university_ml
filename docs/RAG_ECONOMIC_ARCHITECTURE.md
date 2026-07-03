# Arquitectura RAG económico-inmobiliaria

```text
CRM + Mercado + Reportes + Contratos
        ↓
Marts económicos + hipótesis
        ↓
Table-to-text stories
        ↓
Corpus seguro
        ↓
Chunking + embeddings + índice vectorial
        ↓
Retriever top-k + multi-query + reranking
        ↓
Guardrails + prompt grounded + citas
        ↓
Respuesta ejecutiva + RAGAS-like evaluation
```

## Decisión clave

Yo no mando tablas crudas al LLM. Primero genero marts e historias auditables. Luego el RAG consulta esa memoria.
