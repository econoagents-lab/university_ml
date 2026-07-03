from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from .document import RagChunk


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return a_norm @ b_norm.T


class LocalVectorStore:
    """
    Yo implemento una tienda vectorial local compatible con el flujo FAISS.
    Si FAISS no está disponible, mantengo la reproducibilidad con numpy.
    """
    def __init__(self, chunks: list[RagChunk], vectors: np.ndarray, embedding_model_name: str):
        self.chunks = chunks
        self.vectors = vectors.astype("float32")
        self.embedding_model_name = embedding_model_name

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[RagChunk]:
        query_vector = query_vector.astype("float32")
        scores = _cosine_similarity(self.vectors, query_vector.reshape(1, -1)).ravel()
        order = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in order:
            chunk = self.chunks[int(idx)]
            results.append(RagChunk(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                text=chunk.text,
                source_path=chunk.source_path,
                title=chunk.title,
                metadata=chunk.metadata,
                score=float(scores[idx]),
            ))
        return results

    def save_metadata(self, output_dir: str | Path) -> Path:
        """
        Yo guardo metadata del índice para auditar qué corpus fue indexado.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "embedding_model_name": self.embedding_model_name,
            "chunks": [asdict(chunk) for chunk in self.chunks],
            "num_chunks": len(self.chunks),
        }
        path = output_dir / "vector_store_metadata.json"
        path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
