from __future__ import annotations

from collections import OrderedDict
import re
from .document import RagChunk
from .guardrails import sanitize_context

SYNONYMS = {
    "caída": ["anulación", "desistimiento", "riesgo de caída"],
    "minuta": ["venta", "firma", "cierre"],
    "tubería": ["pipeline", "operación activa", "separación pendiente"],
    "precio": ["pricing", "precio por metro cuadrado", "brecha precio"],
    "mercado": ["oferta", "competencia", "precio m2 de distrito"],
}


def expand_query(question: str) -> list[str]:
    """
    Yo genero variantes simples de la consulta para mejorar recuperación cuando el usuario usa vocabulario distinto.
    """
    variants = [question]
    lower = question.lower()
    for term, syns in SYNONYMS.items():
        if term in lower:
            for syn in syns:
                variants.append(lower.replace(term, syn))
    return list(OrderedDict.fromkeys(variants))


def lexical_rerank(question: str, chunks: list[RagChunk]) -> list[RagChunk]:
    """
    Yo reordeno fragmentos por coincidencia léxica como reranker liviano y reproducible.
    """
    terms = set(re.findall(r"\w+", question.lower()))
    reranked = []
    for chunk in chunks:
        chunk_terms = set(re.findall(r"\w+", chunk.text.lower()))
        lexical_score = len(terms & chunk_terms) / max(1, len(terms))
        chunk.score = float(chunk.score + lexical_score)
        chunk.text = sanitize_context(chunk.text)
        reranked.append(chunk)
    return sorted(reranked, key=lambda c: c.score, reverse=True)


def retrieve_with_expansion(question: str, embedding_model, vector_store, top_k: int = 5) -> list[RagChunk]:
    """
    Yo recupero contexto usando multi-query expansion y luego reordeno los fragmentos.
    """
    candidates: dict[str, RagChunk] = {}
    for query in expand_query(question):
        q_vec = embedding_model.transform([query]).vectors[0]
        for chunk in vector_store.search(q_vec, top_k=top_k):
            if chunk.chunk_id not in candidates or chunk.score > candidates[chunk.chunk_id].score:
                candidates[chunk.chunk_id] = chunk
    return lexical_rerank(question, list(candidates.values()))[:top_k]
