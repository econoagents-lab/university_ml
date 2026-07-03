from __future__ import annotations

from .document import RagDocument, RagChunk


def split_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    """
    Yo divido el texto en fragmentos con solapamiento para mejorar la recuperación semántica.
    """
    text = " ".join((text or "").split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def chunk_documents(documents: list[RagDocument], chunk_size: int = 900, overlap: int = 120) -> list[RagChunk]:
    """
    Yo convierto documentos completos en fragmentos citables.
    """
    chunks: list[RagChunk] = []
    for doc in documents:
        for idx, text in enumerate(split_text(doc.text, chunk_size=chunk_size, overlap=overlap)):
            chunks.append(RagChunk(
                chunk_id=f"{doc.doc_id}__chunk_{idx:03d}",
                doc_id=doc.doc_id,
                text=text,
                source_path=doc.source_path,
                title=doc.title,
                metadata={**doc.metadata, "chunk_index": idx},
            ))
    return chunks
