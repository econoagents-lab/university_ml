# Tabla de trazabilidad UNI

| Requisito UNI | Archivo/Celda sugerida |
|---|---|
| Ficha técnica | Notebook celda 1 |
| Corpus propio | `corpus/safe/` y `corpus/generated_stories/` |
| Ingesta multiformato | `rag/ingest.py` |
| Chunking | `rag/chunking.py` |
| Embeddings | `rag/embeddings.py` |
| FAISS/fallback vectorial | `rag/vector_store_faiss.py` |
| Recuperación top-k | `rag/retriever.py` |
| Multi-query expansion | `rag/retriever.py` |
| Re-ranking | `rag/retriever.py` |
| Guardrails | `rag/guardrails.py` |
| Citación | `rag/citations.py` |
| Text-to-SQL | `rag/text_to_sql.py` |
| Evaluación 15 preguntas | `evaluation/eval_questions.csv` |
| RAGAS-like | `rag/ragas_eval.py` |
| Interfaz | `app/gradio_app.py` |
