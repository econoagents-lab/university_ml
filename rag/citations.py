from __future__ import annotations

from .document import RagChunk


def format_citation(chunk: RagChunk, index: int) -> str:
    """
    Yo construyo una cita legible con título, fuente y chunk_id.
    """
    return f"[{index}] {chunk.title or chunk.doc_id} · {chunk.source_path} · {chunk.chunk_id}"


def build_citations(chunks: list[RagChunk]) -> list[str]:
    """
    Yo preparo las citas que acompañan cada respuesta del asistente.
    """
    return [format_citation(chunk, i + 1) for i, chunk in enumerate(chunks)]
