from __future__ import annotations

from pathlib import Path
import json
from .ingest import load_corpus
from .chunking import chunk_documents
from .embeddings import create_embedding_model
from .vector_store_faiss import LocalVectorStore
from .retriever import retrieve_with_expansion
from .generator import generate_grounded_answer, RagAnswer
from .guardrails import apply_input_guardrails


class EconomicRagPipeline:
    """
    Yo orquesto el RAG económico-inmobiliario: corpus, chunks, embeddings, recuperación, guardrails y respuesta con citas.
    """
    def __init__(self, corpus_dir: str | Path = "corpus/safe", prefer_semantic_embeddings: bool = False):
        self.corpus_dir = Path(corpus_dir)
        self.prefer_semantic_embeddings = prefer_semantic_embeddings
        self.documents = []
        self.chunks = []
        self.embedding_model = None
        self.vector_store = None

    def build(self):
        """
        Yo construyo el índice RAG desde el corpus seguro.
        """
        self.documents = load_corpus(self.corpus_dir)
        self.chunks = chunk_documents(self.documents)
        self.embedding_model = create_embedding_model(prefer_semantic=self.prefer_semantic_embeddings)
        bundle = self.embedding_model.fit_transform([chunk.text for chunk in self.chunks])
        self.vector_store = LocalVectorStore(self.chunks, bundle.vectors, bundle.model_name)
        self.vector_store.save_metadata("rag/index")
        return self

    def ask(self, question: str, top_k: int = 5) -> RagAnswer:
        """
        Yo respondo una pregunta con guardrails y evidencia recuperada.
        """
        guard = apply_input_guardrails(question)
        if not guard.allowed:
            return RagAnswer(
                question=question,
                answer="No puedo responder esa solicitud porque pide información sensible o intenta vulnerar las instrucciones del sistema.",
                contexts=[],
                citations=[],
                refused=True,
                refusal_reason=guard.reason,
            )
        if self.vector_store is None or self.embedding_model is None:
            self.build()
        chunks = retrieve_with_expansion(guard.sanitized_text, self.embedding_model, self.vector_store, top_k=top_k)
        return generate_grounded_answer(guard.sanitized_text, chunks)

    def save_manifest(self, path: str | Path = "rag/index/rag_manifest.json") -> Path:
        """
        Yo guardo la metadata del RAG para trazabilidad académica y técnica.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "corpus_dir": str(self.corpus_dir),
            "documents": len(self.documents),
            "chunks": len(self.chunks),
            "embedding_model": getattr(self.vector_store, "embedding_model_name", None),
            "techniques": ["citations", "guardrails", "multi_query_expansion", "light_reranking", "text_to_sql"],
        }
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
