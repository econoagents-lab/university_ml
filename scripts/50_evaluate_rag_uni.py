from pathlib import Path
import sys, json
sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.ragas_eval import evaluate_answers

if __name__ == "__main__":
    # Yo evalúo las respuestas con métricas locales inspiradas en RAGAS.
    records_path = Path("reports/uni_final/demo_records.json")
    if not records_path.exists():
        raise FileNotFoundError("Primero ejecuto scripts/49_run_rag_demo_questions.py")
    records = json.loads(records_path.read_text(encoding="utf-8"))
    df = evaluate_answers(records, output_dir="reports/uni_final")
    print(df[["faithfulness_proxy", "answer_relevance_proxy", "context_relevance_proxy", "is_trap", "refused"]].mean(numeric_only=True))
