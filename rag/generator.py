from __future__ import annotations

import re
from dataclasses import dataclass
from .document import RagChunk
from .citations import build_citations


@dataclass
class RagAnswer:
    question: str
    answer: str
    contexts: list[str]
    citations: list[str]
    refused: bool = False
    refusal_reason: str = ""


def _select_sentences(question: str, chunks: list[RagChunk], max_sentences: int = 5) -> list[str]:
    """
    Yo selecciono oraciones con mayor superposición con la pregunta para construir una respuesta grounded local.
    """
    q_terms = set(re.findall(r"\w+", question.lower()))
    candidates = []
    for chunk in chunks:
        sentences = re.split(r"(?<=[.!?])\s+", chunk.text)
        for sent in sentences:
            s_terms = set(re.findall(r"\w+", sent.lower()))
            if not sent.strip():
                continue
            score = len(q_terms & s_terms) / max(1, len(q_terms))
            candidates.append((score + chunk.score, sent.strip()))
    candidates.sort(reverse=True, key=lambda x: x[0])
    selected = []
    seen = set()
    for _, sentence in candidates:
        if sentence not in seen:
            selected.append(sentence)
            seen.add(sentence)
        if len(selected) >= max_sentences:
            break
    return selected


def generate_grounded_answer(question: str, chunks: list[RagChunk]) -> RagAnswer:
    """
    Yo genero una respuesta basada únicamente en los fragmentos recuperados.
    Si no tengo contexto suficiente, lo digo en vez de inventar.
    """
    if not chunks:
        return RagAnswer(
            question=question,
            answer="No tengo evidencia suficiente en el corpus recuperado para responder esta pregunta.",
            contexts=[],
            citations=[],
        )
    selected = _select_sentences(question, chunks)
    if not selected:
        return RagAnswer(
            question=question,
            answer="No tengo evidencia suficiente en el corpus recuperado para responder esta pregunta.",
            contexts=[c.text for c in chunks],
            citations=build_citations(chunks),
        )
    body = " ".join(selected)
    answer = (
        "Con la evidencia recuperada, mi lectura es la siguiente: "
        + body
        + "\n\nAcción recomendada: revisar la evidencia citada, validar si aplica al periodo/proyecto consultado y convertir la respuesta en una decisión con responsable."
    )
    return RagAnswer(
        question=question,
        answer=answer,
        contexts=[c.text for c in chunks],
        citations=build_citations(chunks),
    )
