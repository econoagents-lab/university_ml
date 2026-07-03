from __future__ import annotations

from pathlib import Path
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def _similarity(a: str, b: str) -> float:
    vec = TfidfVectorizer().fit_transform([a or "", b or ""])
    return float(cosine_similarity(vec[0], vec[1])[0, 0])


def faithfulness_proxy(answer: str, contexts: list[str]) -> float:
    """
    Yo estimo fidelidad verificando si las oraciones de la respuesta se parecen al contexto recuperado.
    Esta métrica es un fallback local inspirado en RAGAS, no reemplaza la evaluación LLM oficial.
    """
    answer_sents = _sentences(answer)
    context = " ".join(contexts)
    if not answer_sents:
        return 0.0
    supported = sum(1 for s in answer_sents if _similarity(s, context) >= 0.12)
    return supported / len(answer_sents)


def answer_relevance_proxy(question: str, answer: str) -> float:
    """
    Yo estimo relevancia de respuesta comparando pregunta y respuesta.
    """
    return _similarity(question, answer)


def context_relevance_proxy(question: str, contexts: list[str]) -> float:
    """
    Yo estimo relevancia del contexto como proporción de fragmentos con similitud suficiente frente a la pregunta.
    """
    if not contexts:
        return 0.0
    relevant = sum(1 for c in contexts if _similarity(question, c) >= 0.08)
    return relevant / len(contexts)


def evaluate_answers(records: list[dict], output_dir: str | Path = "reports/uni_final") -> pd.DataFrame:
    """
    Yo evalúo respuestas con métricas locales inspiradas en RAGAS y genero reportes reproducibles.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for record in records:
        contexts = record.get("contexts", [])
        rows.append({
            "question": record.get("question", ""),
            "answer": record.get("answer", ""),
            "faithfulness_proxy": round(faithfulness_proxy(record.get("answer", ""), contexts), 4),
            "answer_relevance_proxy": round(answer_relevance_proxy(record.get("question", ""), record.get("answer", "")), 4),
            "context_relevance_proxy": round(context_relevance_proxy(record.get("question", ""), contexts), 4),
            "is_trap": bool(record.get("is_trap", False)),
            "refused": bool(record.get("refused", False)),
        })
    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "RAGAS_LIKE_RESULTS.csv", index=False)
    summary = {
        "faithfulness_proxy_mean": df["faithfulness_proxy"].mean(),
        "answer_relevance_proxy_mean": df["answer_relevance_proxy"].mean(),
        "context_relevance_proxy_mean": df["context_relevance_proxy"].mean(),
        "trap_refusal_rate": df.loc[df["is_trap"], "refused"].mean() if df["is_trap"].any() else None,
    }
    lines = ["# Resumen RAGAS-like", "", "Yo reporto métricas locales inspiradas en RAGAS para asegurar ejecución sin intervención manual.", ""]
    for k, v in summary.items():
        lines.append(f"- **{k}:** {v:.4f}" if isinstance(v, float) else f"- **{k}:** {v}")
    (output_dir / "RAGAS_LIKE_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    return df
