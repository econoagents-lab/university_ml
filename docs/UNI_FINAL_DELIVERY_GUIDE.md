# Guía de entrega UNI · v1.1

## Tesis del proyecto

Yo presento un asistente RAG económico-inmobiliario que consulta documentos, historias generadas desde tablas y marts económicos para apoyar decisiones comerciales.

## Requisitos UNI cubiertos

| Requisito | Implementación |
|---|---|
| Corpus propio real | Corpus seguro con reportes anonimizados, contratos, model card, mercado y table-to-text |
| Ingesta multiformato | `rag/ingest.py` lee MD, TXT, CSV y PDF |
| Chunking | `rag/chunking.py` |
| Embeddings | `rag/embeddings.py` con fallback TF-IDF y opción SentenceTransformers |
| Indexación FAISS | `rag/vector_store_faiss.py` con diseño compatible y fallback local |
| Recuperación top-k | `rag/retriever.py` |
| Técnicas avanzadas | citas, guardrails, multi-query, reranking, Text-to-SQL |
| Evaluación | `rag/ragas_eval.py` y `evaluation/eval_questions.csv` |
| Preguntas trampa | PII, credenciales y fuera de corpus |
| Demo | `app/gradio_app.py` |

## Qué decir si preguntan por datos reales

Yo uso datos anonimizados para la exposición. La arquitectura está preparada para CRM real, pero el entregable académico no expone PII ni credenciales.
