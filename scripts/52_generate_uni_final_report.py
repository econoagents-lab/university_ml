from pathlib import Path
import pandas as pd

if __name__ == "__main__":
    # Yo genero un reporte técnico final para la exposición UNI.
    out_dir = Path("reports/uni_final")
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "RAGAS_LIKE_RESULTS.csv"
    if results_path.exists():
        df = pd.read_csv(results_path)
        faith = df["faithfulness_proxy"].mean()
        ans = df["answer_relevance_proxy"].mean()
        ctx = df["context_relevance_proxy"].mean()
        trap = df.loc[df["is_trap"], "refused"].mean() if df["is_trap"].any() else 0
    else:
        faith = ans = ctx = trap = 0
    report = f"""# Reporte técnico final UNI

## Sistema

Yo construí un asistente RAG económico-inmobiliario con corpus seguro, hipótesis económicas, table-to-text, guardrails, Text-to-SQL y evaluación RAGAS-like.

## Métricas

- Faithfulness proxy promedio: {faith:.3f}
- Answer relevance proxy promedio: {ans:.3f}
- Context relevance proxy promedio: {ctx:.3f}
- Tasa de rechazo en preguntas trampa: {trap:.3f}

## Técnicas avanzadas

1. Citación obligatoria.
2. Guardrails PII y prompt injection.
3. Multi-query expansion.
4. Re-ranking liviano.
5. Text-to-SQL controlado.

## Limitaciones

Yo uso métricas offline inspiradas en RAGAS para reproducibilidad. En producción académica con API disponible, puedo ejecutar la librería `ragas` oficial.
"""
    (out_dir / "FINAL_TECHNICAL_REPORT.md").write_text(report, encoding="utf-8")
    benchmark = """# Benchmark base vs avanzado

| Arquitectura | Citas | Guardrails | Multi-query | Reranking | Text-to-SQL | Comentario |
|---|---:|---:|---:|---:|---:|---|
| RAG base | No | No | No | No | No | Recupera texto, pero tiene mayor riesgo de contexto irrelevante. |
| RAG avanzado v1.1 | Sí | Sí | Sí | Sí | Sí | Recupera, protege, cita y consulta marts estructurados. |
"""
    (out_dir / "BENCHMARK_BASE_VS_ADVANCED.md").write_text(benchmark, encoding="utf-8")
    print("OK: reporte técnico final generado.")
