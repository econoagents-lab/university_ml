from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RagDocument:
    """
    Yo represento un documento recuperable por el RAG con texto, fuente y metadata.
    """
    doc_id: str
    text: str
    source_path: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RagChunk:
    """
    Yo represento un fragmento citables del corpus.
    """
    chunk_id: str
    doc_id: str
    text: str
    source_path: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
