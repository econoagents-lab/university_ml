from pathlib import Path
import sys
import pandas as pd
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.pipeline import EconomicRagPipeline
from rag.text_to_sql import run_sql_question

if __name__ == "__main__":
    # Yo ejecuto preguntas de demostración para generar evidencia de funcionamiento.
    questions = pd.read_csv("evaluation/eval_questions.csv")
    pipeline = EconomicRagPipeline(corpus_dir="corpus", prefer_semantic_embeddings=False).build()
    out_dir = Path("reports/uni_final")
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Demo answers", ""]
    records = []
    for _, row in questions.iterrows():
        question = row["question"]
        answer = pipeline.ask(question)
        if row["question_type"] == "sql" and not answer.refused:
            sql_result = run_sql_question(question)
            answer.answer += "\n\nResultado Text-to-SQL controlado: " + str(sql_result["rows"])
        records.append({
            "id": row["id"],
            "question": question,
            "answer": answer.answer,
            "contexts": answer.contexts,
            "citations": answer.citations,
            "is_trap": row["question_type"] == "trap",
            "refused": answer.refused,
        })
        lines.append(f"## {row['id']} · {question}")
        lines.append("")
        lines.append(answer.answer)
        lines.append("")
        if answer.citations:
            lines.append("**Citas:**")
            for citation in answer.citations:
                lines.append(f"- {citation}")
        lines.append("")
    pd.DataFrame([{k:v for k,v in r.items() if k not in {"contexts","citations"}} for r in records]).to_csv(out_dir / "DEMO_ANSWERS.csv", index=False)
    (out_dir / "DEMO_ANSWERS.md").write_text("\n".join(lines), encoding="utf-8")
    import json
    (out_dir / "demo_records.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: respuestas demo generadas.")
